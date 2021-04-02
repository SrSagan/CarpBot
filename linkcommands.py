import os

import discord
from discord.ext import commands
import data

a = data.datos()
grupos = a.grupos
formatos = a.formatos
gruposText = a.gruposText

class linkcommands(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(
	aliases=['al'],
	name='addlink',
	help="Permite agregar un link de imagen al grupo de rayllum o carpincho, uso: addlink (link1 link2 link3 ...)",
	brief="Permite agregar un link de imagen"
	)
	async def add_link(self, ctx, *args):
		a = data.datos()
		print("addlink usado")
		if len(args) > 0:
			added=0
			await ctx.send("En cual queres agregar el link?")
			embed=discord.Embed(title="Grupos",color=0x3498DB,description=gruposText)
			await ctx.send(embed=embed)		
			msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author) 
			contador = 0
			for j in a.grupos:
				if msg.content == a.grupos[j]["name"]:
					archivo = a.grupos[j]["fileName"]  
					
					for arg in args:
						temp = arg.rfind('.')
						formato = arg[temp:]
						finFormato = arg.rfind('?')
						formatoConException = arg[temp:finFormato]
						youtubeLink = arg.find("youtu")

						if arg ==' ':
							await ctx.send("Link invalido")
							print("link invalido")  
						elif arg in a.grupos[j]["data"]:
							await ctx.send("El link ya esta en la lista")
							print("link invalido")  
						elif args[0] == 'exception':
							if arg != 'exception':
								if temp > -1:
									a.grupos[j]["data"].append(arg) 
									with open(archivo, "w")as txt_file:
										for line in a.grupos[j]["data"]:
											txt_file.write("".join(line)+"\n")
									print("link agregado con exception")
									added=added+1
									jact = j
								else:
									await ctx.send("Link invalido")
									print("link invalido")
									break
							
						elif args[0] == "continue":
							await ctx.send("Esperando imagenes")
							while True:
								imagenes = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
								if imagenes.content == "end":
									await ctx.send("Terminado")
									break
								for b in imagenes.attachments:
									img = b.url		
									temp = img.rfind('.')
									formato = img[temp:]		
									if formato in formatos:
										if img not in a.grupos[j]["data"]:
											a.grupos[j]["data"].append(img) 
											with open(archivo, "w") as txt_file:
												for line in a.grupos[j]["data"]:
													txt_file.write("".join(line) + "\n")
										else:
											await ctx.send("El link ya esta en la lista")
											print("link invalido")		
										added=added+1
										jact = j
									else:
										await ctx.send("formato invalido")
										await ctx.send("Formatos:"+str(formatos))		
						elif temp > -1:
							if formato in formatos or formato in formatoConException or youtubeLink > -1:
								a = data.datos()
								a.grupos[j]["data"].append(arg) 
								with open(archivo, "w") as txt_file:
									for line in a.grupos[j]["data"]:
										txt_file.write("".join(line) + "\n")
								added=added+1
								jact = j
							else:
								await ctx.send("formato invalido")
								await ctx.send("Formatos:"+str(formatos))
						else:
							await ctx.send("Link invalido")
							print("link invalido")  
				elif msg.content == "cancel":
					await ctx.send("Operacion cancelada")
					break   
				else:
					contador = contador+1
				if contador >= len(a.grupos):
					await ctx.send("Grupo Invalido")
					embed=discord.Embed(title="Grupos validos:",color=0x3498DB,description=gruposText)
					await ctx.send(embed=embed) 
			if added == 1:
				await ctx.send(str(added)+" link agregado a "+"'"+str(a.grupos[jact]["name"])+"'")
			elif added > 1:
				await ctx.send(str(added)+" links agregados a "+"'"+str(a.grupos[jact]["name"])+"'")
		else:
			await ctx.send("Escriba un link junto con el comando")

	@commands.command(
	aliases=['rl'],
    name='removelink',
    help="Permite eliminar un link de imagen de el grupo rayllum o carpincho, uso: removelink (link1 link2 link3 ...)",
    brief="Permite eliminar un link de imagen"
    )
	async def removelink(self, ctx, *args):
		a = data.datos()	
		removedLinks={
			"carplinks":0,
			"rayllumlinks":0,
			"tdplinks":0,
			"avatarlinks":0,
			"memelinks":0,
			"csmlinks":0
		}   
		print("removelink usado")
		for x in args:
			if len(args) > 0:
				contador=0
				for j in a.grupos:
					if not x in a.grupos[j]["data"]:
						z = (x+"\n")
					else:
						z = x	
					if z in a.grupos[j]["data"]:
						y = a.grupos[j]["data"].index(z)
						a.grupos[j]["data"].pop(y)    
						archivo = a.grupos[j]["fileName"]
						#elimina el link del archivo
						with open(archivo, "r") as f:
							lines = f.readlines()
						with open(archivo, "w") as f:
							for line in lines:
								if line.strip("\n") != x:
									f.write(line)
						removedLinks[j]=removedLinks[j]+1
						print("link removido")
					else:
						contador = contador+1
					if contador >= len(a.grupos):
						await ctx.send("El link: "+"'"+x+"'"+" no se encuentra en ningun grupo")
			else:
				await ctx.send("Escriba el link de la img junto con el comando")
		for j in a.grupos:
			if removedLinks[j] > 0:
				if removedLinks[j] == 1:
					await ctx.send(str(removedLinks[j])+" link removido de: "+"'"+str(a.grupos[j]["name"])+"'")
				elif removedLinks[j] > 1:
					await ctx.send(str(removedLinks[j])+" links removidos de: "+"'"+str(a.grupos[j]["name"])+"'") 
def setup(bot):
    bot.add_cog(linkcommands(bot))