import os
import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import time
import asyncio


class music:
    def __init__(self):
        links = []
        names = []
        files = []
        index = 0

        self.links = links
        self.names = names
        self.files = files
        self.index = index

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
        self.inxdex = index

#-----------------GENERAL-----------------#

    def reset_all(self):
        self.links = []
        self.names = []
        self.files = []
        self.index = 0

#--------------MUSIC PLAYER---------------#

    async def play(self, vc, ctx):

        while True:  # comienza el loop de reproduccion

            while True:  # si esta reproduciendo no hace nada y espera
                if vc.is_playing() == False:
                    break
                await asyncio.sleep(0.25)

            # si termina la queue frena el loop
            if self.index+1 > len(self.links):
                await ctx.send("Queue over")
                break

            embed = discord.Embed(
                title="Now Playing", color=0x3498DB, description=str(self.names[self.index]))
            await ctx.send(embed=embed)  # muestra que esta reproduciendo

            vc.play(discord.FFmpegPCMAudio(
                self.files[self.index]))  # reproduce

            # elimina el archivo anterior para ahorrar espacio
            if self.index != 0:
                os.system("rm "+self.files[self.index-1])
            self.index = self.index+1  # sube el contador
