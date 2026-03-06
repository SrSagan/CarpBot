import discord
from commands.base.base_command import AdminCommand
from discord.ext import commands
import lenguajes as leng
from services.server_config_service import ServerConfigService


class ConfigCommand(AdminCommand):
    """Comandos de configuración del servidor - Requiere permisos de admin."""

    def __init__(self, bot):
        super().__init__(bot)
        self.config_service = ServerConfigService()

    @commands.command(name="changeprefix", aliases=["cp"])
    async def changeprefix(self, ctx: commands.Context, *args):
        """Cambia el prefijo del bot en el servidor."""
        self.log_command_user(ctx, "changeprefix")

        # Verificar permisos
        if not await self.check_permissions(ctx):
            return

        lang = self.get_language(ctx)
        current_prefix = self.get_prefix(ctx)

        # Crear embed con el prefijo actual
        embed = discord.Embed(title=leng.cp[lang], color=0x3498DB)
        embed.add_field(name=leng.pa[lang], value=f"**{current_prefix}**")

        # Solicitar el nuevo prefijo
        # TODO: Agregar timeout a wait_for para evitar que el bot se cuelgue indefinidamente
        await ctx.send(leng.eunp[lang])
        message = await self.bot.wait_for(
            "message", check=lambda m: m.author == ctx.author
        )

        new_prefix = message.content

        # Permitir cancelación
        if new_prefix.lower() == "cancel":
            await ctx.send(leng.oc[lang])
            return

        # Actualizar prefijo
        self.config_service.set_prefix(ctx.guild.id, new_prefix)

        # Mostrar confirmación
        embed.add_field(name=leng.np[lang], value=f"**{new_prefix}**")
        await ctx.send(embed=embed)

    @commands.command(name="changelenguage", aliases=["cl"])
    async def changelenguage(self, ctx: commands.Context, *args):
        """Cambia el idioma del bot en el servidor."""
        self.log_command_user(ctx, "changelenguage")

        # Verificar permisos
        if not await self.check_permissions(ctx):
            return

        lang = self.get_language(ctx)
        # TODO: Mover valid_languages a constants.py
        valid_languages = ["EN", "ES", "PT"]

        # Si se proporciona directamente el idioma
        if args and args[0].upper() in valid_languages:
            new_language = args[0].upper()
        else:
            # Solicitar el idioma
            embed = discord.Embed(title=leng.cel[lang], color=0x3498DB)
            embed.add_field(name=leng.eul[lang], value=leng.pei[lang])
            await ctx.send(embed=embed)

            # TODO: Agregar timeout a wait_for
            message = await self.bot.wait_for(
                "message", check=lambda m: m.author == ctx.author
            )
            new_language = message.content.upper()

        # Permitir cancelación
        if new_language == "CANCEL":
            await ctx.send(leng.oc[lang])
            return

        # Validar idioma
        if new_language in valid_languages:
            self.config_service.set_language(ctx.guild.id, new_language)
            await ctx.send(f"{leng.lca[lang]} {new_language}")
        else:
            await ctx.send(leng.li[lang])


async def setup(bot):
    """Configura los comandos de configuración."""
    await bot.add_cog(ConfigCommand(bot))
