import discord
import data
from requests import get
import discord.utils
import lenguajes as leng
import requests
import shutil
from tinytag import TinyTag
import os
import yt_dlp
import servermanager as s
from loguru import logger

a = data.datos()
sm = s.serverManager()

class queuer:

#-------------QUEUER--------------#

    async def queuer(self, song, id):
        server = {
            "id": 0,
            "cplaying": 0,
            "ptime": None,
            "time": None,
            "status": False,
            "tlenght": 0,
            'looping': 0,
            "songs":
            [{
                "name": None,
                "link": None,
                "length": None,
                "class": None,
            }],
        }
        if(sm.exists(id)):
            if(isinstance(song, list)):
                s.servers[sm.get_index(id)]["songs"]+=song
            else:
                s.servers[sm.get_index(id)]["songs"].append(song)
            sm.apply()
        else:
            s.servers_id.append(int(id))
            server["id"]=int(id)
            if(isinstance(song, list)):
                print("Es nuevo y encima una list")
                server["songs"] = song
            else:
                server["songs"][0]["name"] = song["name"]
                server["songs"][0]["length"] = song["length"]
                server["songs"][0]["link"] = song["link"]
                server["songs"][0]["class"] = song["class"]
            s.servers.append(server)
            sm.apply()

#-------------YOUTUBE QUEUER--------------#

    async def youtube_queuer(self, ctx, request):
        ydl_opts = {
            'quiet': False,
            'extract_flat': 'in_playlist',
            'youtube_include_dash_manifest': False,
            'youtube_include_hls_manifest': False,
        }
        type = "none"

        ydl = yt_dlp.YoutubeDL(ydl_opts)
        try:
            get(request)
        except:
            video = ydl.extract_info(f"ytsearch:{request}", download=False)[  # busca que es por nombre
                'entries'][0]
        else:
            # si no es nombre busca la url
            try:
                video = ydl.extract_info(request, download=False)
            except:
                await ctx.send("Video unavailable")

        # diferencia que tipo de dato le fue dado (playlist, link, nombre)
        if "_type" in video:
            if video.get("_type", None) == "playlist":
                type = "playlist"
            else:
                type = "none"
        else:
            type = "link"

        if type == "playlist":  # si es una playlist agrega cada cancion por separado
            logger.debug("Downloading playlist")
            sm.apply()
            logger.debug("I made it past here??'")
            title = video["title"]
            if("uploader" in video): author = video["uploader"]
            else: author= "Unknown"

            totalLenght = 0
            counter = 0
            tempSongs=[]
            for entrie in video["entries"]:
                vid_name = video["entries"][counter]['title']
                vid_length = video["entries"][counter]['duration']
                if(vid_length != None):
                    totalLenght = totalLenght+vid_length
                    vid_length = a.get_time(vid_length)
                    vid_link = video["entries"][counter]['url']

                    id = ctx.message.guild.id

                    song = {
                        "name": vid_name,
                        "length": vid_length,
                        "link": vid_link,
                        "class": "yt"
                    }
                    if(counter == 0):
                        await self.queuer(song, id)
                    else:
                        tempSongs.append(song)

                counter = counter+1

            s.servers[sm.get_index(id)]["songs"] = s.servers[s.servers_id.index(int(id))]["songs"] + tempSongs
            embed = discord.Embed(
                title="Queued "+title, color=0x3498DB, description=str(len(tempSongs)+1)+" "+leng.canciones[a.get_lenguaje(ctx.message)])
            totalLenght = a.get_time(totalLenght)
            embed.set_footer(text=leng.duracion[a.get_lenguaje(ctx.message)]+": "+str(totalLenght)+"\n"+author)
            await ctx.send(embed=embed)

        else:  # si es un link o nombre guarda tambien los datos
            # titulo, duracion, url, thumbnail*, url

            # agarra distinta info del video
            vid_name = video.get('title', None)
            vid_length = video.get('duration')
            vid_length = a.get_time(vid_length)

            if type == 'none':
                ydl = yt_dlp.YoutubeDL({
                    'format': 'bestaudio/best', 'forcethumbnail': 'best', })
                vid_link = video.get('url', None)
                vid_thumbnail = ydl.extract_info(vid_link, download=False)
                vid_thumbnail = vid_thumbnail.get('thumbnail', None)

            elif type == 'link':
                vid_link = video.get('webpage_url', None)
                vid_thumbnail = video.get('thumbnail', None)

            id = ctx.message.guild.id

            song = {
                "name": vid_name,
                "length": vid_length,
                "link": vid_link,
                "class": "yt"
            }
            
            await self.queuer(song, id)

            if(s.servers[sm.get_index(id)]["status"] == True):
                embed = discord.Embed(
                    title="Queued", color=0x3498DB, description=str(vid_name))
                embed.set_image(url=vid_thumbnail)
                embed.set_footer(text=leng.duracion[a.get_lenguaje(ctx.message)]+": "+str(vid_length)+"\n"+leng.posicion[a.get_lenguaje(ctx.message)]+": "+str(len(s.servers[s.servers_id.index(int(id))]["songs"])))
                await ctx.send(embed=embed)

#-------------FILE QUEUER--------------#

    async def file_queuer(self, ctx, url):
        id = ctx.message.guild.id

        #download the song and get the metadata
        r = requests.get(url, stream=True)

        #https://cdn.discordapp.com/attachments/879920775195422783/937832073236979772/ta_bien.mp3

        #get the name from the url
        y = url.rfind("/")
        name = url[y+1:]

        if r.status_code == 200:
            with open("temp/"+name, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

        audio = TinyTag.get("temp/"+name)

        if(audio.title==None):
            title = name
        else:
            title = audio.title
        
        vid_length=a.get_time(audio.duration)

        song = {
                "name": title,
                "length": vid_length,
                "link": url,
                "class": "fl"
        }
        await self.queuer(song, id)
        embed = discord.Embed(
            title="Queued", color=0x3498DB, description=str(title))
        embed.set_footer(text=leng.duracion[a.get_lenguaje(ctx.message)]+": "+str(vid_length)+"\n"+leng.posicion[a.get_lenguaje(ctx.message)]+": "+str(len(s.servers[s.servers_id.index(int(id))]["songs"])))
        await ctx.send(embed=embed)

        os.remove("temp/"+name)