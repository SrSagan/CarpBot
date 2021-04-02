import os

import discord
from discord.ext import commands
import data
from dotenv import load_dotenv

a = data.datos()


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
devuser = os.getenv('DEV_USER')
devuser2 = os.getenv('DEV_USER2')

class devcommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(
	 aliases=["da"],
	 name='debug_arrays',
	 help="Muestra las arrays de links",
	 brief="Muestra las arrays de links (solo devs)"
	) 

    async def debug_arrays(self, ctx):
        a = data.datos()
        print("debug_arrays usado")
        if ctx.message.author.id == int(devuser) or int(devuser2):
        	for j in a.grupos:
        		await ctx.send(str(j)+" array: "+str(len(a.grupos[j]["data"])))
        else:
        	await ctx.send("Solo devs pueden usar este comando")

    @commands.command(
	aliases=["di"],
	name='debug_images',
	help="Muestra todas las imagenes guardadas",
	brief="Muestra todas las img (solo devs)"
	)
    async def debug_images(self, ctx, *arg):
        a = data.datos()
        print("debug_images usado")
        if ctx.message.author.id == int(devuser) or int(devuser2):
        	for j in a.grupos:
        		if arg[0] == a.grupos[j]["name"]:
        			for link in a.grupos[j]["data"]:
        				await ctx.send(str(link))
        else:
        	await ctx.send("Solo devs pueden usar este comando")
def setup(bot):
    bot.add_cog(devcommands(bot))