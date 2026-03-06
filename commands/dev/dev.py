import subprocess
import discord
from commands.base.base_command import DevCommand
from discord.ext import commands
from services.link_service import LinkService


class DevCommands(DevCommand):
    """Comandos de desarrollador - Solo para devs."""

    def __init__(self, bot):
        super().__init__(bot)
        self.link_service = LinkService()

    @commands.command(name="debug_images", aliases=["di"])
    async def debug_images(self, ctx: commands.Context, *args):
        """
        Muestra todas las imágenes de un grupo específico.

        ⚠️ ADVERTENCIA: Este comando puede enviar muchos mensajes.
        Úsalo con cuidado para no saturar el canal.

        Uso: debug_images <nombre_grupo>
        """
        self.log_command_user(ctx, "debug_images")

        # Verificar permisos
        if not await self.check_permissions(ctx):
            return

        if not args:
            await ctx.send(
                "Especifica el nombre del grupo. Ej: `debug_images carpincho`"
            )
            return

        group_name = args[0].lower()

        # Obtener el grupo
        group = self.link_service.get_group_by_name(group_name)

        if not group:
            await ctx.send(f"❌ Grupo '{group_name}' no encontrado.")
            return

        # Cargar links del grupo
        self.link_service.load_links(group)

        if not group.data:
            await ctx.send(f"📭 El grupo '{group_name}' está vacío.")
            return

        # Advertencia antes de enviar
        await ctx.send(
            f"⚠️ Se enviarán **{len(group.data)}** links del grupo **{group_name}**.\n"
            f"Esto puede tomar tiempo y saturar el canal."
        )

        # Enviar todos los links
        for link in group.data:
            await ctx.send(str(link).strip())

        await ctx.send(
            f"✅ Se enviaron {len(group.data)} links del grupo '{group_name}'."
        )

    @commands.command(name="ip")
    async def ip(self, ctx: commands.Context):
        """
        Muestra la dirección IP pública del servidor donde corre el bot.

        Solo disponible para desarrolladores.
        """
        self.log_command_user(ctx, "ip")

        # Verificar permisos
        if not await self.check_permissions(ctx):
            return

        try:
            # TODO: Reemplazar comando dig con requests a https://api.ipify.org
            # El comando dig es específico de Linux/Unix y puede no estar disponible en Windows
            command = "dig +short myip.opendns.com @resolver1.opendns.com"

            process = subprocess.Popen(
                command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            output, error = process.communicate()

            if error:
                await ctx.send(f"❌ Error al obtener IP: {error.decode()}")
                return

            # Parsear la salida
            ip_str = output.decode().strip()

            if ip_str:
                embed = discord.Embed(
                    title="🌐 IP del Servidor",
                    description=f"**IP:** `{ip_str}`",
                    color=0x3498DB,
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ No se pudo obtener la IP del servidor.")

        except Exception as e:
            await ctx.send(f"❌ Error al ejecutar el comando: {str(e)}")

    @commands.command(name="debug")
    async def debug(self, ctx: commands.Context, *args):
        """
        Panel de debug con controles interactivos.

        Muestra un panel con botones de navegación para debugging.
        Solo disponible para desarrolladores.
        """
        self.log_command_user(ctx, "debug")

        # Verificar permisos
        if not await self.check_permissions(ctx):
            return

        # Crear vista con controles
        view = DebugControlPanel()

        embed = discord.Embed(
            title="🔧 Panel de Debug",
            description="Usa los botones para navegar",
            color=0xE74C3C,
        )

        await ctx.send(embed=embed, view=view)


class DebugControlPanel(discord.ui.View):
    """Panel de control de debug con botones de navegación."""

    def __init__(self, *, timeout=800):
        super().__init__(timeout=timeout)
        self.current_page = 0

    @discord.ui.button(label="◄◄", style=discord.ButtonStyle.gray)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Ir al inicio."""
        self.current_page = 0
        await interaction.response.edit_message(
            content=f"📍 Página: {self.current_page} (Inicio)"
        )

    @discord.ui.button(label="◄", style=discord.ButtonStyle.gray)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retroceder una página."""
        if self.current_page > 0:
            self.current_page -= 1
        await interaction.response.edit_message(
            content=f"📍 Página: {self.current_page}"
        )

    @discord.ui.button(label="►", style=discord.ButtonStyle.gray)
    async def forward(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """Avanzar una página."""
        self.current_page += 1
        await interaction.response.edit_message(
            content=f"📍 Página: {self.current_page}"
        )

    @discord.ui.button(label="►►", style=discord.ButtonStyle.gray)
    async def end(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Ir al final."""
        self.current_page = 999
        await interaction.response.edit_message(
            content=f"📍 Página: {self.current_page} (Final)"
        )


async def setup(bot):
    """Configura los comandos de desarrollador."""
    await bot.add_cog(DevCommands(bot))
