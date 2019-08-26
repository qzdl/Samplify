import requests
from bs4 import BeautifulSoup
if __name__ == '__main__':
    import direction as direct
    import logger
else:
    from . import direction as direct
    from . import logger

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
        self.logger = logger.Logger(verbosity)
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
            samples = samples + self.get_samples(track['track'], track['artist'][0])
        if not samples:
            self.log(message='No samples found',
                     function='get_whosampled_playlist')
            return None

        # get the track lists from samples => get the tracks from the track list
        # output is <list: dict>, where dict = sample detail
        lst = [track for tracks in samples for track in tracks]
        self.logger.write_log('scraper_trace')
        return lst

    def get_samples(self, song_title, artist_name):
        """ Retrieves sample detail for individual song """
        link = self.search(song_title, artist_name)
        if not link:
            return []
        sample_data = self.get_sample_details(song_title, link)
        return sample_data or []

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

    def get_sample_details(self, song_title, link):
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
        url = f'{self.base_url}{link}'
        s = self.req.get(url)   # get summary page
        page_detail = s.content

        self.log(message=f'Getting summary page: {url}',
                 function='get_sample_details',
                 data=page_detail)

        # get section headers (correspond to `direction`)
        match = []
        soup = BeautifulSoup(page_detail, 'html.parser')
        headings = soup.findAll('header', attrs={'class': 'sectionHeader'})
        for header in headings:
            for direction in self.directions:
                if direction not in header.span.text:
                    continue

                direction_data = header.find_next_sibling(
                        'div', attrs={'class': 'list bordered-list'}).text
                match.append(self.parse_sample_items(
                    song_title=song_title,
                    sample_data=direction_data,
                    link=link,
                    direction=direction
                ))
        return match

    def get_direction_content(self, url, song_title, direction, recursing=False):
        s = self.req.get(url)
        page_detail = s.content
        soup = BeautifulSoup(page_detail, 'html.parser')
        # check if base paged content is 404
        if 'The page you requested cannot be found' in str(soup):
            return None, []

        listed = [i.text for i in soup.findAll('div', attrs={'class': 'list bordered-list'})]
        return soup, self.parse_sample_items(song_title=song_title,
                                             sample_data=listed[0],
                                             direction=direction,
                                             link=None,
                                             recursing=recursing)

    def parse_sample_items(self, song_title, sample_data,
                           direction, link, recursing=False):
        """ Gets detail from track listing
        description:
          Parses text from
        Returns:
          <list: dict> detail of
        """
        raw_samples =  [i.split('\n') for i in list(filter(None, sample_data.split('\t')))][:-1]
        parsed_samples = []
        if len(raw_samples) >= 5 and not recursing:
            parsed_sampled = \
                parsed_samples + self.scrape_paged_content(song_title, direction, link)

        for sample in raw_samples:
            interim = sample[-2].replace('by ', '', 1).split(' (')
            year = interim[1].replace(')', '')
            artist = interim[0]
            parsed_samples.append({
                'query': song_title,
                'direction': direction,
                'type': sample[-7],
                'genre': sample[-6],
                'title': sample[-3],
                'artist':  artist,
                'year': year
            })
        self.log(message=f'Getting sample data for {song_title}, len=={len(parsed_samples)}',
                 function='parse_sample_items',
                 data=parsed_samples)
        return parsed_samples

    def scrape_paged_content(self, song_title, direction, link):
        """Heads to scaped"""
        paged_url = f'{self.base_url}{link}{direct.get_paged_content_by_direction(direction=direction)}/'
        soup, samples = self.get_direction_content(
            url=paged_url, song_title=song_title, direction=direction, recursing=True)

        if not soup:
            return samples
        pagination = soup.findAll(
            'div', attrs={'class': "pagination"})
        if not len(pagination) > 0:
            return samples

        # get max page number
        page_link_cont = pagination[0].find_all('span')
        page_links = [item.a.get('href') for item in page_link_cont if item.a is not None]
        last_link_num = int(page_links[-1].split('=')[1]) # maybe 'next'
        potential_max_link_num = int(page_links[-2].split('=')[1]) # maybe max page value

        tracks = []
        for page_number in range(1, max(last_link_num, potential_max_link_num)+1):
            url = f'{paged_url}?cp={page_number}'
            soup, parsed = self.get_direction_content(
                url=url, song_title=song_title, direction=direction, recursing=True)
            tracks = tracks + parsed
        return tracks

    def log(self, **kwargs):
        self.logger.log(**kwargs)


if __name__ == '__main__':
    s = Scraper([direct.contains_sample_of, direct.was_sampled_in], debug=True)

    result = s.get_whosampled_playlist(
        [{"track": "Communism", "artist": ["Common"]}],
        direction=[direct.contains_sample_of]
    )

    # result = s.get_whosampled_playlist(
    #     [{"track": "School Boy Crush", "artist": ["Average White Band"]}],
    #     direction=[direct.contains_sample_of]
    # )

    print(result)
