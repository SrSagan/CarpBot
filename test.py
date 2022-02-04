import requests
import shutil
from tinytag import TinyTag
import time

url = "https://cdn.discordapp.com/attachments/880103197866352700/937089326116904961/Juegos_de_seduccion.mp3"

r = requests.get(url, stream=True)

if r.status_code == 200:
    with open("song.mp3", 'wb') as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)

audio = TinyTag.get("song.mp3")

print("Duration: " + time.strftime("%H:%M:%S", time.gmtime(audio.duration)))
print("Title: " + audio.title)

