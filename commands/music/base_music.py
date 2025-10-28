from discord.ext import commands
from commands.base.base_command import UserCommand
from utils.permissions import is_dev_user
import lenguajes as leng

class BaseMusicCommand(UserCommand):
    """Clase base para comandos de música."""

    def __init__(self, bot):
        super().__init__(bot)
        self.music_manager = None # Inicializar en setup

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