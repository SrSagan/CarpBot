import os

import discord
from discord.ext import commands
import data
import youtube_dl
from discord import FFmpegPCMAudio

a = data.datos()


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
    @commands.command(pass_context=True,  # reproduce musica
                      name='play',
                      help='Reproduce un link de youtube',
                      brief='Reproduce musica'
                      )
    async def play(self, ctx, *url):

        author = ctx.message.author
        channel = author.voice.channel

        links = a.get_links()
        songs = []
        for link in url:

            if link in links:
                await ctx.send("El link ya esta en la lista")
            else:
                a.add_links(link)

        for link in links:

            ydl_opts = a.get_yld_opts()  # opciones de descarga guardadas en datos
            ydl = youtube_dl.YoutubeDL(ydl_opts)
            ydl.download([link])

            songNum = ydl_opts["outtmpl"]
            x = songNum.find(".mp3")
            songNum = int(songNum[:x])
            songNum = songNum+1
            ydl_opts["outtmpl"] = str(songNum)+".mp3"
            songs.append(str(songNum)+".mp3")

            a.set_yld_opts(ydl_opts)
            
        voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if voice_client == None:  # si no esta conectado
            vc = await channel.connect()

        links = a.get_links()
        
        for song in songs:
            if vc.is_playing() == False:
                vc.play(discord.FFmpegPCMAudio(song))
            #else:
                #os.system("rm "+str(songNum-1)+".mp3")
                


def setup(bot):
    bot.add_cog(music(bot))
