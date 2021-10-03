import os
import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import time
import asyncio
from requests.sessions import merge_setting
import youtube_dl
import data
from requests import get
import json

a = data.datos()


class music:
    def __init__(self):
        status = False
        time = ""

        servers = []
        servers_id = []

        self.servers = servers
        self.servers_id = servers_id

        self.status = status
        self.time = time

#-----------------SERVERS-----------------#

    def get_servers(self):
        return self.servers

    def set_servers(self, servers):
        self.servers = servers

#----------------SERVERS_ID---------------#

    def get_servers_id(self):
        return self.servers_id

    def set_servers_id(self, servers_id):
        self.servers_id = servers_id

#------------------LINKS------------------#

    def get_links(self):
        return self.links

    def set_links(self, links):
        self.links = links

#------------------NAMES------------------#

    def get_names(self):
        return self.names

    def set_names(self, names):
        self.names = names

#------------------FILES------------------#

    def get_files(self):
        return self.files

    def set_files(self, files):
        self.files = files

#------------------FILES------------------#

    def get_lenghts(self):
        return self.lengths

#------------------FILES------------------#

    def get_time(self):
        return self.time

#------------------INDEX------------------#

    def get_index(self):
        return self.index

    def set_index(self, index):
        self.index = index

#-----------------STATUS------------------#

    def get_status(self):
        return self.status

    def set_status(self, status):
        self.status = status

#-----------------GENERAL-----------------#

    def reset_all(self, ctx):
        id = ctx.message.guild.id
        if int(id) in self.servers_id:
            self.servers.pop(self.servers_id.index(int(id)))
            self.servers_id.pop(self.servers_id.index(int(id)))

        json_object = json.dumps(self.servers, indent=4)

        # Writing to sample.json
        with open("sample.json", "w") as outfile:
            outfile.write(json_object)

# ------------YOUTUBE QUEUER--------------#

    async def music_queuer(self, ctx, reqest):
        ydl_opts = {
            'quiet' : False,
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

        server = {
            "id": 0,
            "playlist":
            {
                "cplaying": 0,
                "ptime": None,
                "time": None,
                "status": False,
                "tlenght": 0,
                "songs":
                [{
                    "name": None,
                    "link": None,
                    "length": None,
                }],
            }
        }

        if type == "playlist":  # si es una playlist agrega cada cancion por separado
            totalLenght=0
            counter = 0
            for entrie in video["entries"]:
                vid_name = video["entries"][counter]['title']
                vid_length = video["entries"][counter]['duration']
                totalLenght= totalLenght+vid_length
                vid_length = time.strftime(
                    "%H:%M:%S", time.gmtime(vid_length))
                vid_link = video["entries"][counter]['url']

                id = ctx.message.guild.id

                if int(id) in self.servers_id:
                    song = {
                        "name": vid_name,
                        "length": vid_length,
                        "link": vid_link,
                    }
                    self.servers[self.servers_id.index(
                        int(id))]["playlist"]["songs"].append(song)

                else:
                    self.servers_id.append(int(id))
                    server["id"] = int(id)
                    server["playlist"]["songs"][0]["name"] = vid_name
                    server["playlist"]["songs"][0]["length"] = vid_length
                    server["playlist"]["songs"][0]["link"] = vid_link
                    self.servers.append(server)

                counter = counter+1
            embed = discord.Embed(
                title="Queued", color=0x3498DB, description=str(len(video["entries"]))+" songs")
            totalLenght=time.strftime(
                    "%H:%M:%S", time.gmtime(totalLenght))
            embed.set_footer(text="Length "+str(totalLenght))
            await ctx.send(embed=embed)

        else:  # si es un link o nombre guarda tambien los datos
            # titulo, duracion, url, thumbnail*, url

            # agarra distinta info del video
            vid_name = video.get('title', None)
            vid_length = video.get('duration')
            vid_length = time.strftime("%H:%M:%S", time.gmtime(vid_length))

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

            if int(id) in self.servers_id:
                song = {
                    "name": vid_name,
                    "length": vid_length,
                    "link": vid_link,
                }
                self.servers[self.servers_id.index(
                    int(id))]["playlist"]["songs"].append(song)

            else:
                self.servers_id.append(int(id))
                server["id"] = int(id)
                server["playlist"]["songs"][0]["name"] = vid_name
                server["playlist"]["songs"][0]["length"] = vid_length
                server["playlist"]["songs"][0]["link"] = vid_link
                self.servers.append(server)

            embed = discord.Embed(
                title="Queued", color=0x3498DB, description=str(vid_name))
            embed.set_image(url=vid_thumbnail)
            embed.set_footer(text="Length "+str(vid_length))
            await ctx.send(embed=embed)
        json_object = json.dumps(self.servers, indent=4)

        # Writing to sample.json
        with open("sample.json", "w") as outfile:
            outfile.write(json_object)

#--------------MUSIC PLAYER---------------#

    async def play(self, vc, ctx):
        id = ctx.message.guild.id
        msg_sent=False

        while True:  # comienza el loop de reproduccion
            if int(id) in self.servers_id:

                j = self.servers[self.servers_id.index(int(id))]
                j["playlist"]["status"] = True
                index = j["playlist"]["cplaying"]
                json_object = json.dumps(self.servers, indent=4)
                # Writing to sample.json
                with open("sample.json", "w") as outfile:
                    outfile.write(json_object)

               #--------------------------REPRODUCIENDO---------------------------#
                while True:  # si esta reproduciendo no hace nada y espera
                    if vc.is_playing() == False:
                        if vc.is_paused() == False:
                            break
                    await asyncio.sleep(0.25)
                #--------------------------REPRODUCIENDO---------------------------#

                index = j["playlist"]["cplaying"]

                # si termina la queue frena el loop
                if j["playlist"]["cplaying"]+1 > len(j["playlist"]["songs"]) or j["playlist"]["status"] == False or int(id) not in self.servers_id:
                    j["playlist"]["status"] = False
                    embed = discord.Embed(
                        title="Queue over", color=0x3498DB)
                    await ctx.send(embed=embed)

                    json_object = json.dumps(self.servers, indent=4)
                    # Writing to sample.json
                    with open("sample.json", "w") as outfile:
                        outfile.write(json_object)
                    break

                ydl = youtube_dl.YoutubeDL()
                r = ydl.extract_info(
                    j["playlist"]["songs"][index]["link"], download=False)
                vid_thumbnail = r.get('thumbnail', None)
                # check if last message was a "Now Playing" from carpbot

                if(msg_sent==True): await msg.delete()

                # if it is it should be deleted

                embed = discord.Embed(
                    title="Now Playing", color=0x3498DB, description=str(j["playlist"]["songs"][index]["name"]))
                embed.set_image(url=vid_thumbnail)
                # muestra que esta reproduciendo
                msg = await ctx.send(embed=embed)
                msg_sent=True

                t = time.localtime()
                j["playlist"]["time"] = time.strftime("%H:%M:%S", t)
                vc.play(discord.FFmpegPCMAudio(
                    r["formats"][0]["url"], before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'))  # reproduce

                index = index+1  # sube el contador
                j["playlist"]["cplaying"] = index

                json_object = json.dumps(self.servers, indent=4)

                # Writing to sample.json
                with open("sample.json", "w") as outfile:
                    outfile.write(json_object)
