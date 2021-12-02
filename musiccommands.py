import os
import re

import discord
from discord.ext import commands
from discord.flags import alias_flag_value
from requests.models import RequestEncodingMixin
from discord.utils import get
import data
import music
import datetime
import time
import json
import asyncio
from dotenv import load_dotenv

a = data.datos()
b = music.music()

load_dotenv()
devuser = os.getenv('DEV_USER') 


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
        author = ctx.message.author

        try:
            channel = author.voice.channel
            status = True
        except:
            await ctx.send("You're not in any voice channel")
            status = False
        
        if(ctx.message.author.id == int(devuser)): status=True

        if(status == True):
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
                status = True
            except:
                await ctx.send("You're not in any voice channel")
                status = False

            # SI ESTA CONECTADO SOLO agrega el link a la queue
            if(ctx.message.author.id == int(devuser)): status=True

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
                    await b.play(vc, ctx, self.bot)

            # SI NO ESTA CONECTADO SE TIENE QUE CONECTAR Y REPRODUCIR >:(((((((((( uuh acabo de caer si esta conectado y no esta reproduciendo si ;-;
            # WENO SE ARREGLA DESPOIS
            elif status == True:

                await b.music_queuer(ctx, texto)
                await channel.connect()

                vc = ctx.voice_client
                if vc.is_playing() == False:  # si no esta reproduciendo comienza a reproducir (no hace falta pero weno)
                    await b.play(vc, ctx, self.bot)
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
        vc = ctx.voice_client

        if int(id) in servers_id:
            playlist = servers[servers_id.index(int(id))]
            lengths = []
            names = []
            index = playlist["playlist"]["cplaying"]

            for j in playlist["playlist"]["songs"]:
                lengths.append(j["length"])
                names.append(j["name"])

            start_time = playlist["playlist"]["time"]
            x = time.strptime(start_time.split(',')[0], '%H:%M:%S')
            # convierte el timepo comienzo a segundos

            start_time = datetime.timedelta(
                hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()
            x = time.strptime(lengths[index-1].split(',')[0], '%H:%M:%S')
            # lo mismo pero del largo del video

            length = datetime.timedelta(
                hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()
            # checkeea tiempo actual
            if vc.is_paused() == True and playlist["playlist"]["status"] == True:
                x = time.strptime(
                    playlist["playlist"]["ptime"].split(',')[0], '%H:%M:%S')
                current_time = datetime.timedelta(
                    hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()
            else:
                t = time.localtime()
                current_time = time.strftime("%H:%M:%S", t)

                x = time.strptime(current_time.split(',')[0], '%H:%M:%S')
                current_time = datetime.timedelta(
                    hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()

            time_elapsed = current_time - start_time  # resta los tiempos

            time_left = time.strftime("%H:%M:%S", time.gmtime(
                length-time_elapsed))

            #------------------IMPRESION---------------#

            start = index-1
            printed=0
            edit=0
            while True:
                if start <= 0:
                    start =1
                if start > len(names)-10:
                    start = len(names)-10
                    
                counter=1
                data=''
                for name in names:
                    if counter == index and playlist["playlist"]["status"] == True and counter>=start:
                        data = data+"\n**"+(str(counter)+") " +
                                            str(name)+"**")+" *Time Left: "+time_left+"*"

                    elif counter>=start:
                        data = data+"\n**"+(str(counter)+")** " +
                                            str(name))+" *Lenght: "+lengths[counter-1]+"*"

                    counter = counter+1

                    if counter == start+11:
                        if(len(names)-counter+1 != 0):
                            data = data+"\n\n**" + \
                                str(len(names)-counter+1)+" More songs**"
                        break

                embed = discord.Embed(
                    title="Queue", color=0x3498DB, description=data)

                if(printed==0):
                    message = await ctx.send(embed=embed)
                elif(edit==1):
                    print("edited")
                    await message.edit(embed=embed)
                    edit=0

                #------------------IMPRESION---------------#

                #------------------REACITONS---------------#
                if(printed==0):
                    controls = ['⏮️', '⏪', '⏩', '⏭️']
                    for emoji in controls:
                        await message.add_reaction(emoji)
                printed=1

                await asyncio.sleep(0.5)
                

                pressed = await b.control_checker(message, controls, self.bot, ctx) #devuelve las diferencias entre el anterior control y el nuevo
                if(pressed == "no"): break

                else:
                    counter=0
                    for press in pressed:
                        if(press == 1): #checkea donde hay diferencia y actua
                            if(counter == 0):
                                start = 0
                            elif(counter == 1):
                                start = start-10
                            elif(counter == 2):
                                start = start+10
                            elif(counter == 3):
                                start = len(names)-10
                            edit=1
                        counter=counter+1

                    #------------------REACITONS---------------#

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
            status = True
        except:
            await ctx.send("You're not in any voice channel")
            status = False

        if(ctx.message.author.id == int(devuser)): status=True

        if int(id) in servers_id and status == True:
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
        servers = b.get_servers()
        servers_id = b.get_servers_id()
        vc = ctx.voice_client
        author = ctx.message.author
        id = ctx.message.guild.id

        if int(id) in servers_id:
            playlist = servers[servers_id.index(int(id))]
            try:
                channel = author.voice.channel
                status = True
            except:
                await ctx.send("You're not in any voice channel")
                status = False

            if(ctx.message.author.id == int(devuser)): status=True

            if vc.is_paused() == True and status == True:
                await ctx.send("Audio already paused")
            else:
                t = time.localtime()
                playlist["playlist"]["ptime"] = time.strftime("%H:%M:%S", t)
                vc.pause()
                embed = discord.Embed(title="Paused", color=0x3498DB)
                await ctx.send(embed=embed)

#---------------------------------------------------------RESUME----------------------------------------------------------#

    @commands.command(
        aliases=['r'],
        name='resume',
        help='Resume la musica',
        brief='Resume la musica'
    )
    async def resume(self, ctx):
        # chekear si el client esta en canal de voz sino no usar
        servers = b.get_servers()
        servers_id = b.get_servers_id()
        author = ctx.message.author
        id = ctx.message.guild.id
        if int(id) in servers_id:
            playlist = servers[servers_id.index(int(id))]

            try:
                channel = author.voice.channel
                status = True
            except:
                await ctx.send("You're not in any voice channel")
                status = False

            if(ctx.message.author.id == int(devuser)): status=True

            vc = ctx.voice_client
            if vc.is_paused() == True and status == True:
                vc.resume()
                embed = discord.Embed(title="Resumed", color=0x3498DB)
                await ctx.send(embed=embed)

                t = time.localtime()
                resume_time = time.strftime("%H:%M:%S", t)
                x = time.strptime(resume_time.split(',')[0], '%H:%M:%S')
                resume_time = datetime.timedelta(
                    hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()

                x = time.strptime(
                    playlist["playlist"]["time"].split(',')[0], '%H:%M:%S')
                tiempo = datetime.timedelta(
                    hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()

                x = time.strptime(
                    playlist["playlist"]["ptime"].split(',')[0], '%H:%M:%S')
                ptime = datetime.timedelta(
                    hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()

                time_paused = resume_time-ptime
                playlist["playlist"]["time"] = time.strftime("%H:%M:%S", time.gmtime(
                    tiempo+time_paused))

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
            status = True
        except:
            await ctx.send("You're not in any voice channel")
            status = False

        if(ctx.message.author.id == int(devuser)): status=True

        if int(id) in servers_id and status == True:

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
                if playlist["playlist"]["looping"] == 2:
                    playlist["playlist"]["cplaying"] = playlist["playlist"]["cplaying"]+1
                    vc.stop()
                else:
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
            status = True
        except:
            await ctx.send("You're not in any voice channel")
            status = False

        if(ctx.message.author.id == int(devuser)): status=True

        if int(id) in servers_id and status == True:
            playlist = servers[servers_id.index(int(id))]
            vc = ctx.voice_client

            if playlist["playlist"]["status"] == False:
                playlist["playlist"]["cplaying"] = playlist["playlist"]["cplaying"]-1
                await b.play(vc, ctx)

            else:
                playlist["playlist"]["cplaying"] = playlist["playlist"]["cplaying"]-2
                vc.stop()

#---------------------------------------------------------SONG----------------------------------------------------------#

    @commands.command(
        name='song',
        help='Muestra que cancion se esta reproduciendo',
        brief='Song playing'
    )
    async def song(self, ctx):
        servers = b.get_servers()
        servers_id = b.get_servers_id()
        id = ctx.message.guild.id
        vc = ctx.voice_client

        if int(id) in servers_id:
            playlist = servers[servers_id.index(int(id))]
            start_time = playlist["playlist"]["time"]
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

            # checkeea tiempo actual

            if vc.is_paused() == True and playlist["playlist"]["status"] == True:
                x = time.strptime(
                    playlist["playlist"]["ptime"].split(',')[0], '%H:%M:%S')
                current_time = datetime.timedelta(
                    hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()
            else:
                t = time.localtime()
                current_time = time.strftime("%H:%M:%S", t)

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
            status = True
        except:
            await ctx.send("You're not in any voice channel")
            status = False

        if(ctx.message.author.id == int(devuser)): status=True

        if int(id) in servers_id and status == True:
            playlist = servers[servers_id.index(int(id))]
            playlist["playlist"]["status"] = False
            vc.stop()
            b.reset_all(ctx)

#---------------------------------------------------------REMOVE----------------------------------------------------------#

    @commands.command(
        aliases=['rm'],
        name='remove',
        help='Removes a song from the queue, use: remove <number>',
        brief='Removes a song'
    )
    async def remove(self, ctx, *args):
        vc = ctx.voice_client
        servers = b.get_servers()
        servers_id = b.get_servers_id()
        id = ctx.message.guild.id
        author = ctx.message.author

        try:
            channel = author.voice.channel
            status = True
        except:
            await ctx.send("You're not in any voice channel")
            status = False

        if(ctx.message.author.id == int(devuser)): status=True

        if int(id) in servers_id and status == True:
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
                    if args[0] == "last":
                        embed = discord.Embed(
                            title="Removed:", color=0x3498DB, description=str(playlist["playlist"]["songs"][len(playlist["playlist"]["songs"])-1]["name"]))
                        embed.set_footer(
                            text="Length: "+str(playlist["playlist"]["songs"][len(playlist["playlist"]["songs"])-1]["length"]))
                        await ctx.send(embed=embed)

                        playlist["playlist"]["songs"].pop(
                            len(playlist["playlist"]["songs"])-1)
                    else:
                        await ctx.send("Specify the number of a song")
            else:
                await ctx.send("Specify the number of a song to remove. remove <number>")

#---------------------------------------------------------MOVE----------------------------------------------------------#

    @commands.command(
        aliases=['m'],
        name='move',
        help='Moves a song in the queue',
        brief='Moves a song'
    )
    async def move(self, ctx, *args):
        vc = ctx.voice_client
        servers = b.get_servers()
        servers_id = b.get_servers_id()
        id = ctx.message.guild.id
        author = ctx.message.author

        try:
            channel = author.voice.channel
            status = True
        except:
            await ctx.send("You're not in any voice channel")
            status = False

        if(ctx.message.author.id == int(devuser)): status=True

        if int(id) in servers_id and status == True:
            playlist = servers[servers_id.index(int(id))]
            if len(args) > 0:
                if args[0].isnumeric():
                    if int(args[0]) <= len(playlist["playlist"]["songs"]) and int(args[1]) <= len(playlist["playlist"]["songs"]):
                        moving_song = playlist["playlist"]["songs"][int(
                            args[0])-1]
                        if args[1].isnumeric():
                            playlist["playlist"]["songs"].pop(int(args[0])-1)
                            playlist["playlist"]["songs"].insert(
                                int(args[1])-1, moving_song)
                            embed = discord.Embed(title="Song moved", color=0x3498DB, description=str(
                                playlist["playlist"]["songs"][int(args[1])-1]["name"])+" moved to position "+str(args[1]))
                            await ctx.send(embed=embed)

                        else:
                            await ctx.send("Specify where to move the song")
                    else:
                        await ctx.send("Song out of range")
                else:
                    await ctx.send("Specify what song to move and where to move it")
            else:
                await ctx.send("Specify song and place. Use: move <song> <place to move>")

#---------------------------------------------------------LOOP----------------------------------------------------------#

    @commands.command(
        aliases=['lp'],
        name='loop',
        help='Loops the song or queue',
        brief='Loops the song or queue'
    )
    async def loop(self, ctx, *args):
        vc = ctx.voice_client
        servers = b.get_servers()
        servers_id = b.get_servers_id()
        id = ctx.message.guild.id

        if int(id) in servers_id:
            playlist = servers[servers_id.index(int(id))]

            if playlist["playlist"]["looping"] == 0:
                playlist["playlist"]["looping"] = 1
                embed = discord.Embed(
                    description="Now looping **queue**", color=0x3498DB)
                await ctx.send(embed=embed)

            elif playlist["playlist"]["looping"] == 1:
                playlist["playlist"]["looping"] = 2
                embed = discord.Embed(
                    description="Now looping the **current track**", color=0x3498DB)
                await ctx.send(embed=embed)

            elif playlist["playlist"]["looping"] == 2:
                playlist["playlist"]["looping"] = 0
                embed = discord.Embed(
                    description="Looping is now **disabled**", color=0x3498DB)
                await ctx.send(embed=embed)

#---------------------------------------------------------SHUFFLE----------------------------------------------------------#

    @commands.command(
        aliases=['sh'],
        name='shuffle',
        help='Shuffles the playlist',
        brief='Shuffles'
    )
    async def shuffle(self, ctx):
        b.shuffler(ctx)
        await ctx.send("music shuffled")


def setup(bot):
    bot.add_cog(music(bot))
