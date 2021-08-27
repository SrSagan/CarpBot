import os
import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import time
import asyncio
import youtube_dl
import data

a = data.datos()


class music:
    def __init__(self):
        links = []
        names = []
        files = []
        index = 0
        status = False

        self.links = links
        self.names = names
        self.files = files
        self.index = index
        self.status = status

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

#------------YOUTUBE DOWNLOAD-------------#

    async def youtube_download(self, ctx, url):
        for link in url:

            if link in self.links:
                await ctx.send("El link ya esta en la lista")
            else:
                self.links.append(link)

                ydl_opts = a.get_yld_opts()  # opciones de descarga guardadas en datos
                ydl = youtube_dl.YoutubeDL(ydl_opts)
                ydl.download([link])

                info_dict = ydl.extract_info(
                    link, download=False)  # guarda el nombre
                    
                self.names.append(info_dict.get('title', None))

                songNum = ydl_opts["outtmpl"]
                x = songNum.find(".mp3")
                songNum = int(songNum[:x])
                self.files.append(str(songNum)+".mp3")

                songNum = songNum+1
                # descarga todos los links y cambia el nombre del proximo archivo a descargar
                ydl_opts["outtmpl"] = str(songNum)+".mp3"

                a.set_yld_opts(ydl_opts)


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

            embed = discord.Embed(
                title="Now Playing", color=0x3498DB, description=str(self.names[self.index]))
            await ctx.send(embed=embed)  # muestra que esta reproduciendo
            await ctx.send("playing index:"+str(self.index))
            vc.play(discord.FFmpegPCMAudio(
                self.files[self.index]))  # reproduce

            # elimina el archivo anterior para ahorrar espacio
            if self.index >= 2:
                os.system("rm "+self.files[self.index-2])
            self.index = self.index+1  # sube el contador
