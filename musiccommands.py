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
import json

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
        vc = ctx.voice_client
        vc.stop()
        await ctx.voice_client.disconnect()
        b.reset_all(ctx)

#---------------------------------------------------------PLAY----------------------------------------------------------#

    @commands.command(pass_context=True,  # reproduce musica
                      aliases=['p', 'pl'],
                      name='play',
                      help='Reproduce un link de youtube',
                      brief='Reproduce musica'
                      )
    async def play(self, ctx, *request):

        # cosas a hacer:
        # Se tiene que checkear por problemas, checkear si el client esta en un canal de voz DONE
        if len(request) > 0:
            author = ctx.message.author
            try:
                channel = author.voice.channel
                status=True
            except:
                await ctx.send("You're not in any voice channel")
                status=True

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
                    await b.play(vc, ctx)

            # SI NO ESTA CONECTADO SE TIENE QUE CONECTAR Y REPRODUCIR >:(((((((((( uuh acabo de caer si esta conectado y no esta reproduciendo si ;-;
            # WENO SE ARREGLA DESPOIS
            elif status==True:

                await b.music_queuer(ctx, texto)
                await channel.connect()

                vc = ctx.voice_client
                if vc.is_playing() == False:  # si no esta reproduciendo comienza a reproducir (no hace falta pero weno)
                    await b.play(vc, ctx)
        else:
            await ctx.send("Write the name or link of a video to add to queue")

#---------------------------------------------------------QUEUE----------------------------------------------------------#

    @commands.command(
        aliases=['q'],
        name='queue',
        help='Muestra la lista de canciones',
        brief='Muestra la queue'
    )
    async def queue(self, ctx):
        servers = b.get_servers()
        servers_id = b.get_servers_id()
        id = ctx.message.guild.id

        if int(id) in servers_id:
            playlist = servers[servers_id.index(int(id))]
            lengths = []
            names = []
            index = playlist["playlist"]["cplaying"]

            for j in playlist["playlist"]["songs"]:
                lengths.append(j["length"])
                names.append(j["name"])

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
            valor = 1
            data = ''
            if len(names) - index < 9 and len(names) > 9:
                valor = 9-(len(names)-index)
            for name in names:
                if number >= index-valor:
                    if number == index and playlist["playlist"]["status"] == True:
                        data = data+"\n**"+(str(number)+") " +
                                            str(name)+"**")+" *Time Left: "+time_left+"*"
                    else:
                        data = data+"\n**"+(str(number)+")** " +
                                            str(name))+" *Lenght: "+lengths[number-1]+"*"
                number = number+1
                if number == index+9:
                    data = data+"\n\n**" + \
                        str(len(names)-index-8)+" Songs more**"
                    break
            embed = discord.Embed(
                title="Queue", color=0x3498DB, description=data)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Not playing anything")

#---------------------------------------------------------STOP----------------------------------------------------------#

    @commands.command(
        aliases=['s'],
        name='stop',
        help='Para la musica',
        brief='Para la musica'
    )
    async def stop(self, ctx):
        # chekear si el client esta en canal de voz sino no usar done
        servers = b.get_servers()
        servers_id = b.get_servers_id()
        id = ctx.message.guild.id
        author = ctx.message.author

        try:
            channel = author.voice.channel
            status=True
        except:
            await ctx.send("You're not in any voice channel")
            status=False

        if int(id) in servers_id and status==True:
            playlist = servers[servers_id.index(int(id))]
            vc = ctx.voice_client
            playlist["playlist"]["status"] = False
            vc.stop()

#---------------------------------------------------------PAUSE----------------------------------------------------------#


    @commands.command(
        aliases=['ps'],
        name='pause',
        help='Pausa la musica',
        brief='Pausa la musica'
    )
    async def pause(self, ctx):
        # chekear si el client esta en canal de voz sino no usar
        vc = ctx.voice_client
        author = ctx.message.author        

        try:
            channel = author.voice.channel
            status=True
        except:
            await ctx.send("You're not in any voice channel")
            status=False

        if vc.is_paused() == True and status==True:
            await ctx.send("Audio already paused")
        else:
            vc.pause()

#---------------------------------------------------------RESUME----------------------------------------------------------#

    @commands.command(
        aliases=['res'],
        name='resume',
        help='Resume la musica',
        brief='Resume la musica'
    )
    async def resume(self, ctx):
        # chekear si el client esta en canal de voz sino no usar
        author = ctx.message.author        

        try:
            channel = author.voice.channel
            status=True
        except:
            await ctx.send("You're not in any voice channel")
            status=False

        vc = ctx.voice_client
        if vc.is_paused() == True and status==True:
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
    async def next(self, ctx, *args):
        # chekear si el client esta en canal de voz sino no usar
        servers = b.get_servers()
        servers_id = b.get_servers_id()
        id = ctx.message.guild.id
        author = ctx.message.author        

        try:
            channel = author.voice.channel
            status=True
        except:
            await ctx.send("You're not in any voice channel")
            status=False
        if int(id) in servers_id and status==True:

            playlist = servers[servers_id.index(int(id))]
            songs = playlist["playlist"]["songs"]
            vc = ctx.voice_client

            if len(args) != 0:
                if args[0].isnumeric():
                    if int(args[0]) <= len(songs):
                        index = int(args[0])-1
                        playlist["playlist"]["cplaying"] = index
                        vc.stop()
                    else:
                        await ctx.send("Song out of range")
                else:
                    await ctx.send("Specify the number of a song")
            else:
                index = playlist["playlist"]["cplaying"]
                index = index
                playlist["playlist"]["cplaying"] = index
                vc.stop()
        json_object = json.dumps(servers, indent=4)

        # Writing to sample.json
        with open("sample.json", "w") as outfile:
            outfile.write(json_object)

#---------------------------------------------------------BACK----------------------------------------------------------#

    @commands.command(
        aliases=['b'],
        name='back',
        help='Vuelve a la anterior cancion',
        brief='Vuelve la musica'
    )
    async def back(self, ctx):
        # chekear si el client esta en canal de voz sino no usar
        servers = b.get_servers()
        servers_id = b.get_servers_id()
        id = ctx.message.guild.id
        author = ctx.message.author        

        try:
            channel = author.voice.channel
            status=True
        except:
            await ctx.send("You're not in any voice channel")
            status=False

        if int(id) in servers_id and status==True:
            playlist = servers[servers_id.index(int(id))]
            vc = ctx.voice_client

            if playlist["playlist"]["status"] == False:
                playlist["playlist"]["cplaying"] = playlist["playlist"]["cplaying"]-1
                await b.play(vc, ctx)

            else:
                playlist["playlist"]["cplaying"] = playlist["playlist"]["cplaying"]-1
                vc.stop()

#---------------------------------------------------------SONG----------------------------------------------------------#

    @commands.command(
        name='song',
        help='Muestra que cancion se esta reproduciendo',
        brief='Song playing'
    )
    async def song(self, ctx):
        start_time = b.get_time()
        servers = b.get_servers()
        servers_id = b.get_servers_id()
        id = ctx.message.guild.id

        if int(id) in servers_id:
            playlist = servers[servers_id.index(int(id))]

            lengths = []
            names = []
            index = playlist["playlist"]["cplaying"]
            for j in playlist["playlist"]["songs"]:
                lengths.append(j["length"])
                names.append(j["name"])

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
            # lo conviernet
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
        servers = b.get_servers()
        servers_id = b.get_servers_id()
        id = ctx.message.guild.id
        author = ctx.message.author        

        try:
            channel = author.voice.channel
            status=True
        except:
            await ctx.send("You're not in any voice channel")
            status=False

        if int(id) in servers_id and status==True:
            playlist = servers[servers_id.index(int(id))]
            playlist["playlist"]["status"] = False
            vc.stop()
            b.reset_all(ctx)

#---------------------------------------------------------REMOVE----------------------------------------------------------#

    @commands.command(
        aliases=['r'],
        name='remove',
        help='Removes a song from the queue, use: remove <number>',
        brief='Removes a song'
    )
    async def clear(self, ctx, *args):
        vc = ctx.voice_client
        servers = b.get_servers()
        servers_id = b.get_servers_id()
        id = ctx.message.guild.id
        author = ctx.message.author        

        try:
            channel = author.voice.channel
            status=True
        except:
            await ctx.send("You're not in any voice channel")
            status=False

        if int(id) in servers_id and status==True:
            playlist = servers[servers_id.index(int(id))]
            if len(args) != 0:
                if args[0].isnumeric():
                    if int(args[0]) <= len(playlist["playlist"]["songs"]):

                        embed = discord.Embed(
                            title="Removed:", color=0x3498DB, description=str(playlist["playlist"]["songs"][int(args[0])-1]["name"]))
                        embed.set_footer(
                            text="Length: "+str(playlist["playlist"]["songs"][int(args[0])-1]["length"]))
                        await ctx.send(embed=embed)

                        playlist["playlist"]["songs"].pop(int(args[0])-1)
                    else:
                        await ctx.send("Song out of range")
                else:
                    await ctx.send("Specify the number of a song")
            else:
                await ctx.send("Specify the number of a song to remove. remove <number>")


def setup(bot):
    bot.add_cog(music(bot))
