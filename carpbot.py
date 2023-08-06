import os
import sys
import discord
from dotenv import load_dotenv
from discord.ext import commands
import data
import asyncio
d = data.datos()
import logging
import time

#all logging

timestr = time.strftime("%d-%Y-%m--%H:%m:%S")

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()

fileHandler = logging.FileHandler("{0}/{1}.log".format("logs", timestr))
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

#till here

intents = discord.Intents.default()
intents.message_content = True

load_dotenv() #carga datos importantes como el token y los dev users del archivo .dev
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix=d.get_prefix, case_insensitive=True, help_command=None, intents=intents) #pone el prefix del comando

extensions=["linkcommands", "imagecommands", "devcommands", "generalcommands", "musiccommands"] #una array con todos los archivos

async def main():
	for extension in extensions:
		await bot.load_extension(extension)
	print("Bot iniciado")
	#await bot.start(TOKEN)
		

asyncio.run(main())
bot.run(TOKEN)
