import discord
from commands.music.base_music import BaseMusicCommand
from discord.ext import commands
import lenguajes as leng
from musica.music import musicManager
import musica.servermanager as sm

class PlaybackCommand(BaseMusicCommand):
	"""Comandos de reproducción: play, pause, resume, stop."""

	def __init__(self, bot):
		super().__init__(bot)
		self.music_manager = musicManager()
		self.server_manager = sm.serverManager()

	@commands.Command(name="new_play", aliases=["p", "pl"])
	async def play(self, ctx: commands.Context, *request):
		"""Reproduce música desde YouTube o archivos"""
		self.log_command_user(ctx, "play")

		# Validar que hay un request
		if not request:
			lang = self.get_language(ctx)
			await ctx.send(leng.eenolduvpaalq[lang])
			return

		# Verificar permisos de voz (usuario en canal o dev)
		if not await self.check_voice_channel(ctx):
			return

		# Construir el texto de la solicitud
		texto = " ".join(request)

		# Determinar tipo de reproducción (archivo o YouTube)
		is_file = "-f" in texto
		queue_type = "fl" if is_file else "yt"
		
		# Obtener voice channel si existe
		voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

		# TODO: Refactorizar musicManager para usar servicios modernos
		# TODO: Separar lógica de queue del reproductor
		# Agregar a la cola
		await self.music_manager.queuer(ctx, texto, queue_type)

		# Si el bot ya está conectado
		if voice_client and voice_client.is_connected():
			await self._handle_existing_connection(ctx, voice_client)
		# Si necesita conectarse
		elif ctx.author.voice:
			await self._handle_new_connection(ctx)
	
	async def _handle_existing_connection(self, ctx: commands.Context, voice_client: discord.VoiceClient):
		"""Maneja la reproducción cuando el bot ya está conectado."""
		guild_id = ctx.guild.id

		# Si no está reproduciendo, iniciar
		if not voice_client.is_playing():
			# TODO: Refactorizar esta lógica al servicio de música
			# Verificar si hay un índice válido
			if self.server_manager.exists(guild_id):
				server = self.server_manager.get_server(guild_id)
				if server.cplaying == -1:
					server.cplaying = len(server.songs) - 1

			await self.music_manager.play(voice_client, ctx, self.bot)
	
	async def _handle_new_connection(self, ctx: commands.Context):
		"""Maneja la conexión inicial del bot al canal de voz."""
		channel = ctx.author.voice.channel
		await channel.connect()

		voice_client = ctx.voice_client

		# Iniciar reproducción
		if not voice_client.is_playing():
			await self.music_manager.play(voice_client, ctx, self.bot)

	@commands.Command(name="new_pause", aliases=["ps"])
	async def pause(self, ctx: commands.Context):
		"""Pausa la reproducción actual."""
		self.log_command_user(ctx, "pause")

		if not self.has_permission(ctx):
			lang = self.get_language(ctx)
			await ctx.send(leng.neencdv[lang])
			return
		
		voice_client = ctx.voice_client

		if not voice_client:
			return

		guild_id = ctx.guild.id

		if not self.server_manager.exists(guild_id):
			return
		
		lang = self.get_language(ctx)

		if voice_client.is_paused():
			await ctx.send(leng.eayep[lang])
			return
		
		# TODO: Mover esta lógica de tiempo a un servicio dedicado
		import time
		server = self.server_manager.get_server(guild_id)
		t = time.localtime()
		server.ptime = time.strftime("%H:%M:%S", t)

		voice_client.pause()

		embed = discord.Embed(title=leng.pausado[lang], color=0x3498DB)
		await ctx.send(embed=embed)

	@commands.Command(name="new_resume", aliases=["r"])
	async def resume(self, ctx: commands.Context):
		"""Reanuda la reproducción pausada."""
		self.log_command_user(ctx, "resume")

		if not self.has_permission(ctx):
			lang = self.get_language(ctx)
			await ctx.send(leng.neencdv[lang])
			return
		
		voice_client = ctx.voice_client

		if not voice_client:
			return
		
		guild_id = ctx.guild.id

		if not self.server_manager.exists(guild_id):
			return

		lang = self.get_language(ctx)

		if not voice_client.is_paused():
			await ctx.send(leng.eanep[lang])
			return
		
		voice_client.resume()

		# TODO: Refactorizar cálculo de tiempo a un servicio de temporización
		import time
		import datetime

		server = self.server_manager.get_server(guild_id)

		# Calcular tiempo pausado
		resume_time = time.strftime("%H:%M:%S", time.localtime())
		x = time.strptime(resume_time.split(',')[0], "%H:%M:%S")
		resume_time = datetime.timedelta(
			hours=x.tm_hour,
			minutes=x.tm_min,
			seconds=x.tm_sec
		).total_seconds()

		x = time.strptime(server.time.split(',')[0], "%H:%M:%S")
		tiempo = datetime.timedelta(
			hours=x.tm_hour,
			minutes=x.tm_min,
			seconds=x.tm_sec
		).total_seconds()

		x = time.strptime(server.ptime.split(',')[0], "%H:%M:%S")
		ptime = datetime.timedelta(
			hours=x.tm_hour,
			minutes=x.tm_min,
			seconds=x.tm_sec
		).total_seconds()

		time_paused = resume_time - ptime
		server.time = time.strftime("%H:%M:%S", time.gmtime(tiempo + time_paused))

		embed = discord.Embed(title=leng.resumido[lang], color=0x3498DB)
		await ctx.send(embed=embed)

	@commands.Command(name="new_stop", aliases=["s"])
	async def stop(self, ctx: commands.Context):
		"""Detiene la reproducción actual."""
		self.log_command_user(ctx, "stop")

		if not self.has_permission(ctx):
			lang = self.get_language(ctx)
			await ctx.send(leng.neencdv[lang])
			return
		
		guild_id = ctx.guild.id
		
		if not self.server_manager.exists(guild_id):
			return

		voice_client = ctx.voice_client

		if voice_client:
			server = self.server_manager.get_server(guild_id)
			server.status = False
			voice_client.stop()

async def setup(bot):
	await bot.add_cog(PlaybackCommand(bot))