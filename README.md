# Spotify Sample Playlist

## Usage
This is a short program that, given a Spotify playlist, creates a new playlist containing all the samples in that playlist.
When the sample_finder file is run, the user is prompted to input the Spotify playlist uri, which can be found in the playlist details. The user then inputs the desired name for their new sample playlist, and within seconds, the sample playlist is created. This was created for my personal use, to find new music sampled in some of my favorite songs.

## Program Overview
Playlists are read from Spotify through the Spotify API using Spotipy. Song names and artists are stored and then located on Whosampled.com. Whosampled.com is a fantastic service where users report samples in music which are verified by other users. A request is sent to the site searching for the song name, selecting a result with the matching artist name and storing the link to that song's page. A second request is sent to that song page, and BeautifulSoup is used to scrape HTML for sample names, which are also stored. Next, the samples are located using Spotipy, if they exist. Finally, a new playlist is created for the user, containing all the samples available on Spotify.

## Future Development
The next steps in this project will be to implement a recommendation system for myself, which will add new music to my library based on the samples contained in my favorite songs. This is also an excuse for me to try out different machine learning techniques to achieve this goal. 

## Contact
For any questions/suggestions, I may be reached at chris.m.pease@gmail.com
