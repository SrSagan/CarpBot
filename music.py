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
import random
import discord.utils

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

#----------------SHUFFLER-----------------#

    def shuffler(self, ctx):
        id = ctx.message.guild.id

        if int(id) in self.servers_id:
            j = self.servers[self.servers_id.index(int(id))]

            final = []

            cplaying = j["playlist"]["cplaying"]
            y = range(0, cplaying)

            for n in y:
                final.append(j["playlist"]["songs"][n])

            out = j["playlist"]["songs"]
            for n in y:
                out.pop(0)
            random.shuffle(out)
            final += out

            j["playlist"]["songs"] = final

# ------------YOUTUBE QUEUER--------------#

    async def music_queuer(self, ctx, reqest):
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
                'pressed' : [1,1,1,1],
                "songs":
                [{
                    "name": None,
                    "link": None,
                    "length": None,
                }],
            }
        }

        if type == "playlist":  # si es una playlist agrega cada cancion por separado
            totalLenght = 0
            counter = 0
            for entrie in video["entries"]:
                vid_name = video["entries"][counter]['title']
                vid_length = video["entries"][counter]['duration']
                totalLenght = totalLenght+vid_length
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
            totalLenght = time.strftime(
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

    async def play(self, vc, ctx, bot):
        id = ctx.message.guild.id
        msg_sent = False
        ydl_opts = {
            'quiet': True,
            'youtube_include_dash_manifest': False,
        }

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
                if j["playlist"]["looping"] == 2:
                    index = index-1

                # si termina la queue frena el loop
                if j["playlist"]["cplaying"]+1 > len(j["playlist"]["songs"]) or j["playlist"]["status"] == False or int(id) not in self.servers_id:
                    if j["playlist"]["looping"] != 1 or int(id) not in self.servers_id:
                        j["playlist"]["status"] = False
                        embed = discord.Embed(
                            title="Queue over", color=0x3498DB)
                        await ctx.send(embed=embed)

                        json_object = json.dumps(self.servers, indent=4)
                        # Writing to sample.json
                        with open("sample.json", "w") as outfile:
                            outfile.write(json_object)
                        break
                    else:
                        j["playlist"]["cplaying"] = 0
                        index = 0

                ydl = youtube_dl.YoutubeDL(ydl_opts)
                r = ydl.extract_info(
                    j["playlist"]["songs"][index]["link"], download=False)
                vid_thumbnail = r.get('thumbnail', None)
                # check if last message was a "Now Playing" from carpbot and if it wasn't deleted

                if(msg_sent == True):
                    if(discord.utils.get(bot.cached_messages, id=msg.id) != None):
                        await msg.delete()

                # if it is it should be deleted

                embed = discord.Embed(
                    title="Now Playing", color=0x3498DB, description=str(j["playlist"]["songs"][index]["name"]))
                embed.set_image(url=vid_thumbnail)
                # muestra que esta reproduciendo
                msg = await ctx.send(embed=embed)
                msg_sent = True

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

#-------------QUEUE CONTROLS--------------#

    async def control_checker(self, message, controls, bot, ctx):
        #QUE VIJA X DIOSSS
        id = ctx.message.guild.id #agarra todo lo necesario
        if(id in self.servers_id):
            j = self.servers[self.servers_id.index(int(id))]
            prev_pressed = j["playlist"]["pressed"]

            pressed = [0,0,0,0]
            out=[0,0,0,0]
            for i in range(0, 60): #timer de 1min

                cache_msg = discord.utils.get(bot.cached_messages, id=message.id) #hace todo un tema con cached messages pq ds es una vija y no retorna los msg al toque
                reactions = cache_msg.reactions

                for emoji in controls:
                    reaction = discord.utils.get(reactions, emoji=emoji)
                    pressed[controls.index(emoji)]=reaction.count #los cuenta

                counter=0 #los compara
                for press in prev_pressed:
                    if(press == pressed[counter]):
                        out[counter]=0
                    else:
                        out[counter]=1
                    counter=counter+1
                
                j["playlist"]["pressed"]=pressed #los guarda

                if(1 in out): #envia las diferencias
                    return out

                await asyncio.sleep(1)
            return "no"
