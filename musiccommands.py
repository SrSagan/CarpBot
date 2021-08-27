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

#---------------------------------------------------------PLAY----------------------------------------------------------#

    @commands.command(pass_context=True,  # reproduce musica
                      aliases=['p', 'pl'],
                      name='play',
                      help='Reproduce un link de youtube',
                      brief='Reproduce musica'
                      )
    async def play(self, ctx, *url):

        author = ctx.message.author
        channel = author.voice.channel
        songs = []

        links = b.get_links()

        # SI ESTA CONECTADO SOLO agrega el link a la queue

        voice_client = discord.utils.get(
            ctx.bot.voice_clients, guild=ctx.guild)

        if voice_client != None:

            await b.youtube_download(ctx, url)

            vc = ctx.voice_client  # si no esta reproduciendo, comienza a reproducir
            if vc.is_playing() == False:
                b.set_status(True)
                await b.play(vc, ctx)

        # SI NO ESTA CONECTADO SE TIENE QUE CONECTAR Y REPRODUCIR >:(((((((((( uuh acabo de caer si esta conectado y no esta reproduciendo si ;-;
        # WENO SE ARREGLA DESPOIS
        else:
            
            await b.youtube_download(ctx, url)
            '''
            for link in url:
                if link in links:
                    await ctx.send("El link ya esta en la lista")
                else:
                    links.append(link)
                    b.set_links(links)
                    ydl_opts = a.get_yld_opts()  # opciones de descarga guardadas en datos
                    ydl = youtube_dl.YoutubeDL(ydl_opts)
                    ydl.download([link])

                    info_dict = ydl.extract_info(
                        link, download=False)  # guarda el nombre
                    names = b.get_names()
                    names.append(info_dict.get('title', None))
                    b.set_names(names)

                    songNum = ydl_opts["outtmpl"]
                    songs.append(str(songNum))
                    x = songNum.find(".mp3")
                    songNum = int(songNum[:x])
                    songs = b.get_files()
                    songs.append(str(songNum)+".mp3")
                    b.set_files(songs)
                    songNum = songNum+1
                    ydl_opts["outtmpl"] = str(songNum)+".mp3"
                    a.set_yld_opts(ydl_opts)'''

            await channel.connect()

            vc = ctx.voice_client
            if vc.is_playing() == False:  # si no esta reproduciendo comienza a reproducir (no hace falta pero weno)
                b.set_status(True)
                await b.play(vc, ctx)

#---------------------------------------------------------QUEUE----------------------------------------------------------#

    @commands.command(
        aliases=['q'],
        name='queue',
        help='Muestra la lista de canciones',
        brief='Muestra la queue'
    )
    async def queue(self, ctx):
        names = b.get_names()
        index = b.get_index()
        number = 1
        data=''
        for name in names:
            if number == index:
                data = data+"\n**"+(str(number)+") "+str(name)+"**")
            else:
                data = data+"\n**"+(str(number)+")** "+str(name))
            number = number+1
        embed = discord.Embed(
            title="Queue", color=0x3498DB, description=data)
        await ctx.send(embed=embed)
    
#---------------------------------------------------------STOP----------------------------------------------------------#

    @commands.command(
        aliases=['s'],
        name='stop',
        help='Para la musica',
        brief='Para la musica'
    )
    async def stop(self, ctx):
        vc = ctx.voice_client
        b.set_status(False)
        vc.stop()

#---------------------------------------------------------PAUSE----------------------------------------------------------#

    @commands.command(
        aliases=['ps'],
        name='pause',
        help='Pausa la musica',
        brief='Pausa la musica'
    )
    async def pause(self, ctx):
        vc = ctx.voice_client
        if vc.is_paused() == True:
            await ctx.send("Audio already paused")
        else:
            vc.pause()

#---------------------------------------------------------RESUME----------------------------------------------------------#

    @commands.command(
        aliases=['r'],
        name='resume',
        help='Resume la musica',
        brief='Resume la musica'
    )
    async def resume(self, ctx):
        vc = ctx.voice_client
        if vc.is_paused() == True:
            vc.resume()
        else:
            await ctx.send("Audio not paused")
    
#---------------------------------------------------------NEXT----------------------------------------------------------#

    @commands.command(
        aliases=['n', 'skip'],
        name='next',
        help='Salta la cancion',
        brief='Salta la musica'
    )
    async def next(self, ctx):
        vc = ctx.voice_client
        index = b.get_index()
        index = index
        b.set_index(index)
        vc.stop()

#---------------------------------------------------------BACK----------------------------------------------------------#

    @commands.command(
        aliases=['b'],
        name='back',
        help='Vuelve a la anterior cancion',
        brief='Vuelve la musica'
    )
    async def back(self, ctx):
        vc = ctx.voice_client
        index = b.get_index()
        index = index-2
        b.set_index(index)
        vc.stop()
    
    


def setup(bot):
    bot.add_cog(music(bot))
