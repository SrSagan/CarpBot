import os

import discord
from discord.ext import commands
import data
import youtube_dl
from discord import FFmpegPCMAudio


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

    @commands.command(pass_context=True,
                      name='play',
                      help='Reproduce un link de youtube',
                      brief='Reproduce musica'
                      )
    async def play(self, ctx, *url):
        ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
        ydl=youtube_dl.YoutubeDL(ydl_opts)
        ytlinks = []
        ytlinks.append(url)

        for links in ytlinks:
            print(links)
            author = ctx.message.author
            channel = author.voice.channel
            vc = await channel.connect()
            ydl.download(links[0])
            for file in os.listdir("./"):
                if file.endswith(".mp3"):
                    os.rename(file, 'song.mp3')
            vc.play(discord.FFmpegPCMAudio("song.mp3"))
            vc.is_playing()
            #os.system("rm"+' '+'"'+str(video.title)+'"'+'.webm')
        await ctx.send("estoy aca")

    '''@commands.command(pass_context=True,
    	name='queue',
    	help='Muestra las canciones en la lista de reproduccion',
    	brief='Muestra la queue'
    	)
    async def queue(ctx):

    	for url in ytlinks:
    		print(url)
    		v = new(url[0])
    		await ctx.send(str(v.title))'''


def setup(bot):
    bot.add_cog(music(bot))
