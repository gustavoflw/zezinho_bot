import os
import re
import requests
import youtube_dl
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup
from bot_print import print_with_colors as print

class YoutubeHandler: # You can search for a video or pass directly an URL. This will download and stream the video to audio.
    def __init__(self):
        self.download_options = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': '/tmp/%(title)s.%(ext)s',
        }

    def play(self, to_play):
        # Evaluate if the input is a URL or a search query
        if 'https://' in to_play or 'http://' in to_play:
            url = to_play
        else:
            url = self.search(to_play)
        print(f"- Playing video from {url}", color='orange')
        file_path = self.download(url)
        return file_path

    def download(self, url):
        print(f"- Downloading video from {url}", color='orange')
        with youtube_dl.YoutubeDL(self.download_options) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            file_path = ydl.prepare_filename(info_dict)
            file_path = file_path.replace('.webm', '.mp3')
            if not os.path.exists(file_path):
                print(f"- Downloading video to {file_path}", color='orange')
                ydl.download([url])
            else:
                print(f"- Video already downloaded in {file_path}", color='orange')
        return file_path

    def search(self, query):
        print(f"- Searching for {query}", color='orange')
        query_string = urllib.parse.urlencode({"search_query": query})
        formatUrl = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)
        search_results = re.findall(r"watch\?v=(\S{11})", formatUrl.read().decode())
        clip = requests.get("https://www.youtube.com/watch?v=" + "{}".format(search_results[0]))
        clip2 = "https://www.youtube.com/watch?v=" + "{}".format(search_results[0])
        inspect = BeautifulSoup(clip.content, "html.parser")
        yt_title = inspect.find_all("meta", property="og:title")
        for concatMusic1 in yt_title:
            pass
        print(f"- Found video: {clip2}", color='orange')
        return clip2

# Test
if __name__ == "__main__":
    video_to_search = 'Linkin Park Numb'
    youtube = YoutubeHandler()
    url = youtube.search(video_to_search)
    file_path = youtube.download(url)
