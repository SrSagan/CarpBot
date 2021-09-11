import os
import re

import discord
from discord.ext import commands
from discord.flags import alias_flag_value
from requests.models import RequestEncodingMixin
import data
import music
import datetime
import time

a = data.datos()
b = music.music()


class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


#---------------------------------------------------------LEAVE----------------------------------------------------------#


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
        b.reset_all()

#---------------------------------------------------------PLAY----------------------------------------------------------#

    @commands.command(pass_context=True,  # reproduce musica
                      aliases=['p', 'pl'],
                      name='play',
                      help='Reproduce un link de youtube',
                      brief='Reproduce musica'
                      )
    async def play(self, ctx, *request):

        author = ctx.message.author
        channel = author.voice.channel

        # SI ESTA CONECTADO SOLO agrega el link a la queue

        voice_client = discord.utils.get(
            ctx.bot.voice_clients, guild=ctx.guild)

        texto = ""
        for word in request:
            if len(request) == 1:
                texto = request[0]
            else:
                texto = (texto+" "+word)

        if voice_client != None:

            await b.music_queuer(ctx, texto)

            vc = ctx.voice_client  # si no esta reproduciendo, comienza a reproducir
            if vc.is_playing() == False:
                b.set_status(True)
                await b.play(vc, ctx)

        # SI NO ESTA CONECTADO SE TIENE QUE CONECTAR Y REPRODUCIR >:(((((((((( uuh acabo de caer si esta conectado y no esta reproduciendo si ;-;
        # WENO SE ARREGLA DESPOIS
        else:

            await b.music_queuer(ctx, texto)
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
        lengths = b.get_lenghts()
        start_time = b.get_time()

        x = time.strptime(start_time.split(',')[0], '%H:%M:%S')
        # convierte el timepo comienzo a segundos
        start_time = datetime.timedelta(
            hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()
        x = time.strptime(lengths[index-1].split(',')[0], '%H:%M:%S')
        # lo mismo pero del largo del video
        length = datetime.timedelta(
            hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()

        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        # checkeea tiempo actual
        x = time.strptime(current_time.split(',')[0], '%H:%M:%S')
        current_time = datetime.timedelta(
            hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()

        time_elapsed = current_time - start_time  # resta los tiempos
        time_left = time.strftime("%H:%M:%S", time.gmtime(
            length-time_elapsed))

        number = 1
        data = ''
        for name in names:
            if number >= index-1:
                if number == index:
                    data = data+"\n**"+(str(number)+") " +
                                        str(name)+"**")+" Time Left: "+time_left
                else:
                    data = data+"\n**"+(str(number)+")** " +
                                        str(name))+" Lenght: "+lengths[number-1]
            number = number+1
            if number==index+9:
                data = data+"\n\n**"+str(len(names)-index-8)+" Songs more**"
                break
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

#---------------------------------------------------------SONG----------------------------------------------------------#

    @commands.command(
        name='song',
        help='Muestra que cancion se esta reproduciendo',
        brief='Song playing'
    )
    async def song(self, ctx):
        start_time = b.get_time()
        lengths = b.get_lenghts()
        names = b.get_names()
        index = b.get_index()

        x = time.strptime(start_time.split(',')[0], '%H:%M:%S')
        # convierte el timepo comienzo a segundos
        start_time = datetime.timedelta(
            hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()
        x = time.strptime(lengths[index-1].split(',')[0], '%H:%M:%S')
        # lo mismo pero del largo del video
        length = datetime.timedelta(
            hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()

        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        # checkeea tiempo actual
        x = time.strptime(current_time.split(',')[0], '%H:%M:%S')
        current_time = datetime.timedelta(
            hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()

        time_elapsed = current_time - start_time  # resta los tiempos

        time_left = time.strftime("%H:%M:%S", time.gmtime(
            length-time_elapsed))  # lo conviernet
        # amigo alto bardo hacer la pija esta

        embed = discord.Embed(
            title="Now playing", color=0x3498DB, description=str(names[index-1]))
        embed.set_footer(text="Length: "+str(lengths[index-1]))
        embed.set_footer(text="Time Left: "+time_left)
        await ctx.send(embed=embed)

#---------------------------------------------------------CLEAR----------------------------------------------------------#

    @commands.command(
        aliases=['c'],
        name='clear',
        help='Limpia la queue',
        brief='Limpia la queue'
    )
    async def clear(self, ctx):
        vc = ctx.voice_client
        b.set_status(False)
        vc.stop()
        b.reset_all()


def setup(bot):
    bot.add_cog(music(bot))
