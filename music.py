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
        return self.names

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

        while True:

            while True:
                if vc.is_playing() == False:
                    break
                await asyncio.sleep(0.25)

            if self.index+1 > len(self.links):
                await ctx.send("Queue over")
                break

            await ctx.send("Now playing: "+str(self.files[self.index]))
            vc.play(discord.FFmpegPCMAudio(self.files[self.index]))
            os.system("rm "+self.files[self.index-1])
            self.index = self.index+1
