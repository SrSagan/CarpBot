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
                    vid_thumbnail = await p.youtube_player(index, vc, j)
                elif(j["playlist"]["songs"][index]["class"] == "fl"):
                    vid_thumbnail = await p.file_player(index, vc, j)

                if(msg_sent == True):
                    if(discord.utils.get(bot.cached_messages, id=msg.id) != None):
                        await msg.delete()

                # if it is it should be delete
                embed = discord.Embed(
                    title=leng.ar[a.get_lenguaje(ctx.message)], color=0x3498DB, description=str(j["playlist"]["songs"][index]["name"]))
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

                json_object = json.dumps(self.servers, indent=4)

                # Writing to sample.json
                with open("sample.json", "w") as outfile:
                    outfile.write(json_object)

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

            pressed = [0,0,0,0]
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
                
                j["playlist"]["pressed"]=pressed #los guarda

                if(1 in out): #envia las diferencias
                    return out

                await asyncio.sleep(1)
            return "no"