import sys, os

import discord
from dotenv import load_dotenv
from discord.ext import commands
import data
d = data.datos()

load_dotenv() #carga datos importantes como el token y los dev users del archivo .dev
TOKEN = os.getenv('DISCORD_TOKEN')
devuser = os.getenv('DEV_USER')
devuser2 = os.getenv('DEV_USER2')

bot = commands.Bot(command_prefix=d.get_prefix, case_insensitive=True) #pone el prefix del comando

extensions=["linkcommands", "imagecommands", "devcommands", "generalcommands", "musiccommands"] #una array con todos los archivos

if __name__ == '__main__': #se cargan todos los archivos
	for extension in extensions:
		bot.load_extension(extension)


print("bot iniciado")
bot.run(TOKEN)
