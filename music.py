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

#-----------------GENERAL-----------------#

    def reset_all(self, ctx):
        id = ctx.message.guild.id
        if int(id) in self.servers_id:
            self.servers.pop(self.servers_id.index(int(id)))
            self.servers_id.pop(self.servers_id.index(int(id)))

        self.write_json()

#--------------MUSIC PLAYER---------------#
    async def play(self, vc, ctx, bot):
        id = ctx.message.guild.id
        msg_sent = False
        while True:  # comienza el loop de reproduccion
            if int(id) in self.servers_id:
                
                j = self.servers[self.servers_id.index(int(id))]

                self.write_json()

                j["playlist"]["status"] = True
                if(self.get_oldindex(ctx)==self.get_index(ctx)):
                    vid_thumbnail, url = await self.nextSong(ctx, vc, j)  
                else:
                    vid_thumbnail, url = await self.playSong(ctx, vc, j)
                     
                self.set_oldindex(ctx, self.get_index(ctx))

                #check if the message was sent
                if(msg_sent == True):
                    if(discord.utils.get(bot.cached_messages, id=msg.id) != None):
                        await msg.delete() 
                
                if(url == None):
                    url = j["playlist"]["songs"][self.get_index(ctx)]["link"]
                
                # if it is it should be delete
                embed = discord.Embed(
                    title=leng.ar[a.get_lenguaje(ctx.message)], color=0x3498DB, description=j["playlist"]["songs"][self.get_index(ctx)]["name"], url=url)

                if(vid_thumbnail!=0):
                    embed.set_image(url=vid_thumbnail)
                embed.set_footer(text=leng.posicion[a.get_lenguaje(ctx.message)]+": "+str(self.get_index(ctx)+1))

                # muestra que esta reproduciendo
                msg = await ctx.send(embed=embed)
                msg_sent = True

                t = time.localtime()
                j["playlist"]["time"] = time.strftime("%H:%M:%S", t)
    
                #--------------------------REPRODUCIENDO---------------------------#
                while True:  # si esta reproduciendo no hace nada y espera
                    if vc.is_playing() == False:
                        if vc.is_paused() == False:
                            break
                    await asyncio.sleep(0.25)
                #--------------------------REPRODUCIENDO---------------------------#

                if j["playlist"]["looping"] == 2:
                    self.set_index(ctx, function="min")

                # si termina la queue frena el loop
                if self.get_index(ctx)+2 > len(j["playlist"]["songs"]) or j["playlist"]["status"] == False or int(id) not in self.servers_id:
                    if j["playlist"]["looping"] != 1 or int(id) not in self.servers_id:
                        j["playlist"]["status"] = False
                        embed = discord.Embed(
                            title=leng.qo[a.get_lenguaje(ctx.message)], color=0x3498DB)
                        await ctx.send(embed=embed)

                        self.write_json()

                        break
                    else:
                        self.set_index(ctx, 0)
                

                self.write_json()

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

            #gets the state and changes it
            state=prev_pressed[4]
            if(state==0):
                state=1
            else:
                state=0
            j["playlist"]["pressed"][4]=state
            j["playlist"]["pressed"][5]=message.id
            prev_pressed = prev_pressed[0:4]

            pressed = [0,0,0,0, state]
            out=[0,0,0,0]
            for i in range(0, 60): #timer de 1min
                
                if(message.id != j["playlist"]["pressed"][5]):
                    return "no"
                
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
                
                self.write_json()
                if(j["playlist"]["pressed"][4] != state and j["playlist"]["pressed"]["5"] != message.id):
                    return "no"
                else:
                    pressed[4:]=[state, message.id]
                    j["playlist"]["pressed"]=pressed #los guarda

                if(1 in out): #envia las diferencias
                    return out

                await asyncio.sleep(1)
            return "no"

#-------------GET INDEX--------------#
    def get_index(self, ctx):
        id = ctx.message.guild.id
        if int(id) in self.servers_id:
            j = self.servers[self.servers_id.index(int(id))]
 
            return j["playlist"]["cplaying"]
        else:
            return -1

#-------------SET INDEX--------------#
    def set_index(self, ctx, index=0, function=None):
        id = ctx.message.guild.id
        if int(id) in self.servers_id:
            j = self.servers[self.servers_id.index(int(id))]
            
            if(function == "sum"):
                j["playlist"]["cplaying"] =  self.get_index(ctx)+1
            elif(function == "min"):
                j["playlist"]["cplaying"] =  self.get_index(ctx)-1
            else:
                if(index != None):
                    j["playlist"]["cplaying"] = index
            
            self.write_json()

#-------------NEXT SONG--------------#
    async def nextSong(self, ctx, vc, j):
        self.set_index(ctx, function="sum")

        return await self.playSong(ctx, vc, j)

#-------------PLAY SONG--------------#
    async def playSong(self, ctx, vc, j):
        #check if class is youtube or other and use correct function
        if(j["playlist"]["songs"][self.get_index(ctx)]["class"] == "yt"):
            vid_thumbnail, url, index = await p.youtube_player(self.get_index(ctx), vc, j)
            
        elif(j["playlist"]["songs"][self.get_index(ctx)]["class"] == "fl"):
            vid_thumbnail, index = await p.file_player(self.get_index(ctx), vc, j)
            url=None
        
        return vid_thumbnail, url

#-------------GET OLDINDEX--------------#
    def get_oldindex(self, ctx):
        id = ctx.message.guild.id
        if int(id) in self.servers_id:
            j = self.servers[self.servers_id.index(int(id))]
 
            return j["playlist"]["oldindex"]
        else:
            return -1

#-------------SET INDEX--------------#
    def set_oldindex(self, ctx, index=0, function=None):
        id = ctx.message.guild.id
        if int(id) in self.servers_id:
            j = self.servers[self.servers_id.index(int(id))]
            
            if(function == "sum"):
                j["playlist"]["oldindex"] =  self.get_oldindex(ctx)+1
            elif(function == "min"):
                j["playlist"]["oldindex"] =  self.get_oldindex(ctx)-1
            else:
                if(index != None):
                    j["playlist"]["oldindex"] = index
            
            self.write_json()

#-------------WRITE JSON--------------#
    #TODO write constant updater of json :)
    def write_json(self):
        json_object = json.dumps(self.servers, indent=4)
        # Writing to sample.json
        with open("sample.json", "w") as outfile:
            outfile.write(json_object)