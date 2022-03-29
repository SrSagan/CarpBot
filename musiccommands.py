import os

import discord
from discord.ext import commands
import data
import music
import datetime
import time
import json
import asyncio
from dotenv import load_dotenv
import lenguajes as leng
from lyricsgenius import Genius

a = data.datos()
b = music.music()

devusers = []
load_dotenv()
dev = os.getenv('DEV_USERS')  # checkea los los dev users
lyrics_init = os.getenv("LYRICS")
gn = Genius(lyrics_init)

while True:
    x = dev.find(",")
    if(x == -1):
        devusers.append(int(dev))
        break
    devusers.append(int(dev[:x]))
    dev = dev[x+1:]



class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


#---------------------------------------------------------LEAVE----------------------------------------------------------#


    @commands.command(
        aliases=['l', 'lv'],
        name='leave',
    )
    async def leave(self, ctx):
        vc = ctx.voice_client
        author = ctx.message.author

        try:
            channel = author.voice.channel
            status = True
        except:
            await ctx.send(leng.neencdv[a.get_lenguaje(ctx.message)])
            status = False

        if(ctx.message.author.id in devusers):
            status = True

        if(status == True):
            vc.stop()
            await ctx.voice_client.disconnect()
            b.reset_all(ctx)

#---------------------------------------------------------PLAY----------------------------------------------------------#

    @commands.command(pass_context=True,  # reproduce musica
                      aliases=['p', 'pl'],
                      name='play',
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
                status = False

            if(ctx.message.author.id in devusers):
                status = True

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
                x = texto.find("-f")
                if(x != -1):
                    await b.queuer(ctx, texto, "fl")
                else:
                    await b.queuer(ctx, texto, "yt")
                vc = ctx.voice_client  # si no esta reproduciendo, comienza a reproducir
                if vc.is_playing() == False:
                    await b.play(vc, ctx, self.bot)

            # SI NO ESTA CONECTADO SE TIENE QUE CONECTAR Y REPRODUCIR >:(((((((((( uuh acabo de caer si esta conectado y no esta reproduciendo si ;-;
            # WENO SE ARREGLA DESPOIS
            elif status == True:

                x = texto.find("-f")
                if(x != -1):
                    await b.queuer(ctx, texto, "fl")
                else:
                    await b.queuer(ctx, texto, "yt")
                    
                await channel.connect()

                vc = ctx.voice_client
                if vc.is_playing() == False:  # si no esta reproduciendo comienza a reproducir (no hace falta pero weno)
                    
                    await b.play(vc, ctx, self.bot)
            else:
                await ctx.send(leng.neencdv[a.get_lenguaje(ctx.message)])

        else:
            await ctx.send(leng.eenolduvpaalq[a.get_lenguaje(ctx.message)])

#---------------------------------------------------------QUEUE----------------------------------------------------------#

    @commands.command(
        aliases=['q'],
        name='queue',
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
            printed = 0
            edit = 0
            while True:
                if start <= 0:
                    start = 1
                if start > len(names)-10:
                    start = len(names)-10

                counter = 1
                data = ''
                for name in names:
                    if counter == index and playlist["playlist"]["status"] == True and counter >= start:
                        data = data+"\n**"+(str(counter)+") " +
                                            str(name)+"** *")+leng.tr[a.get_lenguaje(ctx.message)]+" "+time_left+"*"

                    elif counter >= start:
                        data = data+"\n**"+(str(counter)+")** " +
                                            str(name))+" *"+leng.duracion[a.get_lenguaje(ctx.message)]+": "+lengths[counter-1]+"*"

                    counter = counter+1

                    if counter == start+11:
                        if(len(names)-counter+1 != 0):
                            data = data+"\n\n**" + \
                                str(len(names)-counter+1)+" " + \
                                leng.mc[a.get_lenguaje(ctx.message)]+"**"
                        break

                embed = discord.Embed(
                    title="Queue", color=0x3498DB, description=data)

                if(printed == 0):
                    message = await ctx.send(embed=embed)
                elif(edit == 1):
                    print("edited")
                    await message.edit(embed=embed)
                    edit = 0

                #------------------IMPRESION---------------#

                #------------------REACITONS---------------#
                if(printed == 0):
                    controls = ['⏮️', '⏪', '⏩', '⏭️']
                    for emoji in controls:
                        await message.add_reaction(emoji)
                printed = 1

                await asyncio.sleep(0.5)

                # devuelve las diferencias entre el anterior control y el nuevo
                pressed = await b.control_checker(message, controls, self.bot, ctx)
                if(pressed == "no"):
                    break

                else:
                    counter = 0
                    for press in pressed:
                        if(press == 1):  # checkea donde hay diferencia y actua
                            if(counter == 0):
                                start = 0
                            elif(counter == 1):
                                start = start-10
                            elif(counter == 2):
                                start = start+10
                            elif(counter == 3):
                                start = len(names)-10
                            edit = 1
                        counter = counter+1

                    #------------------REACITONS---------------#

        else:
            await ctx.send(leng.nsern[a.get_lenguaje(ctx.message)])

#---------------------------------------------------------STOP----------------------------------------------------------#

    @commands.command(
        aliases=['s'],
        name='stop',
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
            await ctx.send(leng.neencdv[a.get_lenguaje(ctx.message)])
            status = False

        if(ctx.message.author.id in devusers):
            status = True

        if int(id) in servers_id and status == True:
            playlist = servers[servers_id.index(int(id))]
            vc = ctx.voice_client
            playlist["playlist"]["status"] = False
            vc.stop()

#---------------------------------------------------------PAUSE----------------------------------------------------------#

    @commands.command(
        aliases=['ps'],
        name='pause',
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
                await ctx.send(leng.neencdv[a.get_lenguaje(ctx.message)])
                status = False

            if(ctx.message.author.id in devusers):
                status = True

            if vc.is_paused() == True and status == True:
                await ctx.send(leng.eayep[a.get_lenguaje(ctx.message)])
            else:
                t = time.localtime()
                playlist["playlist"]["ptime"] = time.strftime("%H:%M:%S", t)
                vc.pause()
                embed = discord.Embed(
                    title=leng.pausado[a.get_lenguaje(ctx.message)], color=0x3498DB)
                await ctx.send(embed=embed)

#---------------------------------------------------------RESUME----------------------------------------------------------#

    @commands.command(
        aliases=['r'],
        name='resume',
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
                await ctx.send(leng.neencdv[a.get_lenguaje(ctx.message)])
                status = False

            if(ctx.message.author.id in devusers):
                status = True

            vc = ctx.voice_client
            if vc.is_paused() == True and status == True:
                vc.resume()
                embed = discord.Embed(
                    title=leng.resumido[a.get_lenguaje(ctx.message)], color=0x3498DB)
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
                await ctx.send(leng.eanep[a.get_lenguaje(ctx.message)])

#---------------------------------------------------------NEXT----------------------------------------------------------#

    @commands.command(
        aliases=['n', 'skip'],
        name='next',
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
            await ctx.send(leng.neencdv[a.get_lenguaje(ctx.message)])
            status = False

        if(ctx.message.author.id in devusers):
            status = True

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
                        await ctx.send(leng.cfdr[a.get_lenguaje(ctx.message)])
                else:
                    await ctx.send(leng.eenduc[a.get_lenguaje(ctx.message)])
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
            await ctx.send(leng.neencdv[a.get_lenguaje(ctx.message)])
            status = False

        if(ctx.message.author.id in devusers):
            status = True

        if int(id) in servers_id and status == True:
            playlist = servers[servers_id.index(int(id))]
            vc = ctx.voice_client

            if playlist["playlist"]["status"] == False:
                playlist["playlist"]["cplaying"] = playlist["playlist"]["cplaying"]-1
                await b.play(vc, ctx, self.bot)

            else:
                playlist["playlist"]["cplaying"] = playlist["playlist"]["cplaying"]-2
                vc.stop()

#---------------------------------------------------------SONG----------------------------------------------------------#

    @commands.command(
        name='song',
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
                title=leng.ar[a.get_lenguaje(ctx.message)], color=0x3498DB, description=str(index)+"- "+(str(names[index-1])))
            embed.set_footer(text=leng.duracion[a.get_lenguaje(
                ctx.message)]+str(lengths[index-1]))
            embed.set_footer(
                text=leng.tr[a.get_lenguaje(ctx.message)]+": "+time_left)
            await ctx.send(embed=embed)

#---------------------------------------------------------CLEAR----------------------------------------------------------#

    @commands.command(
        aliases=['c'],
        name='clear',
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
            await ctx.send(leng.neencdv[a.get_lenguaje(ctx.message)])
            status = False

        if(ctx.message.author.id in devusers):
            status = True

        if int(id) in servers_id and status == True:
            playlist = servers[servers_id.index(int(id))]
            playlist["playlist"]["status"] = False
            vc.stop()
            b.reset_all(ctx)

#---------------------------------------------------------REMOVE----------------------------------------------------------#

    @commands.command(
        aliases=['rm'],
        name='remove',
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
            await ctx.send(leng.neencdv[a.get_lenguaje(ctx.message)])
            status = False

        if(ctx.message.author.id in devusers):
            status = True

        if int(id) in servers_id and status == True:
            playlist = servers[servers_id.index(int(id))]
            if len(args) != 0:
                if args[0].isnumeric():
                    if int(args[0]) <= len(playlist["playlist"]["songs"]):

                        embed = discord.Embed(
                            title=leng.removido[a.get_lenguaje(ctx.message)], color=0x3498DB, description=str(playlist["playlist"]["songs"][int(args[0])-1]["name"]))
                        embed.set_footer(
                            text=leng.duracion[a.get_lenguaje(ctx.message)]+str(playlist["playlist"]["songs"][int(args[0])-1]["length"]))
                        await ctx.send(embed=embed)
                        deleted = int(args[0])-1

                        if(deleted == playlist["playlist"]["cplaying"]-1):
                            playlist["playlist"]["status"] = False
                            vc.stop()
                        playlist["playlist"]["songs"].pop(deleted)

                    else:
                        await ctx.send(leng.cfdr[a.get_lenguaje(ctx.message)])
                else:
                    if args[0] == "last":
                        embed = discord.Embed(
                            title=leng.removido[a.get_lenguaje(ctx.message)], color=0x3498DB, description=str(playlist["playlist"]["songs"][len(playlist["playlist"]["songs"])-1]["name"]))
                        embed.set_footer(
                            text=leng.duracion[a.get_lenguaje(ctx.message)]+str(playlist["playlist"]["songs"][len(playlist["playlist"]["songs"])-1]["length"]))
                        await ctx.send(embed=embed)

                        deleted = len(playlist["playlist"]["songs"])-1

                        if(deleted == playlist["playlist"]["cplaying"]-1):
                            playlist["playlist"]["status"] = False
                            vc.stop()
                        playlist["playlist"]["songs"].pop(deleted)
                    else:
                        await ctx.send(leng.eenduc[a.get_lenguaje(ctx.message)])
            else:
                await ctx.send(leng.eenducar[a.get_lenguaje(ctx.message)])

#---------------------------------------------------------MOVE----------------------------------------------------------#

    @commands.command(
        aliases=['m'],
        name='move',
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
            await ctx.send(leng.neencdv[a.get_lenguaje(ctx.message)])
            status = False

        if(ctx.message.author.id in devusers):
            status = True

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
                            await ctx.send(leng.eadmlc[a.get_lenguaje(ctx.message)])
                    else:
                        await ctx.send(leng.cfdr[a.get_lenguaje(ctx.message)])
                else:
                    await ctx.send(leng.eqcpmyadm[a.get_lenguaje(ctx.message)])
            else:
                await ctx.send(leng.ecyl[a.get_lenguaje(ctx.message)])

#---------------------------------------------------------LOOP----------------------------------------------------------#

    @commands.command(
        aliases=['lp'],
        name='loop',
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
                    description=leng.arlq_ca_d[a.get_lenguaje(ctx.message)][0], color=0x3498DB)
                await ctx.send(embed=embed)

            elif playlist["playlist"]["looping"] == 1:
                playlist["playlist"]["looping"] = 2
                embed = discord.Embed(
                    description=leng.arlq_ca_d[a.get_lenguaje(ctx.message)][1], color=0x3498DB)
                await ctx.send(embed=embed)

            elif playlist["playlist"]["looping"] == 2:
                playlist["playlist"]["looping"] = 0
                embed = discord.Embed(
                    description=leng.arlq_ca_d[a.get_lenguaje(ctx.message)][2], color=0x3498DB)
                await ctx.send(embed=embed)

#---------------------------------------------------------SHUFFLE----------------------------------------------------------#

    @commands.command(
        aliases=['sh'],
        name='shuffle',
    )
    async def shuffle(self, ctx):
        b.shuffler(ctx)
        await ctx.send(leng.mm[a.get_lenguaje(ctx.message)])

#---------------------------------------------------------LYRICS----------------------------------------------------------#

    @commands.command(
        aliases=['letra', 'lyr'],
        name='lyrics',
    )
    async def lyrics(self, ctx, *args):
        servers = b.get_servers()
        servers_id = b.get_servers_id()
        id = ctx.message.guild.id

        if(len(args) > 0):
            texto = ""
            for word in args:
                texto = (texto+" "+word)
            song = gn.search_song(texto)

        else:
            playlist = servers[servers_id.index(int(id))]
            index = playlist["playlist"]["cplaying"]
            song = gn.search_song(playlist["playlist"]["songs"][index-1]["name"])
        
        #find the embeded broken text at the end (fkin piece of shit)
        lyrics = song.lyrics
        x = lyrics.lower()
        x = x.rfind("embed")

        y=1
        while True:
            if(lyrics[x-y].isnumeric()):
                y=y+1
            else:
                break
        lyrics = lyrics[:x-y+1]
    
        #embed send
        if(len(lyrics) >= 6000):
            lyrics_pages=[]
            while True:
                if(len(lyrics) <= 4000):
                    lyrics_pages.append(lyrics)
                    break
                x = lyrics[:4000]
                x = x.rfind("\n")
                lyrics_pages.append(lyrics[:x])
                lyrics = lyrics[x:]
                await ctx.send(str(len(lyrics)))

        for lyrics in lyrics_pages:
            gembed = discord.Embed(title=song.title, color=0x3498DB, description=lyrics)
            gembed.set_thumbnail(url=song.header_image_url)
            await ctx.send(embed=gembed)


def setup(bot):
    bot.add_cog(music(bot))
