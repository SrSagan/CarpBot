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

    @commands.command(pass_context=True,  # reproduce musica
                      name='play',
                      help='Reproduce un link de youtube',
                      brief='Reproduce musica'
                      )
    async def play(self, ctx, *url):

        for link in url:
            a.add_links(link)

        links = a.get_links()

        for link in links:
            ydl_opts = a.get_yld_opts()  # opciones de descarga guardadas en datos
            ydl = youtube_dl.YoutubeDL(ydl_opts)
            ydl.download([link])

            songNum = ydl_opts["outtmpl"]
            x = songNum.find(".mp3")
            songNum = int(songNum[:x])
            print(songNum)
            songNum = songNum+1
            ydl_opts["outtmpl"] = str(songNum)+".mp3"
            a.set_yld_opts(ydl_opts)

            author = ctx.message.author
            channel = author.voice.channel

            voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)

            if voice_client == None:
                vc = await channel.connect()  # entra en la llamada

            #vc.play(discord.FFmpegPCMAudio(str(songNum-1)+".mp3"))
            if vc.is_playing() == False:
                vc.play(discord.FFmpegPCMAudio(str(songNum-1)+".mp3"))
                


def setup(bot):
    bot.add_cog(music(bot))
