import sys
import os

import discord
from discord.ext import commands
import data
from dotenv import load_dotenv
import lenguajes as leng

a = data.datos()

devusers=[]
load_dotenv()
dev = os.getenv('DEV_USERS')  # checkea los los dev users

while True:
    x = dev.find(",")
    if(x==-1):
        devusers.append(int(dev))
        print(devusers)
        break
    devusers.append(int(dev[:x]))
    dev = dev[x+1:]



class devcommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

#-----------------------DEBUG IMAGES------------------------#

    @commands.command(  # muestra todas las img de X grupo
        aliases=["di"],
        name='debug_images',
    )
    async def debug_images(self, ctx, *arg):
        grupos = a.get_data()
        print("debug_images usado")
        # checkeea ke sea un dev
        if(ctx.message.author.id in devusers):
            for j in a.grupos:
                if arg[0] == grupos[j]["name"]:
                    for link in grupos[j]["data"]:
                        # imprime todas las img 1 a 1
                        await ctx.send(str(link))
        else:
            await ctx.send(leng.sdpuec[a.get_lenguaje(ctx.message)])

#-----------------------IP------------------------#

    @commands.command(  # Muestra la ip
        name='ip',
    )
    async def ip(self, ctx):
        import subprocess
        print("ip usado")
        # checkeea ke sea un dev
        if(ctx.message.author.id in devusers):
            # se usa este comando para averiguar la ip
            command = "dig +short myip.opendns.com @resolver1.opendns.com"
            # se lee la salida del comando
            subprocess = subprocess.Popen(
                command, shell=True, stdout=subprocess.PIPE)
            ip = subprocess.stdout.read()
            ip = str(ip)
            x = ip.find("'")
            y = ip.find("\\")
            ip = ip[x+1:y]
            await ctx.send("IP:"+str(ip))
        else:
            await ctx.send("Solo devs pueden usar este comando")

def setup(bot):
    bot.add_cog(devcommands(bot))
