import os

import discord
from dotenv import load_dotenv
from discord.ext import commands

import random

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='"')

formatos = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4']
gruposArray = ['carpincho', 'rayllum', 'tdp', 'avatar', 'meme']

carplinks = []
rayllumlinks = []
tdplinks = []
avatarlinks = []
memelinks = []
fasolinks = []


for j in gruposArray: 

	if j == 'carpincho':
		temparray = carplinks
		archivo = "carplinks.txt"
	elif j == 'rayllum':
		temparray = rayllumlinks
		archivo = "rayllumlinks.txt"
	elif j == 'tdp':
		temparray = tdplinks
		archivo = "tdplinks.txt"
	elif j == 'avatar':
		temparray = avatarlinks
		archivo = "avatarlinks.txt"
	elif j == 'meme':
		temparray = memelinks
		archivo = "memelinks.txt"

	with open(archivo, "r") as f:
		for line in f:
			if line != '\n':
				temparray.append(line)
	
gruposText = """
**avatar**: refiriendose a Avatar la Leyenda de Aang
**tdp**: refiriendose a The Dragon Prince
**rayllum**: refiriendose antra el ship de Rayla y Callum de tdp
**carpincho**: refiriendose al mejor animal en la existencia
**meme**: todo tipo de memes
"""

@bot.command(
	name='addlink',
	help="Permite agregar un link de imagen al grupo de rayllum o carpincho, uso: addlink (link1 link2 link3 ...)",
	brief="Permite agregar un link de imagen"
	)
async def add_link(ctx, *args):

	await ctx.send("En cual queres agregar el link?")
	embed=discord.Embed(title="Grupos",color=0x3498DB,description=gruposText)
	await ctx.send(embed=embed)
	print("addlink usado")
	
	msg = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
	

	if msg.content == 'carpincho':
		archivo = 'carplinks.txt'
		temparray = carplinks
	elif msg.content == 'rayllum':
		archivo = 'rayllumlinks.txt'
		temparray = rayllumlinks
	elif msg.content == 'tdp':
		archivo = 'tdplinks.txt'
		temparray = tdplinks
	elif msg.content == 'avatar':
		archivo = 'avatarlinks.txt'
		temparray = avatarlinks
	elif msg.content == 'meme':
		archivo = 'memelinks.txt'
		temparray = memelinks
	else:
		await ctx.send("Grupo invalido")
		print("Grupo invalido")

	x=0
	arg_cant = (len(args)-1)
	while x <=  arg_cant:
		arg = str(args[x])
		x=x+1
		temp = arg.rfind('.')
		formato = arg[temp:]

		if arg == '':
			await ctx.send("Link invalido")
			print("Link invalido")
		
		elif arg in str(temparray):
			await ctx.send("El link ya esta en la lista")
			print("Link invalido")

		elif args[0] == 'exception':
			if temp > -1:
				await ctx.send("Link agregado")
				print("link agegado")
				temparray.append(arg)
				with open(archivo, "w") as txt_file:
					for line in temparray:
						txt_file.write("".join(line) + "\n")
			elif x > 2:
				await ctx.send("Link invalido")
				print("Link invalido")
		elif temp > -1:
			if formato in formatos:
				await ctx.send("Link agregado")
				print("link agegado")
				temparray.append(arg)
				with open(archivo, "w") as txt_file:
					for line in temparray:
						txt_file.write("".join(line) + "\n")
			else:
				await ctx.send("Formato invalido")
				await ctx.send(formatos)

		else:
			await ctx.send("Link invalido")
			print("Link invalido")
	


@bot.command(
	 name='debug_arrays',
	 help="Muestra las arrays de links",
	 brief="Muestra las arrays de links (solo devs)"
	 )
async def debug_arrays(ctx):

	if ctx.message.author.id == 392731404250906634:
		await ctx.send("carpLinks array: " + str(len(carplinks)))
		await ctx.send("rayllumlinks array: "+str(len(rayllumlinks)))
		await ctx.send("tdplinks array: "+str(len(tdplinks)))
		await ctx.send("avatarlinks array: "+str(len(avatarlinks)))
		await ctx.send("memelinks array: "+str(len(memelinks)))
	else:
		await ctx.send("Solo devs pueden usar este comando")

@bot.command(
	name='debug_images',
	help="Muestra todas las imagenes guardadas",
	brief="Muestra todas las img (solo devs)"
	)
async def debug_images(ctx, *arg):

	if ctx.message.author.id == 392731404250906634:
		if arg[0] == 'carpincho':
			temparray = carplinks
		elif arg[0] == 'rayllum':
			temparray = rayllumlinks
		elif arg[0] == 'tdp':
			temparray = tdplinks
		elif arg[0] == 'avatar':
			temparray = avatarlinks
		elif arg[0] == 'meme':
			temparray = memelinks
		else:
			await ctx.send("Por favor marque el grupo en el comando")

		x=0
		while (len(temparray)-1) >= x:
			await ctx.send(str(temparray[x]))
			x=x+1
	else:
		await ctx.send("Solo devs pueden usar este comando")

@bot.command(
	name='removelink',
	help="Permite eliminar un link de imagen de el grupo rayllum o carpincho, uso: removelink (link1 link2 link3 ...)",
	brief="Permite eliminar un link de imagen"
	)
async def removelink(ctx, *args):

	print("removelink usado")
	j=0
	while j <= 4:

		if j == 0:
			archivo = "carplinks.txt"
			temparray = carplinks
			mensaje = "Link removido de carpincho"
		elif j == 1:
			archivo = "rayllumlinks.txt"
			temparray = rayllumlinks
			mensaje = "Link removido de rayllum"
		elif j == 2:
			archivo = 'tdplinks.txt'
			temparray = tdplinks
			mensaje = "Link removido de tdp"
		elif j == 3:
			archivo = 'avatarlinks.txt'
			temparray = avatarlinks
			mensaje = "Link removido de avatar"
		elif j == 4:
			archivo = 'memelinks.txt'
			temparray = memelinks
			mensaje = "Link removido de meme"
		x=0

		while (len(temparray)-1) >= x:

			y=0

			while y <= (len(args)-1):
				if args[y] in temparray[x]:
					del temparray[x]
					print("link removido")

					with open(archivo, "r") as f:
						lines = f.readlines()
					with open(archivo, "w") as f:
						for line in lines:
							if line.strip("\n") != args[y]:
								f.write(line)
								
					await ctx.send(mensaje)
				y=y+1
			x=x+1
		j=j+1


@bot.command(
	name='carpincho',
	help="Muestra una imagen random de un carpincho",
	brief="Muestra una img de un carpincho"
	)
async def carpincho(ctx):

		print("Carpincho usado")
		response = random.choice(carplinks)
		if response.rfind("mp4") > -1:
			await ctx.send(response)
		else:
			embed=discord.Embed(title="Carpincho",color=0x3498DB)
			embed.set_image(url=response)
			await ctx.send(embed=embed)

@bot.command(
	name='rayllum',
	help="Muestra una imagen random de rayllum",
	brief="Muestra una img de rayllum"
	)
async def rayllum(ctx):
	print("Rayllum usado")
	response = random.choice(rayllumlinks)
	if response.rfind("mp4") > -1:
			await ctx.send(response)
	else:
		embed=discord.Embed(title="Rayllum",color=0x3498DB)
		embed.set_image(url=response)
		await ctx.send(embed=embed)

@bot.command(
	name='tdp',
	help="Muestra una imagen random de The Dragon Prince (incluyendo spoilers)",
	brief="Muestra una img de tdp"
	)
async def tdp(ctx):
	print("tdp usado")
	response = random.choice(tdplinks)
	if response.rfind("mp4") > -1:
			await ctx.send(response)
	else:
		embed=discord.Embed(title="The Dragon Prince",color=0x3498DB)
		embed.set_image(url=response)
		await ctx.send(embed=embed)

@bot.command(
	name='avatar',
	help="Muestra una imagen random de Avatar la Leyenda de Aang (incluyendo spoilers)",
	brief="Muestra una img de avatar"
	)
async def avatar(ctx):
	print("avatar usado")
	response = random.choice(avatarlinks)
	if response.rfind("mp4") > -1:
			await ctx.send(response)
	else:
		embed=discord.Embed(title="Avatar la Leyenda de Aang",color=0x3498DB)
		embed.set_image(url=response)
		await ctx.send(embed=embed)

@bot.command(
	name='meme',
	help="Muestra un meme random",
	brief="Muestra un meme"
	)
async def meme(ctx):
	print("meme usado")
	response = random.choice(memelinks)
	if response.rfind("mp4") > -1:
			await ctx.send(response)
	else:
		embed=discord.Embed(color=0x3498DB)
		embed.set_image(url=response)
		await ctx.send(embed=embed)

bot.run(TOKEN)