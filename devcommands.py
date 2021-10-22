import sys
import os

import discord
from discord.ext import commands
import data
from dotenv import load_dotenv

a = data.datos()

load_dotenv()
devuser = os.getenv('DEV_USER')  # checkea los los dev users
devuser2 = os.getenv('DEV_USER2')


class devcommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
#-----------------------DEBUG ARRAYS------------------------#

    @commands.command(  # comando debug arrays para mostrar el largo de todos los grupos
        aliases=["da"],
        name='debug_arrays',
        help="Muestra las arrays de links",
        brief="Muestra las arrays de links (solo devs)"

    )
    async def debug_arrays(self, ctx):
        a = data.datos()
        grupos = a.get_data()  # agarra la info
        print("debug_arrays usado")
        # checkea ke sea un dev el ke lo haya usado
        if ctx.message.author.id == int(devuser) or ctx.message.author.id == int(devuser2):
            for j in a.grupos:
                # imprime los datos en ds
                await ctx.send(str(j)+" array: "+str(len(grupos[j]["data"])))
        else:
            await ctx.send("Solo devs pueden usar este comando")

#-----------------------DEBUG IMAGES------------------------#

    @commands.command(  # muestra todas las img de X grupo
        aliases=["di"],
        name='debug_images',
        help="Muestra todas las imagenes guardadas",
        brief="Muestra todas las img (solo devs)"
    )
    async def debug_images(self, ctx, *arg):
        a = data.datos()
        grupos = a.get_data()
        print("debug_images usado")
        # checkeea ke sea un dev
        if ctx.message.author.id == int(devuser) or ctx.message.author.id == int(devuser2):
            for j in a.grupos:
                if arg[0] == grupos[j]["name"]:
                    for link in grupos[j]["data"]:
                        # imprime todas las img 1 a 1
                        await ctx.send(str(link))
        else:
            await ctx.send("Solo devs pueden usar este comando")

#-----------------------IP------------------------#

    @commands.command(  # Muestra la ip
        name='ip',
        help="Muestra la ip (solo devs)",
        brief="Muestra la ip (solo devs)"
    )
    async def ip(self, ctx):
        import subprocess
        print("ip usado")
        # checkeea ke sea un dev
        if ctx.message.author.id == int(devuser) or ctx.message.author.id == int(devuser2):
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

    @commands.command(
        aliases=["db"],
        name='debug',
        help='Comando debug',
        brief='Comando debug'
    )
    async def debug(self, ctx):
        user_input = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        await ctx.send(str(user_input))


def setup(bot):
    bot.add_cog(devcommands(bot))
