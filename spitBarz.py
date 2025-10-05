import re
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
from rich.console import Console
from rich import print
from rich.text import Text
from rich.align import Align
from rich.panel import Panel
from rich.console import Group
import os
from dotenv import load_dotenv

load_dotenv()

clientID = os.getenv('SPOTIFY_CLIENT_ID')
clientSecret= os.getenv('SPOTIFY_CLIENT_SECRET')
# client ID: 6a7538f8d2134044aecd841639f228b2
# client password: ac37914664a043cd8e4663d27355cbfa

timeStampPattern = r"\[(\d{1,2})\:(\d{2})\.?(\d{0,2})\]"
SYNCOFFSET = 0 

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-read-playback-state"))
    
current = sp.current_playback()


url = "https://lrclib.net/api/get"

def parse_lyric_content(lrcText):
    lines = lrcText.split('\n')
    timeLyrics = []
    for line in lines:
        line = line.strip()
        
        # check if line has timestamp

        match = re.search(timeStampPattern, line)

        if match:
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            hundreds = int(match.group(3)) if match.group(3) else 0

            progress = (minutes * 60 * 1000) + (seconds * 1000) + (hundreds * 10) + SYNCOFFSET # save timestamp in ms

            closingBracketIndex = line.find(']')
            if closingBracketIndex != -1:
                lyric = line[closingBracketIndex + 1:]
            
            timeLyrics.append((progress, lyric))
    
    return timeLyrics


def fetch_lyrics(trackName, artistName, albumName=None, duration=None):
    params={
        'track_name' : trackName,
        'artist_name' : artistName,
        'album_name' : albumName,
        'duration' : duration}

    response = requests.get(url, params=params)
    print(response)
    data = response.json()

    print(data)
    if 'syncedLyrics' in data and data['syncedLyrics']:
        return parse_lyric_content(data['syncedLyrics'])

    elif 'plainLyrics' in data and data['plainLyrics']:
        return [(0, data['plainLyrics'])]

    else:
        print("no ylrics founrd")
        return []

def get_current_playback_info():
    return sp.current_playback()


def get_current_lyric(progress, timeLyrics):

    if not timeLyrics:
            return[]

    currentIndex =None

    for i, (timestamp, lyric) in enumerate(timeLyrics):

        if progress >= timestamp:
            currentIndex = i
        
        else:
            break
    
    
    if currentIndex is None:
        currentIndex = 0
    
    lyrics = []


    if currentIndex > 0:
        pastText = Text(f"{timeLyrics[currentIndex - 1][1]}")
        pastText.stylize("red")
        lyrics.append(pastText)
    
    currentText=(Text(f"🎤 {timeLyrics[currentIndex][1]} 🎤"))
    currentText.stylize("bold green")
    lyrics.append(currentText)

    if currentIndex < len(timeLyrics) - 1:
        futureText= (Text(f"{timeLyrics[currentIndex+1][1]}"))
        futureText.stylize("red")
        lyrics.append(futureText)
    
    return lyrics


console = Console()

def main():
    currentTrack = None
    currentLyric = []
    trackName = ""
    artistName = ""

    try:
        while True:
            lastLyric = ""
            current = get_current_playback_info()

            if current and current['is_playing']:
                trackID = current['item']['id']
                progress = current['progress_ms']

                if trackID != currentTrack:
                    currentTrack = trackID
                    
                    trackName = current['item']['name']
                    artistName = current['item']['artists'][0]['name']
                    albumName = current['item']['album']['name']
                    print(albumName)
                    duration = current['item']['duration_ms'] * 0.001
                    print(duration)

                    songLyrics = fetch_lyrics(trackName, artistName, albumName, duration)
                    
                currentLyric = get_current_lyric(progress,songLyrics)

                if currentLyric != lastLyric:
                    #print("\033[H\033[J]]") # clears terminal
                    console.clear()
                    lastLyric = currentLyric

                
                titleText = Text(f"Now playing: {trackName} by {artistName}\n")
                titleText.stylize("bold underline #2A1E5C")


                content = Group(titleText, *[lyric for lyric in currentLyric])
                
                daBox = Panel(content)
                console.print(Align.center(daBox))

            else:
                print("Nothing playing")
            
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("stop da moosic")



if __name__ == "__main__":
    main()

