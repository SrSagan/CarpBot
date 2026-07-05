import discord
from commands.base.base_command import UserCommand
from discord.ext import commands
import lenguajes as leng


class HelpCommand(UserCommand):
    """Comando de ayuda - Muestra los comandos disponibles."""

    @commands.command(name="help", aliases=["h"])
    async def help(self, ctx: commands.Context, *args):
        """Muestra la ayuda con todos los comandos disponibles."""
        self.log_command_user(ctx, "help")
        lang = self.get_language(ctx)

        embed = discord.Embed(title="Help", color=0x3498DB)

        # Obtener el texto de ayuda según el idioma
        help_text = leng.help[lang]

        # TODO: Reemplazar formato legacy ##Titulo-Contenido con JSON/YAML estructurado
        # Parsear el texto de ayuda
        # Formato esperado: ##Título-Contenido##Título-Contenido...
        while True:
            x = help_text.find("##")
            if x == -1:
                break

            # Encontrar el separador entre título y contenido
            y = help_text.find("-")
            if y == -1:
                break

            # Extraer el nombre del comando
            name = help_text[x + 2 : y]
            help_text = help_text[y + 1 :]

            # Encontrar el siguiente ##
            x = help_text.find("##")
            if x == -1:
                # Último campo
                value = help_text
                help_text = ""
            else:
                # Extraer el valor hasta el siguiente ##
                value = help_text[:x]
                help_text = help_text[x:]

            # Agregar el campo al embed
            embed.add_field(name=name, value=value, inline=False)

            # Si ya no queda texto, salir
            if not help_text:
                break

        await ctx.send(embed=embed)


async def setup(bot):
    """Configura el comando de ayuda."""
    await bot.add_cog(HelpCommand(bot))
