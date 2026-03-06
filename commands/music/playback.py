import discord
from commands.music.base_music import BaseMusicCommand
from discord.ext import commands
import lenguajes as leng
from musica.music import musicManager
import musica.servermanager as sm
import time
from loguru import logger
from utils.formatters import parse_time_to_seconds


class PlaybackCommand(BaseMusicCommand):
    """Comandos de reproducción: play, pause, resume, stop."""

    def __init__(self, bot):
        super().__init__(bot)
        self.music_manager = musicManager()
        self.server_manager = sm.serverManager()

    def _calculate_remaining_time(self, server, current_song, voice_client) -> str:
        """Calcula el tiempo restante de la canción actual."""
        start_seconds = parse_time_to_seconds(server.time)
        length_seconds = parse_time_to_seconds(current_song.length)

        # Tiempo actual
        if voice_client.is_paused() and server.status:
            current_seconds = parse_time_to_seconds(server.ptime)
        else:
            current_time = time.strftime("%H:%M:%S", time.localtime())
            current_seconds = parse_time_to_seconds(current_time)

        time_elapsed = current_seconds - start_seconds
        return time.strftime("%H:%M:%S", time.gmtime(length_seconds - time_elapsed))

    @commands.command(name="play", aliases=["p", "pl"])
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

    async def _handle_existing_connection(
        self, ctx: commands.Context, voice_client: discord.VoiceClient
    ):
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

    @commands.command(name="pause", aliases=["ps"])
    async def pause(self, ctx: commands.Context):
        """Pausa la reproducción actual."""
        self.log_command_user(ctx, "pause")

        state = await self.validate_music_state(ctx)
        if not state:
            return

        server, voice_client, lang = state

        if voice_client.is_paused():
            await ctx.send(leng.eayep[lang])
            return

        server.ptime = time.strftime("%H:%M:%S", time.localtime())
        voice_client.pause()

        embed = discord.Embed(title=leng.pausado[lang], color=0x3498DB)
        await ctx.send(embed=embed)

    @commands.command(name="resume", aliases=["r"])
    async def resume(self, ctx: commands.Context):
        """Reanuda la reproducción pausada."""
        self.log_command_user(ctx, "resume")

        state = await self.validate_music_state(ctx)
        if not state:
            return

        server, voice_client, lang = state

        if not voice_client.is_paused():
            await ctx.send(leng.eanep[lang])
            return

        voice_client.resume()

        # Calcular tiempo pausado
        resume_time = time.strftime("%H:%M:%S", time.localtime())
        resume_seconds = parse_time_to_seconds(resume_time)
        tiempo_seconds = parse_time_to_seconds(server.time)
        ptime_seconds = parse_time_to_seconds(server.ptime)

        time_paused = resume_seconds - ptime_seconds
        server.time = time.strftime(
            "%H:%M:%S", time.gmtime(tiempo_seconds + time_paused)
        )

        embed = discord.Embed(title=leng.resumido[lang], color=0x3498DB)
        await ctx.send(embed=embed)

    @commands.command(name="stop", aliases=["s"])
    async def stop(self, ctx: commands.Context):
        """Detiene la reproducción actual."""
        self.log_command_user(ctx, "stop")

        state = await self.validate_music_state(ctx)
        if not state:
            return

        server, voice_client, _ = state
        server.status = False
        voice_client.stop()

    @commands.command(name="leave", aliases=["l", "lv", "fuckoff"])
    async def leave(self, ctx: commands.Context):
        """Desconecta el bot del canal de voz y limpia la cola."""
        self.log_command_user(ctx, "leave")

        # Solo verificar permisos y voice_client
        if not self.has_permission(ctx):
            lang = self.get_language(ctx)
            await ctx.send(leng.neencdv[lang])
            return

        voice_client = ctx.voice_client

        if not voice_client:
            return

        guild_id = ctx.guild.id

        # Detener reproducción
        voice_client.stop()

        # Limpiar cola del servidor sin eliminar el servidor
        if self.server_manager.exists(guild_id):
            server = self.server_manager.get_server(guild_id)
            server.songs = []
            server.cplaying = -1
            server.status = False

        await voice_client.disconnect()

        logger.debug(f"Bot desconectado del servidor {guild_id}, cola limpiada")

    @commands.command(name="next", aliases=["n", "skip"])
    async def next(self, ctx: commands.Context, *args):
        """Salta a la siguiente canción o a un índice específico."""
        self.log_command_user(ctx, "next")

        state = await self.validate_music_state(ctx)
        if not state:
            return

        server, voice_client, lang = state

        # Si se especifica un índice
        if args:
            if args[0].isnumeric():
                index = int(args[0])
                if 0 < index <= len(server.songs):
                    server.cplaying = index - 1
                    voice_client.stop()
                else:
                    await ctx.send(leng.cfdr[lang])
            else:
                await ctx.send(leng.eenduc[lang])
        else:
            # Siguiente canción normal
            if server.looping == 2:  # Si está en loop de canción
                server.cplaying += 1
            voice_client.stop()

    @commands.command(name="back", aliases=["b"])
    async def back(self, ctx: commands.Context):
        """Vuelve a la canción anterior."""
        self.log_command_user(ctx, "back")

        state = await self.validate_music_state(ctx)
        if not state:
            return

        server, voice_client, _ = state

        # Si la reproducción se detuvo y está al final
        if not server.status and server.cplaying == -1:
            server.cplaying = len(server.songs) - 1
            await self.music_manager.play(voice_client, ctx, self.bot)
        # Si puede retroceder
        elif server.cplaying > 0:
            server.cplaying -= 2
            voice_client.stop()

    @commands.command(name="song")
    async def song(self, ctx: commands.Context):
        """Muestra información de la canción actual."""
        self.log_command_user(ctx, "song")

        state = await self.validate_music_state(ctx)
        if not state:
            return

        server, voice_client, lang = state

        if server.cplaying == -1:
            return

        index = server.cplaying
        current_song = server.songs[index - 1]

        # Calcular tiempo restante usando helper
        time_left = self._calculate_remaining_time(server, current_song, voice_client)

        # Crear embed
        embed = discord.Embed(
            title=leng.ar[lang],
            color=0x3498DB,
            description=f"{index}. {current_song.name}",
        )
        embed.add_field(
            name=leng.duracion[lang], value=current_song.length, inline=True
        )
        embed.add_field(name=leng.tr[lang], value=time_left, inline=True)

        await ctx.send(embed=embed)


async def setup(bot):
    """Registra el cog de comandos de reproducción."""
    await bot.add_cog(PlaybackCommand(bot))
