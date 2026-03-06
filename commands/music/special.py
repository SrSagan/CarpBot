import discord
from commands.music.base_music import BaseMusicCommand
from discord.ext import commands
from musica.music import musicManager
import musica.servermanager as sm


class SpecialCommand(BaseMusicCommand):
    """Comandos especiales y memoriales."""

    def __init__(self, bot):
        super().__init__(bot)
        self.music_manager = musicManager()
        self.server_manager = sm.serverManager()

    @commands.command(
        name="estrelheinhas",
        aliases=["es", "juli"],
    )
    async def estrelheinhas(self, ctx: commands.Context):
        """Comando especial dedicado a quien siempre estuvo en el corazón.

        Toca una playlist especial como memorial y recuerdo.
        """
        self.log_command_user(ctx, "estrelheinhas")

        # URL de la playlist memorial
        MEMORIAL_PLAYLIST_URL = (
            "https://www.youtube.com/playlist?list=PLT5RzA2p1DMdJSacPMujx1qaFXqMgxnHe"
        )

        # Validar permisos
        if not self.has_permission(ctx):
            lang = self.get_language(ctx)
            from lenguajes import lenguajes as leng

            await ctx.send(leng.neencdv[lang])
            return

        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        # Si el bot ya está conectado
        if voice_client and voice_client.is_connected():
            await self.music_manager.queuer(ctx, MEMORIAL_PLAYLIST_URL, "yt")
            if not voice_client.is_playing():
                await self.music_manager.play(voice_client, ctx, self.bot)

        # Si necesita conectarse
        elif ctx.author.voice:
            await self.music_manager.queuer(ctx, MEMORIAL_PLAYLIST_URL, "yt")
            channel = ctx.author.voice.channel
            await channel.connect()
            voice_client = ctx.voice_client

            if not voice_client.is_playing():
                await self.music_manager.play(voice_client, ctx, self.bot)


async def setup(bot):
    """Registra el cog de comandos especiales."""
    await bot.add_cog(SpecialCommand(bot))
