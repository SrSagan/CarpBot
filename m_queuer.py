import discord
import youtube_dl
import data
from requests import get
import json
import discord.utils
import lenguajes as leng
import requests
import shutil
from tinytag import TinyTag
import os

a = data.datos()

class queuer:

#-------------QUEUER--------------#

    async def queuer(self, song, id, servers_id, servers):
        server = {
            "id": 0,
            "playlist":
            {
                "cplaying": 0,
                "ptime": None,
                "time": None,
                "status": False,
                "tlenght": 0,
                'looping': 0,
                'pressed' : [1,1,1,1,0],
                "songs":
                [{
                    "name": None,
                    "link": None,
                    "length": None,
                    "class": None,
                }],
            }
        }
        if(int(id) in servers_id):
            servers[servers_id.index(int(id))]["playlist"]["songs"].append(song)
            return servers_id, servers
        else:
            servers_id.append(int(id))
            server["playlist"]["songs"][0]["name"] = song["name"]
            server["playlist"]["songs"][0]["length"] = song["length"]
            server["playlist"]["songs"][0]["link"] = song["link"]
            server["playlist"]["songs"][0]["class"] = song["class"]
            servers.append(server)
            return servers_id, servers

#-------------YOUTUBE QUEUER--------------#

    async def youtube_queuer(self, ctx, reqest, servers_id, servers):
        ydl_opts = {
            'quiet': True,
            'format': 'bestaudio/best',
            'extract_flat': 'in_playlist',
            'forcethumbnail': 'best',
            'youtube_include_dash_manifest': False,
        }
        type = "none"

        ydl = youtube_dl.YoutubeDL(ydl_opts)
        try:
            get(reqest)
        except:
            video = ydl.extract_info(f"ytsearch:{reqest}", download=False)[  # busca que es por nombre
                'entries'][0]
        else:
            # si no es nombre busca la url
            video = ydl.extract_info(reqest, download=False)

        # diferencia que tipo de dato le fue dado (playlist, link, nombre)
        if "_type" in video:
            if video.get("_type", None) == "playlist":
                type = "playlist"
            else:
                type = "none"
        else:
            type = "link"

        if type == "playlist":  # si es una playlist agrega cada cancion por separado

            json_object=json.dumps(video, indent=4)
            with open("video.json", "w") as outfile:
                outfile.write(json_object)
        
            
            title = video["title"]
            if("uploader" in video): author = video["uploader"]
            else: author= "Unknown"

            totalLenght = 0
            counter = 0
            for entrie in video["entries"]:
                vid_name = video["entries"][counter]['title']
                vid_length = video["entries"][counter]['duration']
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

                servers_id, servers = await self.queuer(song, id, servers_id, servers)


                counter = counter+1

            embed = discord.Embed(
                title="Queued "+title, color=0x3498DB, description=str(len(video["entries"]))+" "+leng.canciones[a.get_lenguaje(ctx.message)])
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
                ydl = youtube_dl.YoutubeDL({
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
            
            servers_id, servers = await self.queuer(song, id, servers_id, servers)

            if(servers[servers_id.index(int(id))]["playlist"]["cplaying"] == 1):
                embed = discord.Embed(
                    title="Queued", color=0x3498DB, description=str(vid_name))
                embed.set_image(url=vid_thumbnail)
                embed.set_footer(text=leng.duracion[a.get_lenguaje(ctx.message)]+": "+str(vid_length)+"\n"+leng.posicion[a.get_lenguaje(ctx.message)]+": "+str(len(servers[servers_id.index(int(id))]["playlist"]["songs"])))
                await ctx.send(embed=embed)

        
        json_object = json.dumps(servers, indent=4)

        # Writing to sample.json
        with open("sample.json", "w") as outfile:
            outfile.write(json_object)
        return servers_id, servers

#-------------FILE QUEUER--------------#

    async def file_queuer(self, ctx, url, servers_id, servers):
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
        servers_id, servers = await self.queuer(song, id, servers_id, servers)
        embed = discord.Embed(
            title="Queued", color=0x3498DB, description=str(title))
        embed.set_footer(text=leng.duracion[a.get_lenguaje(ctx.message)]+": "+str(vid_length)+"\n"+leng.posicion[a.get_lenguaje(ctx.message)]+": "+str(len(servers[servers_id.index(int(id))]["playlist"]["songs"])))
        await ctx.send(embed=embed)

        os.remove("temp/"+name)

        return servers_id, servers