import discord
import time
import asyncio
import data
import random
import discord.utils
import lenguajes as leng
import m_queuer
import m_player
import yt_dlp
import datetime
import servermanager as s
from loguru import logger

a = data.datos()
q = m_queuer.queuer()
p = m_player.player()

sm = s.serverManager()

class musicManager:
    def __init__(self):
        status = False
        time = ""

#--------------MUSIC PLAYER---------------#
    async def play(self, vc, ctx, bot):
        id = ctx.message.guild.id
        msg_sent = False

        while True:  # comienza el loop de reproduccion
            if sm.exists(id):
                
                server = s.servers[sm.get_index(id)]
                server["status"] = True

                sm.apply()
    
                #--------------------------REPRODUCIENDO---------------------------#
                while True:  # si esta reproduciendo no hace nada y espera
                    if vc.is_playing() == False:
                        if vc.is_paused() == False:
                            break
                    await asyncio.sleep(0.25)
                #--------------------------REPRODUCIENDO---------------------------#

                if server["looping"] == 2:
                    server["cplaying"] = server["cplaying"]-1
                
                sm.apply()

                # si termina la queue frena el loop
                if server["cplaying"]+1 > len(server["songs"]) or server["status"] == False or sm.exists(id) == False:
                    if server["looping"] != 1 or sm.exists(id) == False:
                        server["status"] = False
                        server["cplaying"] = -1
                        sm.apply()
                        embed = discord.Embed(
                            title=leng.qo[a.get_lenguaje(ctx.message)], color=0x3498DB)
                        await ctx.send(embed=embed)
                        break
                    else:
                        server["cplaying"] = 0

                    #check if class is youtube or other and use correct function
                while True:
                    if(server["songs"][server["cplaying"]]["class"] == "yt"):
                        vid_thumbnail, url = await p.youtube_player(vc, id)
                        if(vid_thumbnail == 0 and url == 0):
                            await ctx.send("Video unavailable")
                            server["cplaying"] = server["cplaying"]+1  # sube el contador
                        else:
                            break

                    elif(server["songs"][server["cplaying"]]["class"] == "fl"):
                        vid_thumbnail = await p.file_player(vc, id)
                        url=None

                if(msg_sent == True):
                    if(discord.utils.get(bot.cached_messages, id=msg.id) != None):
                        await msg.delete()

                # if it is it should be delete
                embed = discord.Embed(
                    title=leng.ar[a.get_lenguaje(ctx.message)], color=0x3498DB, description=server["songs"][server["cplaying"]]["name"], url=url)

                if(vid_thumbnail!=0):
                    embed.set_image(url=vid_thumbnail)
                embed.set_footer(text=leng.posicion[a.get_lenguaje(ctx.message)]+": "+str(server["cplaying"]+1))

                # muestra que esta reproduciendo
                msg = await ctx.send(embed=embed)
                msg_sent = True
                server["cplaying"] = server["cplaying"]+1  # sube el contador
                t = time.localtime()
                server["time"] = time.strftime("%H:%M:%S", t)

                sm.apply()

#----------------SHUFFLER-----------------#

    def shuffler(self, ctx):
        id = ctx.message.guild.id

        if(sm.exists(id)):
            j = s.servers[sm.get_index(id)]

            final = []

            cplaying = j["cplaying"]
            y = range(0, cplaying)

            for n in y:
                final.append(j["songs"][n])

            out = j["songs"]
            for n in y:
                out.pop(0)
            random.shuffle(out)
            final += out

            j["songs"] = final
        
#--------------QUEUER---------------#
    async def queuer(self, ctx, request, type):
        if(type=="yt"):
            await q.youtube_queuer(ctx, request)
        elif(type=="fl"):
            msg = ctx.message
            for b in msg.attachments:
                url = b.url
            await q.file_queuer(ctx, url)

#-------------PRINT QUEUE--------------#

    def print_queue(self, playlist, arg, looping, ctx):

        if(looping != -1):
            vc = ctx.voice_client
            start_time = playlist["time"]
            cplaying = playlist["cplaying"]
            time_left = self.calculate_queue_time(start_time, playlist, cplaying, vc)
            Cpage = int((cplaying-1)/10)
        else:
            cplaying=-1
            Cpage=0

        counter=0
        pages=[]
        page=[]

        for j in playlist["songs"]:
            counter+=1
            page.append(j)
            if(counter == 10):
                pages.append(page)
                page=[]
                counter=0

        pages.append(page)
        logger.debug(str(arg)+ "page")
        
        if(arg <= len(pages) and arg != 0):
            Cpage=arg-1
        else:
            return 0
        
        if(arg==-1):
            Cpage=len(pages)-1

        text=''
        index=0+10*Cpage
        for song in pages[Cpage]:
            if(index+1 == cplaying):
                text+="**"+str(index+1)+") "+song["name"]+"** • *"+leng.tr[a.get_lenguaje(ctx.message)]+" "+time_left+"*\n"
            else:
                text+="**"+str(index+1)+")** "+song["name"]+" • *"+leng.duracion[a.get_lenguaje(ctx.message)]+": "+song["length"]+"*\n"
            index+=1
        embed = discord.Embed(title="**Queue**", color=0x3498DB, description=text)

        if(len(playlist["songs"])-(Cpage+1)*10 > 0 and looping != -1):
            embed.add_field(name="Songs left",value=str(len(playlist["songs"])-(Cpage+1)*10) ,inline=True)
        
        if(looping != 2 and looping != -1):
            embed.add_field(name="Looping",value=leng.arlq_ca_d[a.get_lenguaje(ctx.message)][looping], inline=True)
        embed.set_footer(text="Page: "+str(Cpage+1)+"/"+str(len(pages)))

        return embed  

#-------------VIDEO INFO--------------#

    async def get_video_info(self, id, ctx, *index):
        #gives currently playing video info
        #info to give:
        #name, author, length, url, views, thumbnail_link, codec, bitrate
        #if possible track release year album artist
        if(sm.exists(id)):
            j = s.servers[sm.get_index(id)]
            ydl_opts = {
                'quiet': False,
                'youtube_include_dash_manifest': False,
                'youtube_include_hls_manifest': False,
                'format': 'bestaudio'
            }
            yt = yt_dlp.YoutubeDL(ydl_opts)
            #if an index is given use that instead of the currently playing
            if(len(index) != 0):
                index = int(index[0])

                if(index <= len(j["songs"])):
                    video = yt.extract_info(j["songs"][index-1]["link"], download=False)
                else:
                    return leng.cfdr[a.get_lenguaje(ctx.message)]

            else:
                video = yt.extract_info(j["songs"][j["cplaying"]-1]["link"], download=False)
            
            final_text=''
            
            #convert time myself cuz datetime is a piece of crap fact
            date = "/"+video["upload_date"][0:4]
            date = "/"+video["upload_date"][4:6]+date
            date = video["upload_date"][6:]+date

            youtube_info="**Youtube Information**\n"
            youtube_info+="-**Title:** "+video["title"]+"\n"
            youtube_info+="-**Uploader:** "+video["uploader"]+"\n"
            youtube_info+="-**Views:** "+str(round(video["view_count"]/1000,1))+"K\n"
            youtube_info+="-**Length:** "+video["duration_string"]+"\n"
            youtube_info+="-**Likes:** "+str(round(video["like_count"]/1000,1))+"K\n"
            youtube_info+="-**Uploaded:** "+date+"\n"
            youtube_info+="-**Link:** "+video["webpage_url"]+"\n"
            youtube_info+="-**Channel Link:** "+video["channel_url"]+"\n"
            youtube_info+="-**Thumbnail:** "+video["thumbnail"]+"\n\n"
            final_text=youtube_info

            if("track" in video):
                music_info="**Music information**\n"
                music_info+="-**Track name:** "+video["track"]+"\n"
                music_info+="-**Artist:** "+video["artist"]+"\n"
                music_info+="-**Album:** "+video["album"]+"\n"
                if(video["release_year"] == None):
                    release_year="Unknown"
                else:
                    release_year=str(video["release_year"])
                music_info+="-**Release year:** "+release_year+"\n\n"
                final_text+=music_info

            file_info="**File information**\n"
            file_info+="-**Audio codec**: "+video["acodec"]+"\n"
            file_info+="-**Sample rate**: "+str(video["asr"]/1000)+"Khz\n"
            file_info+="-**Size**: "+str(round(video["filesize"]/1000000,2))+"MB\n"
            file_info+="-**Channels**: "+str(video["audio_channels"])+"\n"
            file_info+="-**Youtube format**: "+video["format"]+"\n"
            final_text+=file_info
            
            embed = discord.Embed(
               title="Video Information", color=0x3498DB, description=final_text)
            embed.set_thumbnail(url=video["thumbnail"])
            return embed

#-------------CALCULATE QUEUE TIME--------------#

    def calculate_queue_time(self, start_time, playlist, cplaying, vc):

        if(cplaying > len(playlist["songs"])-1):
            return "Done"
         
        x = time.strptime(start_time.split(',')[0], '%H:%M:%S')
        # convierte el timepo comienzo a segundos
        start_time = datetime.timedelta(
            hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()
        x = time.strptime(playlist["songs"][cplaying-1]["length"].split(',')[0], '%H:%M:%S')
        # lo mismo pero del largo del video
        length = datetime.timedelta(
            hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()
        # checkeea tiempo actual

        if(vc.is_paused() == True and playlist["status"] == True):
            x = time.strptime(
                playlist["ptime"].split(',')[0], '%H:%M:%S')
            current_time = datetime.timedelta(hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()
        else:
            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)
            x = time.strptime(current_time.split(',')[0], '%H:%M:%S')
            current_time = datetime.timedelta(hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec).total_seconds()
            
        time_elapsed = current_time - start_time  # resta los tiempos
        time_left = time.strftime("%H:%M:%S", time.gmtime(length-time_elapsed))

        return time_left
    
#-------------CONTROL CHECKER--------------#

class control_checker(discord.ui.View):
    def __init__(self, *, timeout=800, playlist, arg, looping, ctx):
        super().__init__(timeout=timeout)
        self.playlist = playlist
        self.arg = arg
        self.looping = looping
        self.ctx = ctx
        self.a = musicManager()

    @discord.ui.button(label="◄◄", style=discord.ButtonStyle.gray)
    async def start(self,interaction:discord.Interaction,button:discord.ui.Button):
        self.arg=1
        embed=self.a.print_queue(self.playlist, self.arg, self.looping, self.ctx)
        if(embed != 0):
            await interaction.response.edit_message(view=self, embed=embed)

    @discord.ui.button(label="◄", style=discord.ButtonStyle.gray)
    async def back(self,interaction:discord.Interaction,button:discord.ui.Button):
        self.arg=self.arg-1
        if(self.arg < 1):
            self.arg=1
        embed=self.a.print_queue(self.playlist, self.arg, self.looping, self.ctx)
        if(embed != 0):
            await interaction.response.edit_message(view=self, embed=embed)
    
    @discord.ui.button(label="►", style=discord.ButtonStyle.gray)
    async def forward(self,interaction:discord.Interaction,button:discord.ui.Button):
        self.arg=self.arg+1
        embed=self.a.print_queue(self.playlist, self.arg, self.looping, self.ctx)
        if(embed != 0):
            await interaction.response.edit_message(view=self, embed=embed)
    
    @discord.ui.button(label="►►", style=discord.ButtonStyle.gray)
    async def end(self,interaction:discord.Interaction,button:discord.ui.Button):
        self.arg=int(len(self.playlist["songs"])/10)+1
        embed=self.a.print_queue(self.playlist, self.arg, self.looping, self.ctx)
        if(embed != 0):
            await interaction.response.edit_message(view=self, embed=embed)