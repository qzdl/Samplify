import requests
from time import time
from bs4 import BeautifulSoup
import samplify.tools.direction as direct
import samplify.tools.logger as logger

class Scraper:
    """ A scraper for whosampled
    Description:
      -

    Parameters:
      debug:
        - Prints detail of each step
    """
    def __init__(self, verbosity=0):
        # create a session to manage lifetime of self.requests and skip auto-reject from
        # whosampled; seems pretty unfriendly to block self.request's default headers.
        self.verbosity = verbosity
        self.logger = logger.Logger(verbosity, f'scraper_track.{time()}')
        self.directions = None
        self.base_url = 'https://whosampled.com'
        self.req = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=10)
        self.req.mount('https://', adapter)
        self.req.mount('http://', adapter)
        self.req.headers = {
            "User-Agent":
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
        }

    def get_whosampled_playlist(self, source_playlist, direction):
        """ Finds detail relevant to direction from songs related to a source playlist

        Parameters:
          source_playlist: <list: dict>
            - e.g. [{"track": "School Boy Crush", "artist": ["Average White Band"]}]
            - Gets link for each song in `source_playlist`
            - scrapes corresponding detail page for song
            - parses detail from scrape

          direction: <list: str>
            - e.g. [direct.contains_sample_of]
            - items defined in ./direction.py
            - collect *only* samples relevant to direction

        Returns:
          <list: dict> of sample detail
        """
        samples = []
        self.directions = direction
        self.log(message='Scraping for source_playlist',
                 function='get_whosampled_playlist',
                 data=source_playlist)

        for track in source_playlist:
            samples = self.get_samples(track['track'], track['artist'][0])
            track['samples'] = samples
            if not samples:
                self.log(message='No samples found',
                         function='get_whosampled_playlist')

        return source_playlist

    def get_samples(self, song_title, artist_name):
        """ Retrieves sample detail for individual song """
        link = self.search(song_title, artist_name)
        if not link:
            return {}
        sample_data = self.get_sample_details(link)
        return sample_data or {}

    def search(self, song_title, artist_name):
        """ Queries whosampled.com for song, returns relevant links
        Description:
        - Builds query string with `song_title` and `artist_name`
        - whosampled is doing the heavy lifting for 'relevance',
          as only the top result for a given query is taken
        Parameters:
          song_title:
          - <str> song title, e.g 'Teenage Love'
          artist_name:
          - <str> artist name, e.g 'Slick Rick'
        """

        query = song_title.replace(' ', '%20')
        if artist_name:
            query = f'{query}%20{artist_name.replace(" ", "%20")}'
        url = f'https://www.whosampled.com/search/tracks/?q={query}'
        r = self.req.get(url)
        search_page_soup = BeautifulSoup(r.content, 'html.parser')
        search_results = search_page_soup.findAll(
            'li', attrs={'class': "listEntry"})

        if not search_results:
            return None

        # return first result
        link = [i.a for i in search_results][0].get('href')
        return link

    def get_sample_details(self, link):
        """ Gets sample details from top-level link

        link (str):
          e.g '/Kenny-Burrell/Midnight-Blue/'

        - 'sampled' -> Was sampled in
        - 'samples' -> Contains samples of

            - relevant pages only exist when # references > 5
            - paging query string can be '?sp=N' or '?cp=N'
            valid pages are:
            - 'sampled' -> Was sampled in
            - 'samples' -> Contains samples of
            - e.g. https://www.whosampled.com/Nas/Halftime/sampled?sp=1
            worth trying next page until 404 is hit as a quick & dirty
            - 'The page you requested cannot be found' (UK-ENG)

          - e.g only parse items in 'Sampled By'
        """
        matches = {}
        url = f'{self.base_url}{link}'
        soup = None
        headings = None

        for direction in self.directions:
            soup, headings, matches[direction] = self.get_direction_content(
                direction=direction,
                link=link,
                soup=soup,
                headings=headings

            )
        return matches

    def get_direction_content(self, direction, link, headings=None,
                              soup=None, recursing_page=False):
        """ Gets detail page, and parses out sample data in the corresponding direction
            - reused within recursive portions in child functions

            Parameters:
            - direction: from tools.direction
              + e.g. direction.contains_sample_of

            - link:      top-level identifier for a track page
              + e.g '/Nas/Halftime'

            - heading: the direction heading before a section of content
              + if this is not null, `heading.find_next_sibling` will return the
                sample grid

            - soup: the currently working doc soup - skips a request if not null

            - recursing_page: safety against infinite loops when called from children
        """
        samples = []
        if not soup:
            url = f'{self.base_url}{link}'
            page_detail = self.req.get(url).content
            soup = BeautifulSoup(page_detail, 'html.parser')
            self.log(message=f'Getting page: {url}',
                     function='get_direction_content',
                     data=page_detail)

        # check if base paged content is 404
        if 'The page you requested cannot be found' in str(soup):
            self.log(message='404 page hit at {url}')
            return None, []

        # get section headers (correspond to `direction`)
        if not headings:
            headings = soup.findAll('header', attrs={'class': 'sectionHeader'})
        direction_container = [
            heading.find_next_sibling('div', attrs={'class': 'list bordered-list'})
            for heading in headings if direction in heading.span.text
        ]

        # container should exist & be unique
        if direction_container and len(direction_container) == 1:
            samples = self.parse_sample_items(
                sample_data=direction_container[0],
                direction=direction,
                link=link,
                recursing_page=recursing_page
            )
        return soup, headings, samples

    def parse_sample_items(self, sample_data, direction, link, recursing_page=False):
        """ Gets detail from track listing
        description:
          Parses text from
        Returns:
          <list: dict> detail of
        """
        # split entries by newlines, and properties within entries by tabs
        parsed_samples = []
        raw_samples = sample_data.findAll('div', attrs={'class': 'sampleEntry'})

        if len(raw_samples) >= 5 and not recursing_page:
            parsed_samples = self.scrape_paged_content(direction, link)
        else:
            find_class = lambda s,e,c: s.find(e, attrs={'class': c})
            for sample in raw_samples:
                track_artist = find_class(sample, 'span','trackArtist')
                track_name = find_class(sample, 'a', 'trackName')
                track_badge = find_class(sample, 'div', 'trackBadge')
                track_type = find_class(track_badge, 'span', 'topItem')
                track_genre = find_class(track_badge, 'span', 'bottomItem')
                breakdown_ref = track_name.get('href')
                print(breakdown_ref)
                ids = self.get_videos_from_breakdown(breakdown_ref)
                yt_originator, yt_sample = direct.get_originator_from_direction(direction, ids)
                parsed_samples.append({
                    'type': track_type.text if track_type else '',
                    'genre': track_genre.text if track_genre else '',
                    'title': track_name.text,
                    'artist': [a.text for a in track_artist.find_all('a')],
                    'year': track_artist.text[-9:-5],
                    'yt_breakdown': track_name.get('href'),
                    'yt_originator': yt_originator,
                    'yt_sample': yt_sample
                })
        self.log(message=f'Parsing sample data from {link}',
                 function='parse_sample_items',
                 data=parsed_samples)
        return parsed_samples

    def scrape_paged_content(self, direction, link):
        """ Accesses top-level paged content where n:samples > 5
            - handles pagination dynamically
            - from landing on top-level page to last page
            - calls out to `parse_sample_items` for individual rows
        """
        paged_link= f'{link}{direct.get_paged_content_by_direction(direction=direction)}/'
        soup, _, samples = self.get_direction_content(
            direction=direction,
            link=paged_link,
            headings=None,
            soup=None,
            recursing_page=True
        )
        if not soup:
            return samples

        pagination = soup.findAll(
            'div', attrs={'class': "pagination"})
        if not len(pagination) > 0:
            return samples

        # get max page number
        page_link_cont = pagination[0].find_all('span')
        page_links = [item.a.get('href') for item in page_link_cont if item.a is not None]
        last_link_num = int(page_links[-1].split('=')[1])          # maybe 'next'
        potential_max_link_num = int(page_links[-2].split('=')[1]) # maybe max page value

        for page_number in range(2, max(last_link_num, potential_max_link_num)+1):
            number_link = f'{paged_link}?cp={page_number}'
            self.log(message=f'Getting paged content for {number_link}')
            soup, _, paged_samples = self.get_direction_content(
                direction=direction,
                link=number_link,
                soup=None,
                headings=None,
                recursing_page=True
            )
            samples = (samples or []) + paged_samples

        self.log(message='ending paging recursion', data=samples)
        return samples


    def get_videos_from_breakdown(self, link):
        url = self.base_url + link
        breakdown = BeautifulSoup(self.req.get(url).content, 'html.parser')
        print(url)
        ids = [
            div.iframe.get('id') if div.iframe else None for div in
            breakdown.find_all('div', attrs={'class': 'sample-embed'})
        ]

        return ids # subject is normalised above as (originator, sample)

    def log(self, **kwargs):
        self.logger.log(**kwargs)


if __name__ == '__main__':
    import json
    s = Scraper(3)

    result = s.get_whosampled_playlist(
        [{"track": "halftime", "artist": ["nas"]}],
        direction=direct.all_directions
    )
    print(json.dumps(result, indent=2))
    print(json.dumps(result[0]['samples'][direct.was_sampled_in], indent=2))
    print(len(result[0]['samples'][direct.was_sampled_in]))

    # result = s.get_whosampled_playlist(
    #     [{"track": "Communism", "artist": ["Common"]}],
    #     direction=direct.all_directions
    # )
    # print(json.dumps(result, indent=2))


    # result = s.get_whosampled_playlist(
    #     [{"track": "School Boy Crush", "artist": ["Average White Band"]}],
    #     direction=[direct.was_sampled_in, direct.contains_sample_of, direct.was_
    # )
    # print(json.dumps(result, indent=2))
