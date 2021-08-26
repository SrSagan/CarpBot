import os

import discord
from discord.ext import commands
import data
import music
import youtube_dl
from discord import FFmpegPCMAudio
import time
import asyncio

a = data.datos()
b = music.music()


class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='leave',
        help='Sale del canal de voz',
        brief='Sale del canal de voz'
    )
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()
        ydl_opts = a.get_yld_opts()
        ydl_opts["outtmpl"] = "1.mp3"
        a.set_yld_opts(ydl_opts)
        os.system("rm *.mp3")
        b.set_links([])

    @commands.command(pass_context=True,  # reproduce musica
                      aliases=['p', 'pl'],
                      name='play',
                      help='Reproduce un link de youtube',
                      brief='Reproduce musica'
                      )
    async def play(self, ctx, *url):

        author = ctx.message.author
        channel = author.voice.channel

        links = b.get_links()
        songs = []


        for link in url:

            if link in links:
                await ctx.send("El link ya esta en la lista")
            else:
                links.append(link)
                b.set_links(links)

                ydl_opts = a.get_yld_opts()  # opciones de descarga guardadas en datos
                ydl = youtube_dl.YoutubeDL(ydl_opts)
                ydl.download([link])

                songNum = ydl_opts["outtmpl"]
                songs.append(str(songNum))
                x = songNum.find(".mp3")
                songNum = int(songNum[:x])
                songNum = songNum+1
                ydl_opts["outtmpl"] = str(songNum)+".mp3"

                songs = b.get_files()
                songs.append(str(songNum)+".mp3")
                b.set_files(songs)


                a.set_yld_opts(ydl_opts)

        voice_client = discord.utils.get(
            ctx.bot.voice_clients, guild=ctx.guild)

        if voice_client == None:  # si no esta conectado
            vc = await channel.connect() # se copnecta
        vc=ctx.voice_client

        while True: #loop de reprodduccion de musica
            index = b.get_index()
            songs = b.get_files()
            song = songs[index]

            os.system("rm "+songs[index-1])

            if vc.is_playing() == False:
                print("playing:", song)
                vc.play(discord.FFmpegPCMAudio(song))
                b.set_index(index+1)
            else:
                if index >= len(songs):
                    break

            # else:
                #os.system("rm "+str(songNum-1)+".mp3")


def setup(bot):
    bot.add_cog(music(bot))
