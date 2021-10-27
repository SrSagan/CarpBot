import os

import discord
from discord.ext import commands
import data

a = data.datos()
formatos = a.formatos
gruposText = a.gruposText

class links(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	
	@commands.command( #para agregar un link codigo LARGOOOOOOOOOOOOOOOOOOOOOO
	aliases=['al'],
	name='addlink',
	help="Permite agregar un link de imagen al grupo de rayllum o carpincho, uso: addlink (link1 link2 link3 ...)",
	brief="Permite agregar un link de imagen"
	)
	async def add_link(self, ctx, *args):
		a = data.datos()
		grupos = a.get_data() #agarra lso datos quu ya estan ;-;
		print("addlink usado")
		if len(args) > 0: #checkea si sikiera se puso algo
			added=0 #cantidad de links agregados
			await ctx.send("En cual queres agregar el link?") #se pregunta por grupo
			InvalidGroup=True
			while InvalidGroup:
				InvalidGroup=False
				embed=discord.Embed(title="Grupos",color=0x3498DB,description=gruposText)
				await ctx.send(embed=embed)		
				msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author) #se espera la respuesta del grupo
				contador = 0 #contador
				for j in grupos: #se checkea cada grupo
					if msg.content == grupos[j]["name"]: #checkea si la respuesta de grupo 
						for arg in args: #checkea los argumentos para ver si hay un link
							temp = arg.rfind('.')
							formato = arg[temp:]
							finFormato = arg.rfind('?')
							formatoConException = arg[temp:finFormato]
							youtubeLink = arg.find("youtu")
							argNewLine =(arg+"\n") #checkea tipo muchas cosas en el archivo y lo guarda en varias variables (capaz la mitad no se si se usan)

							if arg ==' ': #checkea ke haya algo porke si no hay nada F
								await ctx.send("Link invalido")
								print("link invalido")  

							elif arg in grupos[j]["data"] or argNewLine in grupos[j]["data"]: #checkea is el link ya esta en la lista
								await ctx.send("El link ya esta en la lista")
								print("link invalido")

							elif args[0] == 'exception': #checkea si hay excepcion
								if arg != 'exception':
									if temp > -1: #checkea si tiene un punto
										a.set_data(j, arg) #lo guarda en el archivo
										print("link agregado con exception") 
										added=added+1 #cantidad de links agregados
										jact = j #nose pake es esto

									else:
										await ctx.send("Link invalido") #si no tiene punto es link invalido
										print("link invalido")
										break
									
							elif args[0] == "continue": #checkea si hay continue
								await ctx.send("Esperando imagenes")
								while True:
									imagenes = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author) #lee msg

									if imagenes.content == "end": #si pone end frena el loop
										await ctx.send("Terminado")
										break

									for b in imagenes.attachments: #de vuelta agarra como 20 cosas que no se si sirven para algo
										img = b.url		
										temp = img.rfind('.')
										formato = img[temp:]
										imgNewLine = (img+"\n")		

										if formato in formatos: #checkea si esta en formatos
											if img not in grupos[j]["data"] or imgNewLine not in grupos[j]["data"]: #checkea que no este ya en la lista
												a.set_data(j, img) #agrega el link
												added=added+1
												jact = j #???? I dunno bruh
											else:
												await ctx.send("El link ya esta en la lista") #si ya esta en la lista se informa
												print("link invalido")		


										else:
											await ctx.send("formato invalido")
											await ctx.send("Formatos:"+str(formatos))

							elif temp > -1: #en caso de que no ke no haya nada especial se checkea formatos y se agrega el link

								if formato in formatos or formato in formatoConException or youtubeLink > -1: #se checkea si es formato o youtube
									a.set_data(j, arg) #se agrega el link
									added=added+1
									jact = j #ke no se capo NOSE
								else:
									await ctx.send("formato invalido")
									await ctx.send("Formatos:"+str(formatos))
							else: #si nada funciona es porque el link es invalido como tu abuela
								await ctx.send("Link invalido")
								print("link invalido")  
					elif msg.content == "cancel": #para cancelar el grupo
						await ctx.send("Operacion cancelada")
						break   
					else:
						contador = contador+1 #contador para cantidad de grupos
					if contador >= len(grupos): #se checkea para la cantidad de grupos
						await ctx.send("Grupo Invalido") #si es un grupo invalido como tu abuela
						InvalidGroup=True

				if added == 1: #cantidad de links igual a 1
					await ctx.send(str(added)+" link agregado a "+"'"+str(grupos[jact]["name"])+"'")
				elif added > 1: #cantidad de links agregados mayor a uno se dice
					await ctx.send(str(added)+" links agregados a "+"'"+str(grupos[jact]["name"])+"'")
		else: #si no se escribio nada
			await ctx.send("Escriba un link junto con el comando")

	@commands.command( #comando de removelink para remover links....
	aliases=['rl'],
    name='removelink',
    help="Permite eliminar un link de imagen de el grupo rayllum o carpincho, uso: removelink (link1 link2 link3 ...)",
    brief="Permite eliminar un link de imagen"
    )
	async def removelink(self, ctx, *args):
		a = data.datos()
		grupos = a.get_data() #agarra la data de grupos
		removedLinks={
			"carplinks":0,
			"rayllumlinks":0,
			"tdplinks":0,
			"avatarlinks":0,
			"memelinks":0,
			"csmlinks":0,
			"owlinks":0,
			"catlinks":0,
		} #contador de links removidos
		print("removelink usado")
		for x in args: #agarra el argumento
			if len(args) > 0: #checkea que haya argumentos
				contador=0
				for j in grupos: #checkea en cada grupo
					if not x in grupos[j]["data"]: #si no esta entre los links
						z = (x+"\n")
					else:
						z = x	
					if z in grupos[j]["data"]:
						a.rem_data(j, z, x) #saca la data
						removedLinks[j]=removedLinks[j]+1 #sube el contador
						print("link removido")
					else:
						contador = contador+1 #sube el contador de grupos
					if contador >= len(grupos): #si todos los grupos son checkeados es porque el link no esta
						await ctx.send("El link: "+"'"+x+"'"+" no se encuentra en ningun grupo")
			else:
				await ctx.send("Escriba el link de la img junto con el comando")
		for j in grupos: #se escribe cuantos links se eliminaron de que grupos
			if removedLinks[j] > 0:
				if removedLinks[j] == 1:
					await ctx.send(str(removedLinks[j])+" link removido de: "+"'"+str(grupos[j]["name"])+"'")
				elif removedLinks[j] > 1:
					await ctx.send(str(removedLinks[j])+" links removidos de: "+"'"+str(grupos[j]["name"])+"'") 
def setup(bot):
    bot.add_cog(links(bot))