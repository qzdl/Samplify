# Spotify Sample Playlist


## Getting Started
Setup TLDR; `git clone https://github.com/cpease00/spotify-samples.git && cd spotify-samples && conda env create -f environment.yml`

- Ensure some form of [conda](https://https://docs.conda.io/en/latest/miniconda.html) is installed.
- Clone this repo with `git clone https://github.com/cpease00/spotify-samples.git`
- `cd` to the new directory, and create a new virtual environment with
  `conda env create -f environment.yml`
  * Refer to [`environment.yml`](./environment.yml) for a list of packages

### Spotify API Access; config.py
If you haven't used the spotify API before:
- Head to the [developer dashboard](https://developer.spotify.com/dashboard/) and register a new application
- Setup a redirect as `http://localhost:<SOME_FREE_PORT>`
  * This can be found in the information page of a registered application > edit settings.
- Create `config.py` at the root of the repository, and populate it as follows:
(NOTE: these are not valid credentials )
```
# ClientID from registered application at:
https://developers.spotify.com/dashboard/applications
client = '7bf224e8jn954215s3g11degh599e3an'

# Client Secret can be found below 'SHOW CLIENT SECRET' once you are on the info
# page of a registered application
secret = '7bf224e8jn954215s3g11degh599e3an'

# The easiest way I've found to get this is to hit the /v1/me endpoint:
# https://developer.spotify.com/console/get-current-user/
# find the "uri" property, e.g. "uri": "spotify:user:1134745600"
username = '1134745600'

# setup this redirect on a registered application. make sure it
# is identical to the letter or you'll get "INVALID REDIRECT"

redirect = 'http://localhost:8889'
```

## Usage
This is a short program that, given a Spotify playlist, creates a new playlist
containing all the samples in that playlist. When the sample_finder file is run,
the user is prompted to input the Spotify playlist uri, which can be found in
the playlist details. The user then inputs the desired name for their new sample
playlist, and within seconds, the sample playlist is created. This was created
for my personal use, to find new music sampled in some of my favorite songs.

### Example Use (from stout)
TODO


## Program Overview
Playlists are read from Spotify through the Spotify API using Spotipy.
Song names and artists are stored and then located on `Whosampled.com`.
`Whosampled.com` is a fantastic service where users report samples in music
which are verified by other users. A request is sent to the site searching for
the song name, selecting a result with the matching artist name and storing the
link to that song's page. A second request is sent to that song page, and
BeautifulSoup is used to scrape HTML for sample names, which are also stored.
Next, the samples are located using Spotipy, if they exist. Finally, a new
playlist is created for the user, containing all the samples available on Spotify.

## Future Development: Notes from cpease00
The next steps in this project will be to implement a recommendation system,
which will add new music to the library based on the samples contained in my favorite songs.
This is also an excuse for me to try out different machine learning techniques to achieve this goal.

## Contact
For any questions/suggestions, please email [chris.m.pease@gmail.com](mailto:chris.m.pease@gmail.com)
