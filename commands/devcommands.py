import sys
import os

import discord
from discord.ext import commands
import data
from dotenv import load_dotenv
import lenguajes as leng
import yt_dlp
#from discord_components import DiscordComponents, DiscordButton, Button

a = data.datos()

devusers=[]
load_dotenv()
dev = os.getenv('DEV_USERS')  # checkea los los dev users

while True:
    x = dev.find(",")
    if(x==-1):
        devusers.append(int(dev))
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
            for j in grupos:
                if arg[0] == j["name"]:
                    for link in j["data"]:
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

#-----------------------DEBUG------------------------#

    @commands.command(  # DEBUG
        name='debug',
        )
    async def debug(self, ctx, *args):
        # checkeea ke sea un dev
        if(ctx.message.author.id in devusers):
            await ctx.send("'-'",view=control_checker())

async def setup(bot):
    await bot.add_cog(devcommands(bot))

class control_checker(discord.ui.View):
    def __init__(self, *, timeout=800):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="◄◄", style=discord.ButtonStyle.gray)
    async def start(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.edit_message(content=f"This is an edited button response!")

    @discord.ui.button(label="◄", style=discord.ButtonStyle.gray)
    async def back(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.edit_message(content=f"This is an edited button response!")
    
    @discord.ui.button(label="►", style=discord.ButtonStyle.gray)
    async def forward(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.edit_message(content=f"This is an edited button response!")
    
    @discord.ui.button(label="►►", style=discord.ButtonStyle.gray)
    async def end(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response
        print("Test")