import os

import discord
from discord.ext import commands
import data
import music
import youtube_dl
from discord import FFmpegPCMAudio
import asyncio

a = data.datos()
b = music.music()


class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        aliases=['l', 'lv'],
        name='leave',
        help='Sale del canal de voz',
        brief='Sale del canal de voz'
    )
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()
        ydl_opts = a.get_yld_opts()
        ydl_opts["outtmpl"] = "0.mp3"
        a.set_yld_opts(ydl_opts)
        os.system("rm *.mp3")
        b.reset_all()

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

        # SI ESTA CONECTADO SOLO agrega el link a la queue

        voice_client = discord.utils.get(
            ctx.bot.voice_clients, guild=ctx.guild)

        if voice_client != None:

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
                    songs = b.get_files()
                    songs.append(str(songNum)+".mp3")
                    b.set_files(songs)
                    songNum = songNum+1
                    ydl_opts["outtmpl"] = str(songNum)+".mp3"

                    a.set_yld_opts(ydl_opts)
        
            vc = ctx.voice_client
            await ctx.send(str(vc.is_playing()))
            if vc.is_playing() == False:
                await b.play(vc, ctx)

        #SI NO ESTA CONECTADO SE TIENE QUE CONECTAR Y REPRODUCIR >:(((((((((( uuh acabo de caer si esta conectado y no esta reproduciendo si ;-;
        #WENO SE ARREGLA DESPOIS
        else:

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
                    songs = b.get_files()
                    songs.append(str(songNum)+".mp3")
                    b.set_files(songs)
                    songNum = songNum+1
                    ydl_opts["outtmpl"] = str(songNum)+".mp3"
                    a.set_yld_opts(ydl_opts)

                    
            await channel.connect()

            vc = ctx.voice_client
            if vc.is_playing() == False:
                await b.play(vc, ctx)


    @commands.command(
        aliases=['q'],
        name='queue',
        help='Muestra la lista de canciones',
        brief='Muestra la queue'
    )
    async def queue(self, ctx):
        files = b.get_files()
        for file in files:
            await ctx.send(file)


def setup(bot):
    bot.add_cog(music(bot))
