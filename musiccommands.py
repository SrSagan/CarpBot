import os

import discord
from discord.ext import commands
import data
import music as f
import datetime
import time
from dotenv import load_dotenv
import lenguajes as leng
from lyricsgenius import Genius
import servermanager as s
import m_queuer
from loguru import logger

a = data.datos()
b = f.musicManager()
c = m_queuer.queuer()
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

sm = s.serverManager()

class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        

#---------------------------------------------------------LEAVE----------------------------------------------------------#


    @commands.command(
        aliases=['l', 'lv', 'fuckoff'],
        name='leave',
    )
    async def leave(self, ctx):
        logger.debug("Leave runned")
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
            sm.clear(ctx.message.guild.id)
            await ctx.voice_client.disconnect()

#-----------------------------------------------------estrelheinhas--------------------------------------------------------------#

    @commands.command(pass_context=True,  #a command for the one no longer with us to remember her as she will always be in my heart
                      aliases=['es', 'juli'],#she came back lmao
                      name='estrelheinhas',
                      )
    async def estrelheinhas(self, ctx):
        voice_client = discord.utils.get(
                ctx.bot.voice_clients, guild=ctx.guild)
        author = ctx.message.author
        try:
            channel = author.voice.channel
            status = True
        except:
            status = False
        if(ctx.message.author.id in devusers):
            status = True
            
        if voice_client != None:

            await b.queuer(ctx, "https://www.youtube.com/playlist?list=PLT5RzA2p1DMdJSacPMujx1qaFXqMgxnHe", "yt")
            vc = ctx.voice_client  # si no esta reproduciendo, comienza a reproducir
            if vc.is_playing() == False:
                 await b.play(vc, ctx, self.bot)

        elif status == True:
            await b.queuer(ctx, "https://www.youtube.com/playlist?list=PLT5RzA2p1DMdJSacPMujx1qaFXqMgxnHe", "yt")
                 
            await channel.connect()
            vc = ctx.voice_client
            if vc.is_playing() == False:  # si no esta reproduciendo comienza a reproducir (no hace falta pero weno)
                await b.play(vc, ctx, self.bot)
            #to conmemorate the only person who truly changed me

#---------------------------------------------------------PLAY----------------------------------------------------------#

    @commands.command(pass_context=True,  # reproduce musica
                      aliases=['p', 'pl'],
                      name='play',
                      )
    async def play(self, ctx, *request):
        id = ctx.message.guild.id
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
                    server = s.servers[sm.get_index(id)]
                    if(server["cplaying"] == -1):
                        server["cplaying"] = len(server["songs"])-1
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
    async def queue(self, ctx, *args):
        logger.debug("Queue runned")
        id = ctx.message.guild.id
        
        #paginas
        # [
        #   [
            # nombre
            # len
        #   ]
        # ]

        #complete re work:
        #create a page system that divides the whole playlist into pages of 10, the last page will have less songs if necessary, none of them will have more
        #once the page is done it's saved and only changed if something changed the playlist

        if(sm.exists(id)):
            playlist = s.servers[sm.get_index(id)]
            looping = playlist["looping"]

            #correct looping
            if(looping == 0):
                looping=2
            elif(looping == 1):
                looping=0
            elif(looping == 2):
                looping=1
            
            arg=int((playlist["cplaying"]-1)/10)+1
            if(arg < 1):
                arg=1
            if(playlist["cplaying"] > len(playlist["songs"])-1):
                arg=-1


            if(len(args) != 0):
                print(len(args))
                if(args[0].isnumeric()):
                    arg = int(args[0])

            embed = b.print_queue(playlist, arg, looping, ctx)
            if(embed != 0):
                await ctx.send(embed=embed, view=f.control_checker(playlist=playlist, arg=arg, looping=looping, ctx=ctx))
            else:
                await ctx.send("Page out of range")

#---------------------------------------------------------STOP----------------------------------------------------------#

    @commands.command(
        aliases=['s'],
        name='stop',
    )
    async def stop(self, ctx):
        # chekear si el client esta en canal de voz sino no usar done
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

        if sm.exists(id) and status == True:
            playlist = playlist = s.servers[sm.get_index(id)]
            vc = ctx.voice_client
            playlist["status"] = False
            vc.stop()
            sm.apply()

#---------------------------------------------------------PAUSE----------------------------------------------------------#

    @commands.command(
        aliases=['ps'],
        name='pause',
    )
    async def pause(self, ctx):
        # chekear si el client esta en canal de voz sino no usar
        vc = ctx.voice_client
        author = ctx.message.author
        id = ctx.message.guild.id

        if(sm.exists(id)):
            playlist = playlist = s.servers[sm.get_index(id)]
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
                playlist["ptime"] = time.strftime("%H:%M:%S", t)
                vc.pause()
                embed = discord.Embed(
                    title=leng.pausado[a.get_lenguaje(ctx.message)], color=0x3498DB)
                await ctx.send(embed=embed)
            sm.apply()

#---------------------------------------------------------RESUME----------------------------------------------------------#

    @commands.command(
        aliases=['r'],
        name='resume',
    )
    async def resume(self, ctx):
        # chekear si el client esta en canal de voz sino no usar
        author = ctx.message.author
        id = ctx.message.guild.id
        if(sm.exists(id)):
            playlist = s.servers[sm.get_index(id)]

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
                    playlist["time"].split(',')[0], '%H:%M:%S')
                tiempo = datetime.timedelta(
                    hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()

                x = time.strptime(
                    playlist["ptime"].split(',')[0], '%H:%M:%S')
                ptime = datetime.timedelta(
                    hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()

                time_paused = resume_time-ptime
                playlist["time"] = time.strftime("%H:%M:%S", time.gmtime(
                    tiempo+time_paused))

            else:
                await ctx.send(leng.eanep[a.get_lenguaje(ctx.message)])
            sm.apply()

#---------------------------------------------------------NEXT----------------------------------------------------------#

    @commands.command(
        aliases=['n', 'skip'],
        name='next',
    )
    async def next(self, ctx, *args):
        # chekear si el client esta en canal de voz sino no usar
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

        if sm.exists(id) and status == True:

            playlist = s.servers[sm.get_index(id)]
            songs = playlist["songs"]
            vc = ctx.voice_client

            if len(args) != 0:
                if args[0].isnumeric():
                    if int(args[0]) <= len(songs) and int(args[0]) > 0:
                        index = int(args[0])-1
                        playlist["cplaying"] = index
                        vc.stop()
                    else:
                        await ctx.send(leng.cfdr[a.get_lenguaje(ctx.message)])
                else:
                    await ctx.send(leng.eenduc[a.get_lenguaje(ctx.message)])
            else:
                if playlist["looping"] == 2:
                    playlist["cplaying"] = playlist["cplaying"]+1
                    vc.stop()
                else:
                    vc.stop()
            sm.apply()

#---------------------------------------------------------BACK----------------------------------------------------------#

    @commands.command(
        aliases=['b'],
        name='back',
    )
    async def back(self, ctx):
        # chekear si el client esta en canal de voz sino no usar
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

        if sm.exists(id) and status == True:
            playlist = s.servers[sm.get_index(id)]
            vc = ctx.voice_client

            if playlist["status"] == False and playlist["cplaying"] == -1:
                playlist["cplaying"] = len(playlist["songs"])-1
                await b.play(vc, ctx, self.bot)

            else:
                playlist["cplaying"] = playlist["cplaying"]-2
                vc.stop()
            sm.apply()

#---------------------------------------------------------SONG----------------------------------------------------------#

    @commands.command(
        name='song',
    )
    async def song(self, ctx):
        id = ctx.message.guild.id
        vc = ctx.voice_client

        if(sm.exists(id)):
            playlist = s.servers[sm.get_index(id)]
            if(playlist["cplaying"] != -1):
                start_time = playlist["time"]
                lengths = []
                names = []
                index = playlist["cplaying"]
                for j in playlist["songs"]:
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
    
                if vc.is_paused() == True and playlist["status"] == True:
                    x = time.strptime(
                        playlist["ptime"].split(',')[0], '%H:%M:%S')
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
                sm.apply()

#---------------------------------------------------------CLEAR----------------------------------------------------------#

    @commands.command(
        aliases=['c'],
        name='clear',
    )
    async def clear(self, ctx):
        vc = ctx.voice_client
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

        if(sm.exists(id)):
            vc.stop()
            sm.clear(id)
            await ctx.send(leng.pv[a.get_lenguaje(ctx.message)])

#---------------------------------------------------------REMOVE----------------------------------------------------------#

    @commands.command(
        aliases=['rm'],
        name='remove',
    )
    async def remove(self, ctx, *args):
        vc = ctx.voice_client
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

        if sm.exists(id) and status == True:
            playlist = s.servers[sm.get_index(id)]
            if len(args) != 0:
                if args[0].isnumeric():
                    if int(args[0]) <= len(playlist["songs"]):

                        embed = discord.Embed(
                            title=leng.removido[a.get_lenguaje(ctx.message)], color=0x3498DB, description=str(playlist["songs"][int(args[0])-1]["name"]))
                        embed.set_footer(
                            text=leng.duracion[a.get_lenguaje(ctx.message)]+str(playlist["songs"][int(args[0])-1]["length"]))
                        await ctx.send(embed=embed)
                        deleted = int(args[0])-1
                    else:
                        await ctx.send(leng.cfdr[a.get_lenguaje(ctx.message)])
                else:
                    if args[0] == "last":
                        embed = discord.Embed(
                            title=leng.removido[a.get_lenguaje(ctx.message)], color=0x3498DB, description=str(playlist["songs"][len(playlist["songs"])-1]["name"]))
                        embed.set_footer(
                            text=leng.duracion[a.get_lenguaje(ctx.message)]+str(playlist["songs"][len(playlist["songs"])-1]["length"]))
                        await ctx.send(embed=embed)

                        deleted = len(playlist["songs"])-1
                    else:
                        await ctx.send(leng.eenduc[a.get_lenguaje(ctx.message)])
                    
                playlist["songs"].pop(deleted)

                if(deleted == playlist["cplaying"]-1):
                    if(deleted == len(playlist["songs"])): #si es la ultima cancion de la playlist vuelve una para atras
                        await self.back(ctx)
                    else:
                        vc.stop() #sino reproduce la siguiente
                        playlist["cplaying"] = playlist["cplaying"]-1 #la siguiente cambia a ser la que estabamos reproduciendo 
                        #ya que se shiftea toda la playlist
                
                if(deleted < playlist["cplaying"]):
                    playlist["cplaying"]-= 1

            else:
                await ctx.send(leng.eenducar[a.get_lenguaje(ctx.message)])
            sm.apply()

#---------------------------------------------------------MOVE----------------------------------------------------------#

    @commands.command(
        aliases=['m'],
        name='move',
    )
    async def move(self, ctx, *args):
        vc = ctx.voice_client
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

        if sm.exists(id) and status == True:
            playlist = s.servers[sm.get_index(id)]
            if len(args) > 0:
                if args[0].isnumeric():
                    if int(args[0]) <= len(playlist["songs"]) and int(args[1]) <= len(playlist["songs"]):
                        moving_song = playlist["songs"][int(
                            args[0])-1]
                        if args[1].isnumeric():
                            playlist["songs"].pop(int(args[0])-1)
                            playlist["songs"].insert(int(args[1])-1, moving_song)

                            if(int(args[1]) <= playlist["cplaying"]):
                                playlist["cplaying"] = playlist["cplaying"]+1

                            embed = discord.Embed(title="Song moved", color=0x3498DB, description=str(
                                playlist["songs"][int(args[1])-1]["name"])+" moved to position "+str(args[1]))
                            await ctx.send(embed=embed)

                        else:
                            await ctx.send(leng.eadmlc[a.get_lenguaje(ctx.message)])
                    else:
                        await ctx.send(leng.cfdr[a.get_lenguaje(ctx.message)])
                else:
                    await ctx.send(leng.eqcpmyadm[a.get_lenguaje(ctx.message)])
            else:
                await ctx.send(leng.ecyl[a.get_lenguaje(ctx.message)])
            sm.apply()

#---------------------------------------------------------LOOP----------------------------------------------------------#

    @commands.command(
        aliases=['lup'],
        name='loop',
    )
    async def loop(self, ctx, *args):
        vc = ctx.voice_client
        id = ctx.message.guild.id

        if(sm.exists(id)):
            playlist = s.servers[sm.get_index(id)]

            if playlist["looping"] == 0:
                playlist["looping"] = 1
                embed = discord.Embed(
                    description=leng.arlq_ca_d[a.get_lenguaje(ctx.message)][0], color=0x3498DB)
                await ctx.send(embed=embed)

            elif playlist["looping"] == 1:
                playlist["looping"] = 2
                embed = discord.Embed(
                    description=leng.arlq_ca_d[a.get_lenguaje(ctx.message)][1], color=0x3498DB)
                await ctx.send(embed=embed)

            elif playlist["looping"] == 2:
                playlist["looping"] = 0
                embed = discord.Embed(
                    description=leng.arlq_ca_d[a.get_lenguaje(ctx.message)][2], color=0x3498DB)
                await ctx.send(embed=embed)
            sm.apply()

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
        #TODO: Give a list of pages of lyrics and make the user select before spamming the whole freaking chat with scott pirigrim movie
        id = ctx.message.guild.id

        if(len(args) > 0):
            texto = ""
            for word in args:
                texto = (texto+" "+word)
            songs = gn.search_songs(texto)  #find a way to search more than 10 songs

        else:
            playlist = s.servers[sm.get_index(id)]
            index = playlist["cplaying"]
            songs = gn.search_songs(playlist["songs"][index-1]["name"])

        songs = songs["hits"]
        out=[]
        for song in songs:
            song={
            "name":song["result"]["title"],
            "artist":song["result"]["primary_artist"]["name"],
            "id":song["result"]["id"]
            }
            out.append(song)
        
        #make pages of 5 songs each and make them control with (n)ext (p)revious (c)ancel
        #somehow add a timer of one minute after last action after which it stops checking
        embed = discord.Embed(title="Results", color=0x3498DB, description="Select a result")
        position=1#redraw menu or edit? new numbers or same 5? 
        for song in out:
            value="**Name:** "+song["name"]+"\n"+"**Arist:** "+song["artist"]
            embed.add_field(name=str(position), value=value, inline=False)
            position=position+1

        await ctx.send(embed=embed)

        msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if(msg.content.lower() == 'cancel'): #also check for previous next and cancel and inform of each one
                return 0

        msg = msg.content
        tabla=[1,2,3,4,5,6,7,8,10]
        if msg.isnumeric():
            msg=int(msg)
            for num in tabla:
                if(msg == num):
                    song = gn.search_song(song_id=out[tabla.index(num)]["id"])


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
        lyrics_pages=[]
        while True:
            if(len(lyrics) <= 4000):
                lyrics_pages.append(lyrics)
                break
            x = lyrics[:4000]
            x = x.rfind("\n")
            lyrics_pages.append(lyrics[:x])
            lyrics = lyrics[x:]

        for lyrics in lyrics_pages:
            gembed = discord.Embed(title=song.title, color=0x3498DB, description=lyrics)
            gembed.set_thumbnail(url=song.header_image_url)
            await ctx.send(embed=gembed)

#---------------------------------------------------------VIDEO INFO----------------------------------------------------------#

    @commands.command(
        aliases=['vi', 'vinf'],
        name='videoinfo',
    )
    async def videoinfo(self, ctx, *args):
        print("videoinfo usado")
        id = ctx.message.guild.id

        if(len(args) != 0):
            if(args[0].isnumeric()):
                embed = await b.get_video_info(id, ctx, args[0])
            else:
                leng.eenduc[a.get_lenguaje(ctx.message)]
        else:
            embed = await b.get_video_info(id, ctx)
        if(type(embed) == str):
            await ctx.send(embed)
        else:
            await ctx.send(embed=embed)

#---------------------------------------------------------SAVE PLAYLIST----------------------------------------------------------#

    @commands.command(
        aliases=["svp"],
        name="save_playlist"
    )
    async def save_playlist(self, ctx, *args):
        id = ctx.message.guild.id
        userid = ctx.message.author.id

        if(sm.exists(id)):

            if(len(args) != 0):
                name=''
                for arg in args:
                    if(args.index(arg) == len(args)-1): #saves name
                        name+=arg
                    else:
                        name+=arg+" "

                work = sm.save_playlist(id, userid, name) #saves file

                if(work == 0): #answers accordingly
                    await ctx.send("You don't have playlist left")
                elif(work == 2): 
                    await ctx.send("A playlist with name "+name+" already exists")
                else:
                    await ctx.send("Playlist added")
            else:
                await ctx.send("Specify playlist name eg: \"sp playlist name")

#---------------------------------------------------------LOAD PLAYLIST----------------------------------------------------------#

    @commands.command(
        aliases=["lp", "ldp"],
        name="load_playlist"
    )
    async def load_playlist(self, ctx, *args):
        #TODO if it's alr in vc it doesn't start playing (make it start playing :gun:)
        id = ctx.message.guild.id
        userid = ctx.message.author.id
        work=2
        author = ctx.message.author
        try:
            channel = author.voice.channel
            status=True
        except:
            status=False

        voice_client = discord.utils.get(
                ctx.bot.voice_clients, guild=ctx.guild)
        
        
        if(len(args) != 0):
            name=''
            for arg in args:
                if(args.index(arg) == len(args)-1): #saves name
                    name+=arg
                else:
                    name+=arg+" "
            while work == 2:
                work = sm.load_playlist(id, userid, name) #saves file
                print(isinstance(work, list))

                if(isinstance(work, list)):
                    await c.queuer(work, id)
                    await ctx.send("Playlist queued")
                    if(status):
                        await channel.connect()
                        vc = ctx.voice_client
                        await b.play(vc, ctx, self.bot)

                if voice_client != None:
                    vc = ctx.voice_client  # si no esta reproduciendo, comienza a reproducir
                    if vc.is_playing() == False:
                        await b.play(vc, ctx, self.bot)

                        
                elif(work == 0): #answers accordingly
                    await ctx.send("The specified playlist doesn't exist")
                elif(work == 1):
                    await ctx.send("Playlist queued")
        else:
            await ctx.send("Specify playlist name eg: \"sp playlist name")

#---------------------------------------------------------SHOW PLAYLIST----------------------------------------------------------#
    @commands.command(
        aliases=["sp", "shp"],
        name="show_playlist"
    )
    async def show_playlist(self, ctx, *args):
        userid = ctx.message.author.id

        playlists = sm.show_playlist(userid)

        if(playlists == 0):
            await ctx.send("No playlist saved with this user")
            return 0
        
        if(len(args) > 0):
            for playlist in playlists:
                if(playlist["name"] == args[0]):
                    embed = b.print_queue(playlist, 1, -1, ctx)
            await ctx.send(embed=embed, view=f.control_checker(playlist=playlist, arg=1, looping=-1, ctx=ctx))

        else:
            text=''
            for playlist in playlists:
                text+="**"+playlist["name"]+"**\n"
                text+=str(len(playlist["songs"]))+" songs\n"
                embed = discord.Embed(title="Playlists:", color=0x3498DB, description=text)
            await ctx.send(embed=embed)

#---------------------------------------------------------REMOVE PLAYLIST----------------------------------------------------------#

    @commands.command(
            aliases=["rp","rmpl"],
            name="remove_playlist"
    )
    async def remove_playlist(self, ctx, *args):
        userid = ctx.message.author.id
        playlists = sm.show_playlist(userid)

        if(playlists == 0):
            await ctx.send("No playlist saved with this user")
            return 0
        
        if(len(args) > 0):
            found = sm.remove_playlist(userid, args[0])
        
        if(found == 0):
            await ctx.send("No playlist has that name")
        else:
            await ctx.send("Playlist "+args[0]+" removida")
                    
#---------------------------------------------------------SEARCH----------------------------------------------------------#

    @commands.command(
        aliases=["sr", "srch"],
        name="search"
    )
    async def search(self, ctx, *args):
        id = ctx.message.guild.id

        if(len(args) != 0):
            if(sm.exists(id)):
                playlist = s.servers[sm.get_index(id)]
                arg = args[0].lower()
                counter=0
                text=""
                for song in playlist["songs"]:
                    name = song["name"].lower()
                    if(name.find(arg) != -1):
                        text = text+"\n**"+str(playlist["songs"].index(song)+1)+")** " +str(song["name"])+" *"+leng.duracion[a.get_lenguaje(ctx.message)]+": "+str(song["length"])+"*"
                        counter+=1
                    if(counter == 10):
                        break
                
                if(len(text) > 0):
                    embed = discord.Embed(
                        title="Found", color=0x3498DB, description=text)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("Nothing found")
        else:
            await ctx.send("Type something to search")
                    
async def setup(bot):
    await bot.add_cog(music(bot))
