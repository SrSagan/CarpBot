import os
import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import time
import asyncio
import youtube_dl
import data
from requests import get
import json

a = data.datos()


class music:
    def __init__(self):
        links = []
        names = []
        files = []
        index = 0
        status = False
        thumbnails = []
        lengths = []
        time = ""

        self.links = links
        self.names = names
        self.files = files
        self.index = index
        self.status = status
        self.thumbnails = thumbnails
        self.lengths = lengths
        self.time = time

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

    def reset_all(self):
        self.links = []
        self.names = []
        self.files = []
        self.index = 0
        self.thumbnails = []
        self.lengths = []
        self.time = ""

# ------------YOUTUBE QUEUER-------------#

    async def music_queuer(self, ctx, reqest):
        ydl_opts = {
            'format': 'bestaudio/best',
            'extract_flat': 'in_playlist',
            'forcethumbnail': 'best',
        }
        type = "none"

        ydl = youtube_dl.YoutubeDL(ydl_opts)
        try:
            get(reqest)
        except:
            video = ydl.extract_info(f"ytsearch:{reqest}", download=False)[
                'entries'][0]
        else:
            video = ydl.extract_info(reqest, download=False)

        json_object = json.dumps(video, indent=4)

        # Writing to sample.json
        with open("sample.json", "w") as outfile:
            outfile.write(json_object)

        if "_type" in video:
            if video.get("_type", None) == "playlist":
                type = "playlist"
            else:
                type = "none"
        else:
            type = "link"

        if type == "playlist":
            counter = 0
            for entrie in video["entries"]:
                vid_name = video["entries"][counter]['title']
                vid_length = video["entries"][counter]['duration']
                vid_length = time.strftime(
                    "%H:%M:%S", time.gmtime(vid_length))
                vid_link = video["entries"][counter]['url']
                if vid_link in self.links:
                    await ctx.send("El link ya esta en la lista")
                else:
                    self.links.append(vid_link)
                    self.names.append(vid_name)
                    self.lengths.append(vid_length)
                counter = counter+1
            embed = discord.Embed(
                title="Queued", color=0x3498DB, description=str(len(video["entries"]))+" songs")
            await ctx.send(embed=embed)

        else:

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

            if vid_link in self.links:
                await ctx.send("El link ya esta en la lista")
            else:
                self.links.append(vid_link)
                self.names.append(vid_name)
                self.lengths.append(vid_length)
                embed = discord.Embed(
                    title="Queued", color=0x3498DB, description=str(vid_name))
                embed.set_image(url=vid_thumbnail)
                embed.set_footer(text="Length "+str(vid_length))
                await ctx.send(embed=embed)

#--------------MUSIC PLAYER---------------#

    async def play(self, vc, ctx):

        while True:  # comienza el loop de reproduccion

            while True:  # si esta reproduciendo no hace nada y espera
                if vc.is_playing() == False:
                    if vc.is_paused() == False:
                        break
                await asyncio.sleep(0.25)

            # si termina la queue frena el loop
            if self.index+1 > len(self.links) or self.status == False:
                await ctx.send("Queue over")
                break

            ydl = youtube_dl.YoutubeDL()
            r = ydl.extract_info(self.links[self.index], download=False)
            vid_thumbnail = r.get('thumbnail', None)

            embed = discord.Embed(
                title="Now Playing", color=0x3498DB, description=str(self.names[self.index]))
            embed.set_image(url=vid_thumbnail)
            await ctx.send(embed=embed)  # muestra que esta reproduciendo

            t = time.localtime()
            self.time = time.strftime("%H:%M:%S", t)

            vc.play(discord.FFmpegPCMAudio(
                r["formats"][0]["url"], before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'))  # reproduce

            self.index = self.index+1  # sube el contador
