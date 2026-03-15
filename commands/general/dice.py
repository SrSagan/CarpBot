import random
from commands.base.base_command import UserCommand
from discord.ext import commands


class DiceCommand(UserCommand):
    """Comandos de dados - Disponible para todos."""

    @commands.command(name="dado")
    async def dado(self, ctx: commands.Context):
        """Lanza un dado de 6 caras."""
        self.log_command_user(ctx, "dado")

        result = random.randrange(1, 6)
        await ctx.send(f"🎲 Has lanzado un dado y ha salido: **{result}**")


async def setup(bot):
    """Configura el comando de dados."""
    await bot.add_cog(DiceCommand(bot))