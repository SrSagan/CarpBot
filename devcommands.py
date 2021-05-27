import os

import discord
from discord.ext import commands
import data
from dotenv import load_dotenv

a = data.datos()


load_dotenv() 
devuser = os.getenv('DEV_USER') #checkea los los dev users
devuser2 = os.getenv('DEV_USER2')

class devcommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command( #comando debug arrays para mostrar el largo de todos los grupos
	 aliases=["da"],
	 name='debug_arrays',
	 help="Muestra las arrays de links",
	 brief="Muestra las arrays de links (solo devs)"

	) 
    async def debug_arrays(self, ctx):
        a = data.datos()
        grupos = a.get_data() #agarra la info
        print("debug_arrays usado")
        if ctx.message.author.id == int(devuser) or int(devuser2): #checkea ke sea un dev el ke lo haya usado
        	for j in a.grupos:
        		await ctx.send(str(j)+" array: "+str(len(grupos[j]["data"]))) #imprime los datos en ds
        else:
        	await ctx.send("Solo devs pueden usar este comando")

    @commands.command( #muestra todas las img de X grupo
	aliases=["di"],
	name='debug_images',
	help="Muestra todas las imagenes guardadas",
	brief="Muestra todas las img (solo devs)"
	)
    async def debug_images(self, ctx, *arg):
        a = data.datos()
        grupos = a.get_data()
        print("debug_images usado")
        if ctx.message.author.id == int(devuser) or int(devuser2): #checkeea ke sea un dev
        	for j in a.grupos:
        		if arg[0] == grupos[j]["name"]:
        			for link in grupos[j]["data"]:
        				await ctx.send(str(link)) #imprime todas las img 1 a 1
        else:
        	await ctx.send("Solo devs pueden usar este comando")

    '''@commands.command(
    	aliases=["db"],
    	name='debug',
    	help='Comando debug',
    	brief='Comando debug'
    )
    async def debug(self, ctx):
    	a = data.datos()
    	grupos = a.get_data()
    	print(grupos["tdplinks"])'''
		
def setup(bot):
    bot.add_cog(devcommands(bot))