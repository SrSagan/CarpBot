import os

import discord
from discord.ext import commands
import data

import random

a = data.datos()


class imgcommands(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(
		aliases=['carp'],
    	name='carpincho',
    	help="Muestra una imagen random de un carpincho",
    	brief="Muestra una img de un carpincho"
    	)
	async def carpincho(self, ctx):
		a = data.datos()
		print("Carpincho usado")
		response = random.choice(a.grupos["carplinks"]["data"])
		if response.rfind("mp4") > -1 or response.rfind("youtu") > -1:
			await ctx.send(response)
		else:
			embed=discord.Embed(title="Carpincho",color=0x3498DB)
			embed.set_image(url=response)
			await ctx.send(embed=embed)
	@commands.command(
		name='rayllum',
		help="Muestra una imagen random de rayllum",
		brief="Muestra una img de rayllum"
		)
	async def rayllum(self, ctx):
		a = data.datos()
		print("Rayllum usado")
		response = random.choice(a.grupos["rayllumlinks"]["data"])
		if response.rfind("mp4") > -1 or response.rfind("youtu") > -1:
				await ctx.send(response)
		else:
			embed=discord.Embed(title="Rayllum",color=0x3498DB)
			embed.set_image(url=response)
			await ctx.send(embed=embed)
	@commands.command(
		name='tdp',
		help="Muestra una imagen random de The Dragon Prince (incluyendo spoilers)",
		brief="Muestra una img de tdp"
    	)
	async def tdp(self, ctx):
		a = data.datos()
		print("tdp usado")
		response = random.choice(a.grupos["tdplinks"]["data"])
		if response.rfind("mp4") > -1 or response.rfind("youtu") > -1:
				await ctx.send(response)
		else:
			embed=discord.Embed(title="The Dragon Prince",color=0x3498DB)
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
		print("avatar usado")
		response = random.choice(a.grupos["avatarlinks"]["data"])
		if response.rfind("mp4") > -1 or response.rfind("youtu") > -1:
			await ctx.send(response)
		else:
			embed=discord.Embed(title="Avatar la Leyenda de Aang",color=0x3498DB)
			embed.set_image(url=response)
			await ctx.send(embed=embed)
	@commands.command(
		name='meme',
		help="Muestra un meme random",
		brief="Muestra un meme"
		)
	async def meme(self, ctx):
		a = data.datos()
		print("meme usado")
		response = random.choice(a.grupos["memelinks"]["data"])
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
		print("csm usado")
		response = random.choice(a.grupos["csmlinks"]["data"])
		print(response)
		if response.rfind("mp4") > -1 or response.rfind("youtu") > -1:
				await ctx.send(response)
		else:
			embed=discord.Embed(color=0x3498DB)
			embed.set_image(url=response)
			await ctx.send(embed=embed)

def setup(bot):
	bot.add_cog(imgcommands(bot))