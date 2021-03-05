import logging
import threading
import jellyfish
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from time import time
import requests

# https://vk.music7s.cc/api/search.php?search={name}&time=1614957922464


class MyThread(object):

    def __init__(self):
        self.thread = []
        self.arr = []
        self.play_list = []
        self.err_list = []
        self.offset = 0
        self.i = 0
        self.pars()
        self.start()
        print(self.err_list)

    def start(self):
        for music in self.play_list:
            x = threading.Thread(target=self.download, args=(music,))
            self.thread.append(x)
            x.start()

    def pars(self):
        r = requests.get(f"https://m.vk.com/audio?act=audio_playlist2000088379_2&access_hash=f63ebd24f227769cb1&from=/audio?act=audio_playlists2000088379&offset={self.offset}")
        soup = BeautifulSoup(r.text, 'html.parser')
        for track in soup.find_all("div", "ai_label"):
            self.i += 1
            if self.i % 100 == 0:
                self.offset += 100
                self.pars()
            art = track.find("span", "ai_artist").find("a").text
            title = track.find("span", "ai_title").text
            self.play_list.append(f"{art} - {title}")

    def download(self, music):
        r = requests.get(f"https://vk.music7s.cc/api/search.php?search={music}&time={int(time())}")
        if not r.json()['error']:
            arr = []
            print(r.json())
            for i in r.json()["items"]:
                proc = int(jellyfish.jaro_similarity(music, f"{i['artist']} - {i['title']}") * 100)
                title = f"{i['artist']} - {i['title']}".replace("/", "").replace("?", "")
                arr.append({
                    "proc": proc,
                    "title": title,
                })
            print(arr.sort(key=lambda item: item.keys()))
                #print(f"{title} - {music} \n percents: {proc}")
                #if proc >= 60:
                    #with open(f"C:/Users/kitpl/PycharmProjects/get_music/music/{title}.mp3", "wb") as music:
                        #r = requests.get(urljoin("https://vk.music7s.cc", i['url']))
                        #music.write(r.content)
                    #break
        else:
            self.err_list.append({
                "track": music,
                "error": r.json()
            })


MyThread()
