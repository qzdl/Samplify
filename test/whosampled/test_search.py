import unittest
import whosampled
import tools.direction

class Test_GetWhoSampledPlaylist(unittest.TestCase):
    """ Testing the main API for the WhoSampled scraper
    """

    direction_sample_of = [direction.contains_sample_of]
    source_common_communism = [{"track": "Communism", "artist": ["Common"]}]
    result_common_communism = [
        {'query': 'Communism', 'direction': 'Contains samples of ', 'type': 'Hook / Riff', 'genre': 'Jazz / Blues', 'title': 'The Surest Things Can Change', 'artist': ['Freddie Hubbard'], 'year': '1978'},
        {'query': 'Communism', 'direction': 'Contains samples of ', 'type': 'Drums', 'genre': 'Rock / Pop', 'title': "Knocking 'Round the Zoo (1971 Version)", 'artist': ['James Taylor and The Flying Machine'], 'year': '1971'},
        {'query': 'Communism', 'direction': 'Contains samples of ', 'type': 'Hook / Riff', 'genre': 'Jazz / Blues', 'title': 'Leaves', 'artist': ['Pete Jolly'], 'year': '1970'}
    ]

    source_common_resurrection = [
        {'artist': ['Common'], 'track': 'Resurrection'},
        {'artist': ['Common'], 'track': 'I Used to Love H.E.R.'},
        {'artist': ['Common'], 'track': 'Watermelon'},
        {'artist': ['Common'], 'track': 'Book Of Life'},
        {'artist': ['Common'], 'track': 'In My Own World (Check The Method)'},
        {'artist': ['Common'], 'track': 'Another Wasted Night With...'},
        {'artist': ['Common'], 'track': "Nuthin' To Do"},
        {'artist': ['Common'], 'track': 'Communism'},
        {'artist': ['Common'], 'track': 'WMOE'},
        {'artist': ['Common'], 'track': 'Thisisme'},
        {'artist': ['Common'], 'track': 'Orange Pineapple Juice'},
        {'artist': ['Common'], 'track': 'Chapter 13 (Rich Man vs. Poor Man)'},
        {'artist': ['Common'], 'track': 'Maintaining'},
        {'artist': ['Common'], 'track': 'Sum Shit I Wrote'},
        {'artist': ['Common'], 'track': "Pop's Rap"}
    ]
    result_common_resurrection =





    result = s.get_whosampled_playlist(
        [{"track": "Communism", "artist": ["Common"]}],
        direction=[direct.contains_sample_of]
    )

    def setUp(self):
        self.engine = whosampled.WhoSampled(debug=True)

    def test_single_sample_of(self):
        result = self.engine.get_whosampled_playlist(
            source_playlist=source_common_communism,
            direction=direction_sample_of
        )
        self.assertEqual(result, result_common_communism)

    def test_multiple_sample_of(self):
        result = self.engine.get_whosampled_playlist(
            source_playlist=source_common_resurrection,
            direction=direction_sample_of
        )
        self.assertEqual(result, result_common_resurrection)
