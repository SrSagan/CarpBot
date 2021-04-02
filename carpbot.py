import os

import discord
from dotenv import load_dotenv
from discord.ext import commands
import devcommands


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
devuser = os.getenv('DEV_USER')
devuser2 = os.getenv('DEV_USER2')

bot = commands.Bot(command_prefix='"', case_insensitive=True)

extensions=["linkcommands", "imagecommands", "devcommands", "generalcommands"]

if __name__ == '__main__':
	for extension in extensions:
		bot.load_extension(extension)



#MUSICA
#----------------------------------------------------------------------------------------------------------------------------

'''@bot.command(
	name='leave',
	help='Sale del canal de voz',
	brief='Sale del canal de voz'
	)
async def leave(ctx):
	await ctx.voice_client.disconnect()


@bot.command(pass_context=True,
	name='play',
	help='Reproduce un link de youtube',
	brief='Reproduce musica'
	)
async def play(ctx, *url):

	await ctx.send("estoy aqui")
	ytlinks.append(url)

	for links in ytlinks:
		print(links)
		author = ctx.message.author
		channel = author.voice.channel
		vc = await channel.connect()
		video = new(links[0])
		audio = video.getbestaudio()
		filename = audio.download()
		vc.play(discord.FFmpegPCMAudio(str(video.title)+'.webm'))
		vc.is_playing()
		#os.system("rm"+' '+'"'+str(video.title)+'"'+'.webm')
	await ctx.send("estoy aca")
	
	

@bot.command(pass_context=True,
	name='queue',
	help='Muestra las canciones en la lista de reproduccion',
	brief='Muestra la queue'
	)
async def queue(ctx):

	for url in ytlinks:
		print(url)
		v = new(url[0])
		await ctx.send(str(v.title))'''

print("bot iniciado")
bot.run(TOKEN)