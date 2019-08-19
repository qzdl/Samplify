import requests
from bs4 import BeautifulSoup

class Scraper:
    def __init__(self, debug=False):
        # create a session to manage lifetime of self.requests and skip auto-reject from
        # whosampled; seems pretty unfriendly to block self.request's default headers.
        self.req = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=10)
        self.req.mount('https://', adapter)
        self.req.mount('http://', adapter)
        self.req.headers = {
            "User-Agent":
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
        }

    def get_whosampled_playlist(self, loaded_playlist):
        """Main endpoint for Scraper
        loaded_playlist:
        - type is <list: dict>
        - [{"track": "School Boy Crush", "artist": "Average White Band"}, ...]
             - Gets link for each song in `loaded_playlist`
             - scrapes corresponding detail page for song
             - parses detail from scrape
        """
        samples = []
        new_playlist = []
        print('SPOTIFY PLAYLIST DISCOVERED: \n')
        for i in loaded_playlist:
            print(i['track'] + ' by ' + i['artist'][0])
            samples, sampled_by = self.getme_thesamples(i['track'], i['artist'][0])
            if samples:
                new_playlist.append(samples)
        lst = [i for j in new_playlist for i in j] # what the fuck
        return lst

    def getme_thesamples(self, song_title, artist_name):
        """Retrieves sample detail for individual song"""
        print(f'getme_thesamples: {song_title}: {artist_name}')
        link = self.retrieve_song_link(song_title, artist_name)
        if not link:
            return None, None
        samples, sampled_by = self.retrieve_samples_v2(song_title, link)
        return samples, sampled_by

    def retrieve_song_link(self, song_title, artist_name=None):
        """queries for song, returns relevant links
           FIXME refinements to how strict this is
             - aka make it find tighter matches at the search level
             - degree of strictness? could be quantified w/ fuzzy match
        """

        query = song_title.replace(' ', '%20')
        if artist_name:
            query = f'{query}%20{artist_name.replace(" ", "%20")}'
        url = f'https://www.whosampled.com/search/tracks/?q={query}'
        r = self.req.get(url)
        content = r.content
        search_page_soup = BeautifulSoup(content, 'html.parser')
        search_results = search_page_soup.findAll(
            'li', attrs={'class': "listEntry"})

        if not search_results:
            return None

        # FIXME: don't just return the first link
        link = [i.a for i in search_results][0].get('href')
        return link

    def retrieve_samples_v2(self, song_title, link):
        """Gets sample details from link

        link (str):
          e.g '/Kenny-Burrell/Midnight-Blue/'
        """
        s = self.req.get(f'https://www.whosampled.com{link}')
        page_detail = s.content
        soup = BeautifulSoup(page_detail, 'html.parser')
        listed = [i.text for i in soup.findAll('div', attrs={'class': 'list bordered-list'})]

        from time import time
        file_name = f'{time()}.{song_title}.html'
        with open(file_name, 'w+') as f:
            print(f'stream open for {file_name}')
            f.write('<!-- SAMPLE PAGE CONTENT -->\n')
            f.write(str(soup))
            f.write(str(listed))

        if not listed:
            print('retrieve_samples_v2: not listed')
            return [], []
        samples = self.parse_sample_items(song_title=song_title,
                                          sample_data=listed[0])
        if not len(listed) > 2:
            print('retrieve_samples_v2: not len(listed) > 2')
            return samples, []
        sampled_by = self.parse_sample_items(song_title=song_title,
                                              sample_data=listed[1])

        print('retrieve_samples_v2: len(listed) > 2')
        return samples, sampled_by

    def parse_sample_items(self, song_title, sample_data):
        """Gets detail from """
        raw_samples =  [i.split('\n') for i in list(filter(None, sample_data.split('\t')))][:-1]
        parsed_samples = []

        for sample in raw_samples:
            # FIXME: maybe `if '(' in sample[-2]`
            year = sample[-2].replace('by ', '').split(' (')[1].replace(')', '')
            artist = sample[-2].replace('by ', '').split(' (')[0]
            parsed_samples.append({
                'query': song_title,
                'type': sample[-7],
                'genre': sample[-6],
                'title': sample[-3],
                'artist':  artist,
                'year': year
            })
        print(f'parse_sample_items: {parsed_samples}')
        return parsed_samples
