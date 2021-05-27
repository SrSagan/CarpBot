import os

import discord
from discord.ext import commands
import data

import random

a = data.datos()

class imgcommands(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command( #todos hacen lo mismo
		aliases=['carp'],
    	name='carpincho',
    	help="Muestra una imagen random de un carpincho",
    	brief="Muestra una img de un carpincho"
    	)
	async def carpincho(self, ctx):
		a = data.datos()
		grupos = a.get_data() #agarra datos
		print("Carpincho usado")
		response = random.choice(grupos["carplinks"]["data"]) #agarra un link random
		if response.rfind("mp4") > -1 or response.rfind("youtu") > -1: # si es mp4 o youtube no le pone marco
			await ctx.send(response)
		else:
			embed=discord.Embed(color=0x3498DB) #si es una img le pone marquito
			embed.set_image(url=response)
			await ctx.send(embed=embed)

	@commands.command(
		name='rayllum',
		help="Muestra una imagen random de rayllum",
		brief="Muestra una img de rayllum"
		)
	async def rayllum(self, ctx):
		a = data.datos()
		grupos = a.get_data()
		print("Rayllum usado")
		response = random.choice(grupos["rayllumlinks"]["data"])
		if response.rfind("mp4") > -1 or response.rfind("youtu") > -1:
				await ctx.send(response)
		else:
			embed=discord.Embed(color=0x3498DB)
			embed.set_image(url=response)
			await ctx.send(embed=embed)
	@commands.command(
		name='tdp',
		help="Muestra una imagen random de The Dragon Prince (incluyendo spoilers)",
		brief="Muestra una img de tdp"
    	)
	async def tdp(self, ctx):
		a = data.datos()
		grupos = a.get_data()
		print("tdp usado")
		response = random.choice(grupos["tdplinks"]["data"])
		if response.rfind("mp4") > -1 or response.rfind("youtu") > -1:
				await ctx.send(response)
		else:
			embed=discord.Embed(color=0x3498DB)
			embed.set_image(url=response)
			await ctx.send(embed=embed)
	@commands.command(
		aliases=['atla'],
		name='avatar',
		help="Muestra una imagen random de Avatar la Leyenda de Aang (incluyendo spoilers)",
		brief="Muestra una img de avatar"
    	)
	async def avatar(self, ctx):
		a = data.datos()
		grupos = a.get_data()
		print("avatar usado")
		response = random.choice(grupos["avatarlinks"]["data"])
		if response.rfind("mp4") > -1 or response.rfind("youtu") > -1:
			await ctx.send(response)
		else:
			embed=discord.Embed(color=0x3498DB)
			embed.set_image(url=response)
			await ctx.send(embed=embed)
	@commands.command(
		name='meme',
		help="Muestra un meme random",
		brief="Muestra un meme"
		)
	async def meme(self, ctx):
		a = data.datos()
		grupos = a.get_data()
		print("meme usado")
		response = random.choice(grupos["memelinks"]["data"])
		if response.rfind("mp4") > -1 or response.rfind("youtu") > -1:
				await ctx.send(response)
		else:
			embed=discord.Embed(color=0x3498DB)
			embed.set_image(url=response)
			await ctx.send(embed=embed)
	@commands.command(
		name='csm',
		help="Muestra una imagen de chainsaw man random",
		brief="Muestra una img. de csm"
    	)
	async def csm(self, ctx):
		a = data.datos()
		grupos = a.get_data()
		print("csm usado")
		response = random.choice(grupos["csmlinks"]["data"])
		print(response)
		if response.rfind("mp4") > -1 or response.rfind("youtu") > -1:
				await ctx.send(response)
		else:
			embed=discord.Embed(color=0x3498DB)
			embed.set_image(url=response)
			await ctx.send(embed=embed)

	@commands.command(
		aliases=['buho'],
		name='owl',
		help="Muestra una imagen de un buho random",
		brief="Muestra una img. de owl"
    	)
	async def owl(self, ctx):
		a = data.datos()
		grupos = a.get_data()
		print("owl usado")
		response = random.choice(grupos["owlinks"]["data"])
		print(response)
		if response.rfind("mp4") > -1 or response.rfind("youtu") > -1:
				await ctx.send(response)
		else:
			embed=discord.Embed(color=0x3498DB)
			embed.set_image(url=response)
			await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(imgcommands(bot))