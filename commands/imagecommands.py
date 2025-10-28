import os

import discord
from discord.ext import commands
import data

import random

a = data.datos()
import lenguajes as leng

groups={
		"carplinks":['carp', 'capybara', 'capivara', 'carpincho'],
		"rayllumlinks":['rayllum'],
		"tdplinks":["tdp"],
		"avatarlinks":["avatar", "atla"],
		"memelinks":["meme"],
		"owlinks":['owl', 'buho'],
		"csmlinks":['csm', 'chainsawman'],
		"catlinks":['cat', "gatinho", "gatito", "kitty", "gato"],
		"ducklinks":["duck", "pato", "quack", "patito", "fuck", "ducky"],
}
aliases=[]
for grupo in groups:
	for alias in groups[grupo]:
		if(alias != 'carpincho'):
			aliases.append(alias)


class images(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		aliases=[]
		self.groups=groups
		self.aliases=aliases

#-----------------------------IMAGES-----------------------------#

	@commands.command(
		aliases=aliases,
		name='carpincho',
    	)
	async def images(self, ctx):
		command = ctx.message.content
		prefix = await a.get_prefix(0, ctx.message)

		command = command[len(prefix):].lower()

		for grupo in self.groups:

			if(command in self.groups[grupo]):
				grupos = a.get_data()
				print(grupo+" usado")

				for g in grupos:
					if(grupo == g["group"]):
						response = random.choice(g["data"])
						break
				if response.rfind("mp4") > -1 or response.rfind("youtu") > -1:
						await ctx.send(response)
				else:
					embed=discord.Embed(color=0x3498DB)
					embed.set_image(url=response)
					await ctx.send(embed=embed)

#-----------------------------GROUPS-----------------------------#

	@commands.command( #todos hacen lo mismo
		aliases=['groups'],
    	name='grupos',
    	)
	async def grupos(self, ctx):
		a = data.datos()
		grupos = a.get_data() #agarra datos
		print("Grupos usado")
		 #si es una img le pone marquito
		texto=''
		for grupo in grupos:
			texto=texto+str(grupo["name"])+": "+str(len(grupo["data"]))+"\n"
			
		embed=discord.Embed(color=0x3498DB, title=leng.grupos[a.get_lenguaje(ctx.message)] ,description=texto)
			
		await ctx.send(embed=embed)




async def setup(bot):
	await bot.add_cog(images(bot))