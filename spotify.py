import json
from urllib import response
import requests
from secretss import spotify_token, base_64, spotify_user_id, refresh_token
import threading, time

class SongControl():
    def __init__(self):
        
        self.refresh_token = refresh_token
        self.base_64 = base_64
        self.user_id = spotify_user_id
        self.spotify_token = ""
        self.volume = 0
        self.refresh()
        
    def getVolume(self):

        query = "https://api.spotify.com/v1/me/player"

        response = requests.get(query, headers={"Content-Type": "application", "Authorization": "Bearer {}".format(self.spotify_token)})

        response_json = response.json()


        self.volume = response_json["device"]["volume_percent"]

    def songSkip(self):
        print("Skipping song")

        query = "https://api.spotify.com/v1/me/player/next"

        response = requests.post(query, headers={"Content-Type": "application", "Authorization": "Bearer {}".format(self.spotify_token)})


    def songPrevious(self):
        print("Going to previous song")

        query = "https://api.spotify.com/v1/me/player/previous"

        response = requests.post(query, headers={"Content-Type": "application", "Authorization": "Bearer {}".format(self.spotify_token)})

    def volumeUp(self, change=3):
        print("Increasing Volume")

        if self.volume + change > 100:
            self.volume = 100

        else:
            self.volume += change

        query = "https://api.spotify.com/v1/me/player/volume?volume_percent={}".format(self.volume)

        response = requests.put(query, headers={"Content-Type": "application", "Authorization": "Bearer {}".format(self.spotify_token)})


    def volumeDown(self, change=3):
        print("Decreasing Volume")

        if self.volume < change:
            self.volume = 0
        else:
            self.volume = self.volume - change

        query = "https://api.spotify.com/v1/me/player/volume?volume_percent={}".format(self.volume)

        response = requests.put(query, headers={"Content-Type": "application", "Authorization": "Bearer {}".format(self.spotify_token)})

    def refresh(self):
        #should refresh

        print("refreshing")

        query = "https://accounts.spotify.com/api/token"

        response = requests.post(query, data={"grant_type": "refresh_token", "refresh_token": refresh_token}, headers={"Authorization": "Basic " + base_64})

        response_json = response.json()

        self.spotify_token = response_json["access_token"]


        self.getVolume()


    def volumeRefresh(self):
        self.getVolume()
        time.sleep(1)
        self.volumeRefresh()


a = SongControl()

refresher = threading.Thread(target=a.volumeRefresh, daemon=True)
refresher.start()