import discord
import time
import asyncio
import data
import json
import random
import discord.utils
import lenguajes as leng
import m_queuer
import m_player
import yt_dlp

a = data.datos()
q = m_queuer.queuer()
p = m_player.player()


class music:
    def __init__(self):
        status = False
        time = ""

        servers = []
        servers_id = []

        self.servers = servers
        self.servers_id = servers_id

        self.status = status
        self.time = time

#-----------------SERVERS-----------------#

    def get_servers(self):
        return self.servers

    def set_servers(self, servers):
        self.servers = servers

#----------------SERVERS_ID---------------#

    def get_servers_id(self):
        return self.servers_id

    def set_servers_id(self, servers_id):
        self.servers_id = servers_id

#-----------------RESET ALL-----------------#

    def reset_all(self, ctx):
        id = ctx.message.guild.id
        if int(id) in self.servers_id:
            self.servers.pop(self.servers_id.index(int(id)))
            self.servers_id.pop(self.servers_id.index(int(id)))

        json_object = json.dumps(self.servers, indent=4)

        # Writing to sample.json
        with open("sample.json", "w") as outfile:
            outfile.write(json_object)

#--------------MUSIC PLAYER---------------#
    async def play(self, vc, ctx, bot):
        id = ctx.message.guild.id
        msg_sent = False

        while True:  # comienza el loop de reproduccion
            if int(id) in self.servers_id:
                

                j = self.servers[self.servers_id.index(int(id))]
                j["playlist"]["status"] = True
                index = j["playlist"]["cplaying"]


                json_object = json.dumps(self.servers, indent=4)
                # Writing to sample.json
                with open("sample.json", "w") as outfile:
                    outfile.write(json_object)
    
                #--------------------------REPRODUCIENDO---------------------------#
                while True:  # si esta reproduciendo no hace nada y espera
                    if vc.is_playing() == False:
                        if vc.is_paused() == False:
                            break
                    await asyncio.sleep(0.25)
                #--------------------------REPRODUCIENDO---------------------------#

                index = j["playlist"]["cplaying"]
                if j["playlist"]["looping"] == 2:
                    index = index-1

                # si termina la queue frena el loop
                while True:
                    if j["playlist"]["cplaying"]+1 > len(j["playlist"]["songs"]) or j["playlist"]["status"] == False or int(id) not in self.servers_id:
                        if j["playlist"]["looping"] != 1 or int(id) not in self.servers_id:
                            j["playlist"]["status"] = False
                            embed = discord.Embed(
                                title=leng.qo[a.get_lenguaje(ctx.message)], color=0x3498DB)
                            await ctx.send(embed=embed)

                            json_object = json.dumps(self.servers, indent=4)
                            # Writing to sample.json
                            with open("sample.json", "w") as outfile:
                                outfile.write(json_object)

                            break
                        else:
                            j["playlist"]["cplaying"] = 0
                            index = 0

                    #check if class is youtube or other and use correct function
                    if(j["playlist"]["songs"][index]["class"] == "yt"):
                        vid_thumbnail, url = await p.youtube_player(index, vc, j)
                        if(vid_thumbnail == 0 and url == 0):
                            await ctx.send("Video unavailable")
                            index = index+1  # sube el contador
                            j["playlist"]["cplaying"] = index
                        else:
                            break

                    elif(j["playlist"]["songs"][index]["class"] == "fl"):
                        vid_thumbnail = await p.file_player(index, vc, j)
                        url=None

                if(msg_sent == True):
                    if(discord.utils.get(bot.cached_messages, id=msg.id) != None):
                        await msg.delete()

                # if it is it should be delete
                embed = discord.Embed(
                    title=leng.ar[a.get_lenguaje(ctx.message)], color=0x3498DB, description=j["playlist"]["songs"][index]["name"], url=url)

                if(vid_thumbnail!=0):
                    embed.set_image(url=vid_thumbnail)
                embed.set_footer(text=leng.posicion[a.get_lenguaje(ctx.message)]+": "+str(index+1))

                # muestra que esta reproduciendo
                msg = await ctx.send(embed=embed)
                msg_sent = True
                index = index+1  # sube el contador
                j["playlist"]["cplaying"] = index
                t = time.localtime()
                j["playlist"]["time"] = time.strftime("%H:%M:%S", t)

                a.write_json(self.servers, "servers")

#----------------SHUFFLER-----------------#

    def shuffler(self, ctx):
        id = ctx.message.guild.id

        if int(id) in self.servers_id:
            j = self.servers[self.servers_id.index(int(id))]

            final = []

            cplaying = j["playlist"]["cplaying"]
            y = range(0, cplaying)

            for n in y:
                final.append(j["playlist"]["songs"][n])

            out = j["playlist"]["songs"]
            for n in y:
                out.pop(0)
            random.shuffle(out)
            final += out

            j["playlist"]["songs"] = final

#--------------QUEUER---------------#
    async def queuer(self, ctx, request, type):
        if(type=="yt"):
            self.servers_id, self.servers = await q.youtube_queuer(ctx, request, self.servers_id, self.servers)
        elif(type=="fl"):
            msg = ctx.message
            for b in msg.attachments:
                url = b.url
            self.servers_id, self.servers = await q.file_queuer(ctx, url, self.servers_id, self.servers)

#-------------QUEUE CONTROLS--------------#

    async def control_checker(self, message, controls, bot, ctx):
        #QUE VIJA X DIOSSS
        id = ctx.message.guild.id #agarra todo lo necesario
        if(id in self.servers_id):
            j = self.servers[self.servers_id.index(int(id))]
            prev_pressed = j["playlist"]["pressed"]

            state=prev_pressed[4]
            if(state==0):
                state=1
            else:
                state=0
            j["playlist"]["pressed"][4]=state
            prev_pressed = prev_pressed[0:3]

            pressed = [0,0,0,0, state]
            out=[0,0,0,0]
            for i in range(0, 60): #timer de 1min

                cache_msg = discord.utils.get(bot.cached_messages, id=message.id) #hace todo un tema con cached messages pq ds es una vija y no retorna los msg al toque
                reactions = cache_msg.reactions

                for emoji in controls:
                    reaction = discord.utils.get(reactions, emoji=emoji)
                    pressed[controls.index(emoji)]=reaction.count #los cuenta

                counter=0 #los compara
                for press in prev_pressed:
                    if(press == pressed[counter]):
                        out[counter]=0
                    else:
                        out[counter]=1
                    counter=counter+1
                if(j["playlist"]["pressed"][4] == state):
                    pressed[4]=state
                    j["playlist"]["pressed"]=pressed #los guarda
                else:
                    return "no"

                if(1 in out): #envia las diferencias
                    return out

                await asyncio.sleep(1)
            return "no"

#-------------VIDEO INFO--------------#

    async def get_video_info(self, id, ctx, *index):
        #gives currently playing video info
        #info to give:
        #name, author, length, url, views, thumbnail_link, codec, bitrate
        #if possible track release year album artist
        if int(id) in self.servers_id:
            j = self.servers[self.servers_id.index(int(id))]
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

                if(index <= len(j["playlist"]["songs"])):
                    video = yt.extract_info(j["playlist"]["songs"][index-1]["link"], download=False)
                else:
                    return leng.cfdr[a.get_lenguaje(ctx.message)]

            else:
                video = yt.extract_info(j["playlist"]["songs"][j["playlist"]["cplaying"]-1]["link"], download=False)
            
            final_text=''
            
            #convert time myself cuz datetime is a piece of crap fact
            date = "/"+video["upload_date"][0:4]
            date = "/"+video["upload_date"][4:6]+date
            date = video["upload_date"][6:8]+date

            youtube_info="**Youtube Information**\n"
            youtube_info+="-**Title:** "+video["fulltitle"]+"\n"
            youtube_info+="-**Uploader:** "+video["uploader"]+"\n"
            youtube_info+="-**Views:** "+str(video["view_count"])+"\n"
            youtube_info+="-**Length:** "+video["duration_string"]+"\n"
            youtube_info+="-**Likes:** "+str(video["like_count"])+"\n"
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
                    release_year=video["release_year"]
                music_info+="-**Release year:** "+release_year+"\n\n"
                final_text+=music_info

            file_info="**File information**\n"
            file_info+="-**Audio codec**: "+video["acodec"]+"\n"
            file_info+="-**Sample rate**: "+str(video["asr"]/1000)+"Khz\n"
            file_info+="-**Size**: "+str(video["filesize"]/1000000)+"MB\n"
            file_info+="-**Channels**: "+str(video["audio_channels"])+"\n"
            file_info+="-**Youtube format**: "+video["format"]+"\n"
            final_text+=file_info
            
            embed = discord.Embed(
               title="Video Information", color=0x3498DB, description=final_text, )
            embed.set_thumbnail(url=video["thumbnail"])
            return embed

