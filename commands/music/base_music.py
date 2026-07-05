from discord.ext import commands
from commands.base.base_command import UserCommand
from utils.permissions import is_dev_user
import lenguajes as leng
from typing import Optional, Tuple
import discord


class BaseMusicCommand(UserCommand):
    """Clase base para comandos de música."""

    def __init__(self, bot):
        super().__init__(bot)
        self.music_manager = None  # Inicializar en clases hijas
        self.server_manager = None  # Inicializar en clases hijas

    async def check_voice_channel(self, ctx: commands.Context) -> bool:
        """Verifica si el usuario está en un canal de voz."""
        if not ctx.author.voice:
            lang = self.get_language(ctx)
            await ctx.send(leng.neencdv[lang])
            return False
        return True

    async def check_bot_connected(self, ctx: commands.Context) -> bool:
        """Verifica si el bot está conectado a un canal de voz."""
        return ctx.voice_client is not None

    def has_permission(self, ctx: commands.Context) -> bool:
        """Verifica si el usuario tiene permiso para usar el comando."""
        return ctx.author.voice is not None or is_dev_user(ctx.author.id)

    async def validate_music_state(
        self, ctx: commands.Context, require_server: bool = True
    ) -> Optional[Tuple[any, discord.VoiceClient, int]]:
        """
        Valida el estado completo para comandos de música.

        Args:
            ctx: Contexto del comando
            require_server: Si se requiere que exista un servidor en la cola

        Returns:
            Tupla (server, voice_client, lang) si todo es válido, None si falta algo
        """
        # Validar permisos
        if not self.has_permission(ctx):
            lang = self.get_language(ctx)
            await ctx.send(leng.neencdv[lang])
            return None

        # Validar voice_client
        voice_client = ctx.voice_client
        if not voice_client:
            return None

        lang = self.get_language(ctx)

        # Si no se requiere servidor, retornar solo voice_client
        if not require_server:
            return None, voice_client, lang

        # Validar que existe el servidor
        if not self.server_manager:
            return None

        guild_id = ctx.guild.id
        if not self.server_manager.exists(guild_id):
            return None

        server = self.server_manager.get_server(guild_id)

        return server, voice_client, lang


async def setup(bot):
    """Configura la base de comandos de música."""
    await bot.add_cog(BaseMusicCommand(bot))
