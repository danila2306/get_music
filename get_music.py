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
        self.threads = []
        self.arr = []
        self.play_list = []
        self.err_list = []
        self.offset = 0
        self.i = 0
        self.pars()
        self.start()
        print(self.err_list)

    def wait_threads(self, last = False):
        def wait(self):
            for thread in self.threads:
                thread.join()
            self.threads = []

        if last == False:
            if len(self.threads) == 30:
                wait(self)
        else:
            wait(self)
            

    def start(self):
        for music in self.play_list:
            x = threading.Thread(target=self.download, args=(music,))
            self.threads.append(x)
            x.start()
            self.wait_threads()
        self.wait_threads(True)

    def pars(self):
        url = f"https://m.vk.com/audio?act=audio_playlist2000088379_2&access_hash=f63ebd24f227769cb1&from=/audio?act=audio_playlists2000088379&offset={self.offset}"
        print(url)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        for track in soup.find_all("div", "ai_label"):
            self.i += 1
            if self.i % 100 == 0:
                self.offset += 100
                self.pars()
            art = track.find("span", "ai_artist").find("a").text
            title = track.find("span", "ai_title").text
            self.play_list.append(f"{art} - {title}")

    def sort_music_proc(self, arr_music):
        assoc_arr_music = {}
        for key, music in enumerate(arr_music):
            assoc_arr_music[key] = music["proc"]
        assoc_arr_music = list(assoc_arr_music.items())
        assoc_arr_music.sort(key=lambda i: i[1])
        return list(reversed(assoc_arr_music))[0]

    def download(self, music):
        url = f"https://vk.music7s.cc/api/search.php?search={music}&time={int(time())}"
        r = requests.get(url)
        if not r.json()['error']:
            arr = []
            for i in r.json()["items"]:
                proc = int(jellyfish.jaro_similarity(music, f"{i['artist']} - {i['title']}") * 100)
                title = f"{i['artist']} - {i['title']}".replace("/", "").replace("?", "")
                arr.append({
                    "proc": proc,
                    "title": title,
                    "url": i["url"]
                })

            similiar_music = self.sort_music_proc(arr)
            music = arr[similiar_music[0]]
            
            if similiar_music[1] >= 60:
                print(f"{music['title']} download. Percent similiar: {proc}")
                r = requests.get(urljoin("https://vk.music7s.cc", music['url']), stream=True, timeout=None)
                with open(f"musics/{music['title']}.mp3", "wb") as file:
                    for chunk in r.iter_content(1024):
                        file.write(chunk)
        else:
            self.err_list.append({
                "track": music,
                "error": r.json()
            })

MyThread()
