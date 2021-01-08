"""
This is a little project for me to learn Python
This was inspired by: The Come Up -> https://www.youtube.com/watch?v=7J_qcttfnJA
I've changed bits and pieces to double check my understanding of how Python works

*** STEPS ***
Step 1: YouTube login
Step 2: Find liked videos
Step 3: Create new Spotify playlist
Step 4: Search for songs
Step 5: Add songs to playlist
"""
import json
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import youtube_dl
import datetime
import csv
import PySimpleGUI as sg
import webbrowser

import requests
from secrets import spotify_user_id, spotify_token

from countries import load_countryList

class CopiaLaYoutuber:

    def __init__(self):
        self.user_id = spotify_user_id
        self.spotify_token = spotify_token
        self.youtube_client = self.get_youtube_client()
        self.all_song_info = {}  # Create dictionary of songs
        self.all_playlists = {}  # Create dictionary of YouTube playlists

# *********************************************************************************************************************
# YOUTUBE CLIENT CONNECTION

    # Step 1: YouTube login
    def get_youtube_client(self):
        # Log Into Youtube, Copied from Youtube Data API
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "client_id.json"

        # Get credentials and create an API client
        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()

        # from the Youtube DATA API
        youtube_client = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

        return youtube_client


# *********************************************************************************************************************
# CREATE ITEMS LIST FROM SOURCE

    # Step 2: Find videos (multiple options) & create dictionary of songs
    def get_myPlaylists(self):
        request = self.youtube_client.playlists().list(
            part="snippet,contentDetails",
            ########## YouTube ChannelID goes here
            channelId="______",
            # How to: go to youtube.com, login, go to your channel (you must have a channel to create playlists)
            # Your channel id is the code at the end of the your channel page URL
            # e.g.https://www.youtube.com/channel/UTOE4fY77RekAYMmCgJJjjjj  ---> channel id = UTOE4fY77RekAYMmCgJJjjjj
            maxResults=25
        )
        response = request.execute()
        self.salva_json(response, "MyPlaylists")
        myPlaylists = []
        for item in response["items"]:
            title = item["snippet"]["title"]
            myPlaylists.append(title)
            self.all_playlists[title] = {
                "playlist_title": title,
                "id": item["id"],
                "published_at": item["snippet"]["publishedAt"],
                "channelId": item["snippet"]["channelId"]
            }
        return myPlaylists

    def get_video_in_myPlaylist(self,playlistId,playlistTitle):
        try:
            request = self.youtube_client.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=playlistId,
            )
            response = request.execute()
            self.salva_json(response, playlistTitle+"-Playlist content")
            self.save_and_collect(response, 2)
        except Exception as ex:
            print(ex)

    def get_videos_myLikedVideos(self):
        try:
            request = self.youtube_client.videos().list(
                part="snippet,contentDetails,statistics",
                myRating="like"
            )
            response = request.execute()
            self.salva_json(response, "MyLikedVideos")
            self.save_and_collect(response, 1)
        except Exception as ex:
            print(ex)

    def get_videos_popular(self, country_iso):
        try:
            request = self.youtube_client.videos().list(
                part="snippet,contentDetails,statistics",
                chart="mostPopular",
                regionCode=country_iso,
                maxResults=50,
                videoCategoryId=10
            )
            response = request.execute()
            self.salva_json(response, "Popular"+country_iso)
            self.save_and_collect(response, 1)
        except Exception as ex:
            print(ex)

    def get_watch_history(self, filepath):
        try:
            with open(filepath, encoding="utf8") as f:
                response = json.load(f)
                self.save_and_collect_history(response)
        except Exception as ex:
            print(ex)

# *********************************************************************************************************************
# SAVE AND COLLECT

    def save_and_collect(self, response, type):
        # set csv headers
        csv_field_names = ["video_title", "youtube_url", "song_name", "artist", "spotify_uri"]

        # collect video and get info
        for item in response["items"]:
            # get song name and artist name from youtube dl, in case of error print and
            video_title = item["snippet"]["title"]
            if type == 1:
                youtube_url = "https://www.youtube.com/watch?v={id_youtube}".format(id_youtube=item["id"])
            elif type == 2:
                youtube_url = "https://www.youtube.com/watch?v={id_youtube}".format(
                    id_youtube=item["snippet"]["resourceId"]["videoId"]
                    )
            else:
                print("Fatal error")
                break

            try:
                video = youtube_dl.YoutubeDL({}).extract_info(youtube_url, download=False)
                song_name = video["track"]
                artist = video["artist"]
                print(video_title,youtube_url,song_name,artist)
                # save info in a list of Dictionaries of song info
                self.all_song_info[youtube_url] = {
                    "video_title": video_title,
                    "youtube_url": youtube_url,
                    "song_name": song_name,
                    "artist": artist,
                    "spotify_uri": self.get_spotify_uri(song_name, artist)
                }
            except Exception as ex:
                print(ex)
        print(self.all_song_info)
        self.salva_lists(self.all_song_info, csv_field_names, "SongsFound")

    def save_and_collect_history(self, response):
        # set csv headers
        csv_field_names = ["video_title", "youtube_url", "song_name", "artist", "spotify_uri"]

        # collect video and get info
        for item in response:
            video_title = item["title"]
            youtube_url = item["titleUrl"]

            try:
                video = youtube_dl.YoutubeDL({}).extract_info(youtube_url, download=False)
                song_name = video["track"]
                artist = video["artist"]
                print(video_title, youtube_url, song_name, artist)
                # save info in a list of Dictionaries of song info
                self.all_song_info[youtube_url] = {
                    "video_title": video_title,
                    "youtube_url": youtube_url,
                    "song_name": song_name,
                    "artist": artist,
                    "spotify_uri": self.get_spotify_uri(song_name, artist)
                }
            except Exception as ex:
                print(ex)
        print(self.all_song_info)
        self.salva_lists(self.all_song_info, csv_field_names, "SongsFound")


# *********************************************************************************************************************
# SPOTIFY

    # Step 3: Create new Spotify playlist
    def create_spotify_playlist(self, playlist_name_input, playlistDescription):
        datetime_now = datetime.datetime.now()
        datetime_now_usable = datetime_now.strftime("%Y%m%d-%H%M%S")

        playlist_name = playlist_name_input
        playlist_descr = playlistDescription + ". Playlist created using Python on " + datetime_now_usable
        query = "https://api.spotify.com/v1/users/{phold}/playlists".format(phold=self.user_id)
        request_body = json.dumps({
            "name": playlist_name,
            "description": playlist_descr,
            "public": False
        })

        response = requests.post(
            query,
            data=request_body,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {chiave}".format(chiave=self.spotify_token)
            }
        )

        response_json = response.json()
        print(playlist_name+" created, id = "+response_json["id"])
        # Playlist ID
        return response_json["id"]

    # Step 4: Search for songs
    def get_spotify_uri(self, song_name, artist):
        if song_name is None and artist is None:
            # print("Song not found")
            return "NotFound"
        else:
            query = "https://api.spotify.com/v1/search?query={}%20{}&type=track&offset=0&limit=20".format(
                artist,
                song_name
            )
            query=query.replace(" ", '%20')
            response = requests.get(
                query,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {chiave}".format(chiave=spotify_token)
                }
            )
            response_json = response.json()
            # self.salva_json(response_json, "SongResponse")

            songs = response_json["tracks"]["items"]
            if not songs:
                return
            else:
                uri_song = songs[0]["uri"]
                return uri_song


# *********************************************************************************************************************
# RUN

    def apri_finestra(self):
        buttons = {'_button1_': 'YouTube popular videos',
                   '_button2_': 'One of my YouTube playlists',
                   '_button3_': 'My YouTube liked videos',
                   '_button4_': 'My YouTube watch history'
                   }

        sg.theme('DefaultNoMoreNagging')
        layout = [[sg.Text("Choose what you would like to import to Spotify", key='_header_')],
                  [sg.Button(buttons['_button1_'], size=(32,3), key='_button1_')],
                  [sg.Button(buttons['_button2_'], size=(32,3), key='_button2_')],
                  [sg.Button(buttons['_button3_'], size=(32,3), key='_button3_')],
                  [sg.Button(buttons['_button4_'], size=(32,3), key='_button4_')],
                  [sg.Text(' ', size=(1,1))],
                  [sg.Button("QUIT")]
                  ]
        # Create the Window
        window = sg.Window('YouTube to Spotify import', layout)
        # Event Loop to process "events"
        while True:
            event, value = window.read()
            if event in (None, 'QUIT'):
                break
            window.FindElement('_header_').update('loading ...')
            window.FindElement('_button1_').update(visible=False)
            window.FindElement('_button2_').update(visible=False)
            window.FindElement('_button3_').update(visible=False)
            window.FindElement('_button4_').update(visible=False)
            window.FindElement('QUIT').update(disabled=True)
            window.Refresh()
            scelta = buttons[event]
            self.selezione(scelta, window)

    def selezione (self, event, window):
        print(event)
        if event == "YouTube popular videos":
            countries = load_countryList(self)
            print('Country list import completed')
            window.close()
            layout = [[sg.Text("Choose country", key="feedback")],
                      [sg.Combo(countries, size=(32, 20), enable_events=True, key='combo')],
                      [sg.Button("SUBMIT", size=(29, 2))],
                      [sg.Button("QUIT")]
                      ]
            # Create the Window
            window2 = sg.Window(event, layout)
            # Event Loop to process "events"
            while True:
                event, values = window2.read()
                if event in (None, sg.WINDOW_CLOSED,  'QUIT'):
                    break
                if event == "SUBMIT":
                    combo = values['combo']
                    country = combo[1]
                    window2.close()
                    print(country)
                    SpotifyTag = 'YouTube popular in ' + country
            self.get_videos_popular(country)

        if event == "One of my YouTube playlists":
            playlists = self.get_myPlaylists()
            print('My YouTube playlist names imported')
            window.close()
            layout = [[sg.Text("Choose playlist", key="feedback")],
                      [sg.Combo(playlists, size=(32, 20), enable_events=True, key='combo')],
                      [sg.Button("SUBMIT", size=(29, 2))],
                      [sg.Button("QUIT")]
                      ]
            # Create the Window
            window2 = sg.Window(event, layout)
            # Event Loop to process "events"
            while True:
                event, values = window2.read()
                if event in (None, sg.WINDOW_CLOSED, 'QUIT'):
                    break
                if event == "SUBMIT":
                    playlistTitle = values['combo']
                    playlistId = self.all_playlists[playlistTitle]["id"]
                    window2.close()
                    SpotifyTag = 'My YouTube playlist: ' + playlistTitle
            self.get_video_in_myPlaylist(playlistId,playlistTitle)

        if event == "My YouTube liked videos":
            window.close()
            self.get_videos_myLikedVideos()
            SpotifyTag = 'My YouTube liked videos'

        if event == "My YouTube watch history":
            window.close()
            layout = [[sg.Text("You must download your YouTube history as a json file and upload it here.")],
                      [sg.Text("To do so:")],
                      [sg.Text("1. Go to https://takeout.google.com/settings/takeout"),sg.Button("click here")],
                      [sg.Text("2. Deselect all and scroll to the bottom of the page")],
                      [sg.Text("3. Tick the YouTube and YouTube Music item")],
                      [sg.Text("4. Select JSON format instead of the default HTML value")],
                      [sg.Text("5. Follow the steps to download the watch history and save it locally")],
                      [sg.Text("6. Use the browse button below to load the JSON file here")],
                      [sg.Text(" ")],
                      [sg.In(key='_FILES_'), sg.FileBrowse(file_types=(("JSON Files", "*.json"),))],
                      [sg.Button("SUBMIT", size=(55, 2))],
                      [sg.Text(" ")],
                      [sg.Button("QUIT")]
                      ]
            # Create the Window
            window2 = sg.Window(event, layout)
            # Event Loop to process "events"
            while True:
                event, values = window2.read()
                if event in (None, sg.WINDOW_CLOSED, 'QUIT'):
                    break
                if event == "click here":
                    webbrowser.open('https://takeout.google.com/settings/takeout', new=2)
                if event == "SUBMIT":
                    filepath = values['_FILES_']
                    if filepath == "":
                        break
                    else:
                        self.get_watch_history(filepath)
                        window2.close()
                        SpotifyTag = 'My YouTube watch history'

        nome_playlist = input("What would you like the new playlist to be called? ")
        self.add_song_to_playlist(nome_playlist, SpotifyTag)

    # Step 5: Add songs to playlist
    def add_song_to_playlist(self, nome_playlist, playlistDescription):
        # Step 5.1 - Create dictionary of songs is covered by the initial flow
        # Step 5.2 - Collect uri
        uris = [info["spotify_uri"] for song, info in self.all_song_info.items()]
        # List must be cleaned to remove all the NotFound and None items
        uris = self.remove_values_from_list(uris, "NotFound")
        uris = self.remove_none_from_list(uris)
        print("Spotify URIs collected")

        # Step 5.3 - Create a new playlist
        playlist_id = self.create_spotify_playlist(nome_playlist, playlistDescription)
        print("New Spotify playlist created, ID: "+playlist_id)

        # Step 5.4 - Add all songs to the new playlist
        request_data = json.dumps(uris)
        request_data = '{"uris":' + request_data + ', "position": 0}'
        query = "https://api.spotify.com/v1/playlists/{play_id}/tracks".format(play_id=playlist_id)
        response = requests.post(
            query,
            data=request_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {chiave}".format(chiave=self.spotify_token)
            }
        )
        response_json = response.json()
        # error handling

        print("Playlist populated")
        return response_json


# *********************************************************************************************************************
# TOOLS

    # Reusable function to save json responses
    def salva_json (self, data, json_filename):
        json_datetime_now = datetime.datetime.now()
        json_datetime_now_usable = json_datetime_now.strftime("%Y%m%d%H%M%S")

        filename = json_filename + json_datetime_now_usable + ".txt"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    # Reusable function to save dictionaries tuple lists
    def salva_lists (self, dizionario, header, new_filename):
        list_datetime_now = datetime.datetime.now()
        list_datetime_now_usable = list_datetime_now.strftime("%Y%m%d%H%M%S")

        filename = new_filename + list_datetime_now_usable + ".csv"
        with open(filename, 'w', newline='', encoding='utf8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=header)
            writer.writeheader()
            for key, info in dizionario.items():
                writer.writerow(info)

    # Reusable function to clean list - remove specific value passed as valueToRemove
    def remove_values_from_list(self, myList, valueToRemove):
        return [value for value in myList if value != valueToRemove]

    # Reusable function to clean list - remove None (null)
    def remove_none_from_list(self, myList):
        return [value for value in myList if value != None]

# *********************************************************************************************************************

if __name__ == '__main__':
    cp = CopiaLaYoutuber()
    cp.apri_finestra()

    # This has to be nested in the GUI flow
    # cp.add_song_to_playlist()

# *********************************************************************************************************************
# STORAGE
