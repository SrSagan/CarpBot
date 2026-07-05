import random

import discord
from commands.base.base_command import UserCommand
from discord.ext import commands
import lenguajes as len


class EightBallCommand(UserCommand):
    """Comando de bola 8 - Disponible para todos."""

    @commands.command(
        name="bola8",
        aliases=["8b"],
    )
    async def eightball(self, ctx: commands.Context, *args):
        """Responde a una pregunta con una respuesta aleatoria de bola 8."""
        self.log_command_user(ctx, "bola8")

        embed = discord.Embed(title="🎱 Bola 8 mágica.", color=0x3498DB)

        texto_pregunta = " ".join(args).strip()
        embed.add_field(
            name=len.p_r[self.get_language(ctx)][0], value=texto_pregunta, inline=False
        )

        respuestas = len.Respuestas8ball[self.get_language(ctx)]
        embed.add_field(
            name=len.p_r[self.get_language(ctx)][1],
            value=random.choice(respuestas),
            inline=False,
        )

        await ctx.send(embed=embed)


async def setup(bot):
    """Configura el comando de bola 8."""
    await bot.add_cog(EightBallCommand(bot))
