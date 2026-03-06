import discord
from commands.base.base_command import UserCommand
from discord.ext import commands
import lenguajes as leng
from services.link_service import LinkService
from typing import Optional


class LinksCommand(UserCommand):
    """Comandos de gestión de links - Agregar y remover links de grupos."""

    def __init__(self, bot):
        super().__init__(bot)
        self.link_service = LinkService()

    async def _select_group(self, ctx: commands.Context, lang: int) -> Optional[str]:
        """
        Solicita al usuario que seleccione un grupo.

        Returns:
            Nombre del grupo seleccionado o None si se cancela
        """
        # Mostrar grupos disponibles
        group_names = self.link_service.get_all_group_names()
        groups_text = "\n".join([f"• {name}" for name in group_names])

        await ctx.send(leng.eqgqael[lang])
        embed = discord.Embed(
            title=leng.grupos[lang], color=0x3498DB, description=groups_text
        )
        await ctx.send(embed=embed)

        # TODO: Agregar timeout a wait_for para evitar que el bot se cuelgue
        # Esperar respuesta del usuario
        msg = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author)

        if msg.content.lower() == "cancel":
            return None

        # Validar que el grupo existe
        if msg.content.lower() in group_names:
            return msg.content.lower()

        await ctx.send(leng.gi[lang])
        return None

    def _validate_link_format(self, link: str, is_exception: bool) -> bool:
        """
        Valida el formato de un link.

        Args:
            link: URL a validar
            is_exception: Si True, acepta cualquier formato

        Returns:
            True si es válido, False en caso contrario
        """
        if is_exception:
            return True

        # Buscar extensión del archivo
        # TODO: Mejorar validación usando urllib.parse en lugar de rfind
        x = link.rfind(".")
        y = link.rfind("?")

        if x != -1:
            if y != -1:
                formato = link[x:y]
            else:
                formato = link[x:]

            # Verificar formato soportado o YouTube
            supported_formats = self.link_service.get_supported_formats()
            if formato not in supported_formats and link.find("youtu") == -1:
                return False
        else:
            # No hay extensión
            return False

        return True

    @commands.command(name="addlink", aliases=["al"])
    async def add_link(self, ctx: commands.Context, *args):
        """
        Agrega links a un grupo de imágenes.

        Modos:
        - Normal: addlink <url1> <url2>...
        - Exception: addlink exception <url> (acepta cualquier formato)
        - Continue: addlink continue (espera imágenes adjuntas hasta 'end')
        """
        self.log_command_user(ctx, "addlink")
        lang = self.get_language(ctx)

        if not args:
            await ctx.send(leng.eulopjcec[lang])
            return

        # Determinar modo de operación
        mode = args[0].lower()
        is_exception = mode == "exception"
        is_continue = mode == "continue"

        # Validar formato de los links (excepto en modo exception o continue)
        if not is_continue:
            for arg in args:
                if not self._validate_link_format(arg, is_exception):
                    if arg.find(".") == -1:
                        await ctx.send(leng.lnkinv[lang])
                    else:
                        await ctx.send(leng.fi[lang])
                    return

        # Seleccionar grupo
        selected_group = await self._select_group(ctx, lang)
        if selected_group is not None:
            # Verificar que se devolvió un grupo válido
            group = self.link_service.get_group_by_name(selected_group)
            if not group:
                return

            # Cargar links del grupo
            self.link_service.load_links(group)

            links_added = 0

            # Modo CONTINUE: esperar imágenes adjuntas
            if is_continue:
                await ctx.send(leng.ei[lang])

                while True:
                    # TODO: Agregar timeout a wait_for
                    msg = await self.bot.wait_for(
                        "message", check=lambda m: m.author == ctx.author
                    )

                    if msg.content.lower() == "end":
                        await ctx.send(leng.terminado[lang])
                        break

                    # Procesar adjuntos
                    for attachment in msg.attachments:
                        img_url = attachment.url

                        # Verificar si ya existe
                        if img_url in group.data or f"{img_url}\n" in group.data:
                            await ctx.send(leng.elyeell[lang])
                            continue

                        # Agregar link
                        self.link_service.add_link(selected_group, img_url)
                        links_added += 1

            # Modo EXCEPTION o NORMAL
            else:
                for arg in args:
                    # En modo exception, saltar el primer argumento
                    if is_exception and arg == args[0]:
                        continue

                    # Verificar si ya existe
                    if arg in group.data or f"{arg}\n" in group.data:
                        await ctx.send(leng.elyeell[lang])
                        return

                    # Agregar link
                    self.link_service.add_link(selected_group, arg)
                    links_added += 1

            # Mensaje de confirmación
            if links_added == 1:
                await ctx.send(
                    f"{links_added} {leng.laa_lsaa[lang][0]} '{selected_group}'"
                )
            elif links_added > 1:
                await ctx.send(
                    f"{links_added} {leng.laa_lsaa[lang][1]} '{selected_group}'"
                )

    @commands.command(name="removelink", aliases=["rl"])
    async def removelink(self, ctx: commands.Context, *args):
        """
        Remueve links de grupos de imágenes.

        Uso: removelink <url1> <url2>...
        """
        self.log_command_user(ctx, "removelink")
        lang = self.get_language(ctx)

        if not args:
            await ctx.send(leng.eeldlijcec[lang])
            return

        # Contador de links removidos por grupo
        removed_by_group = {}

        # Intentar remover cada link de todos los grupos
        for link in args:
            found = False

            for group in self.link_service.link_groups:
                # Cargar links del grupo
                if not group.data:
                    self.link_service.load_links(group)

                # Verificar si el link existe (con o sin \n)
                link_clean = link.strip()
                link_with_newline = f"{link_clean}\n"

                if link_clean in group.data or link_with_newline in group.data:
                    # Intentar remover
                    success = self.link_service.remove_link(group.name, link_clean)

                    if success:
                        if group.name not in removed_by_group:
                            removed_by_group[group.name] = 0
                        removed_by_group[group.name] += 1
                        found = True

            # Si no se encontró el link en ningún grupo
            if not found:
                await ctx.send(
                    f"{leng.el_nseeng[lang][0]} '{link}' {leng.el_nseeng[lang][1]}"
                )

        # Mostrar resumen por grupo
        for group_name, count in removed_by_group.items():
            if count == 1:
                await ctx.send(f"{count} {leng.lrd_lsrd[lang][0]} '{group_name}'")
            elif count > 1:
                await ctx.send(f"{count} {leng.lrd_lsrd[lang][1]} '{group_name}'")


async def setup(bot):
    """Configura los comandos de links."""
    await bot.add_cog(LinksCommand(bot))
