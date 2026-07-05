import discord
from commands.base.base_command import UserCommand
from discord.ext import commands
import lenguajes as leng
from services.link_service import LinkService


# TODO: Mover GROUP_ALIASES a constants.py y generar dinámicamente desde LINK_GROUPS_CONFIG
# TODO: Refactorizar para evitar duplicación con utils/constants.py
# Mapeo de aliases a nombres de grupos
GROUP_ALIASES = {
    "carplinks": ["carp", "capybara", "capivara", "carpincho"],
    "rayllumlinks": ["rayllum"],
    "tdplinks": ["tdp"],
    "avatarlinks": ["avatar", "atla"],
    "memelinks": ["meme"],
    "owlinks": ["owl", "buho"],
    "csmlinks": ["csm", "chainsawman"],
    "catlinks": ["cat", "gatinho", "gatito", "kitty", "gato"],
    "ducklinks": ["duck", "pato", "quack", "patito", "fuck", "ducky"],
}

# Crear lista de aliases (todos excepto 'carpincho' que es el nombre principal)
aliases = []
for grupo in GROUP_ALIASES:
    for alias in GROUP_ALIASES[grupo]:
        if alias != "carpincho":
            aliases.append(alias)


class ImagesCommand(UserCommand):
    """Comandos de imágenes - Muestra imágenes aleatorias de diferentes grupos."""

    def __init__(self, bot):
        super().__init__(bot)
        self.link_service = LinkService()
        self.group_aliases = GROUP_ALIASES

    @commands.command(name="carpincho", aliases=aliases)
    async def images(self, ctx: commands.Context):
        """Muestra una imagen aleatoria del grupo especificado."""
        prefix = self.get_prefix(ctx)
        command = ctx.message.content[len(prefix) :].lower().strip()

        # Buscar en qué grupo se encuentra el comando
        group_name = None
        for grupo, alias_list in self.group_aliases.items():
            if command in alias_list:
                # Obtener el nombre del grupo (sin el sufijo 'links')
                group_name = grupo.replace("links", "")
                self.log_command_user(ctx, command)
                break

        if not group_name:
            return

        # Obtener un link aleatorio del grupo
        response = self.link_service.get_random_link(group_name)

        if not response:
            await ctx.send(f"No hay imágenes disponibles en el grupo {group_name}")
            return

        # TODO: Mejorar detección de tipo de archivo usando URL parsing o extensiones
        # Verificar si es un video o una imagen
        if response.rfind("mp4") > -1 or response.rfind("youtu") > -1:
            # Enviar como texto si es video o youtube
            await ctx.send(response)
        else:
            # Crear embed para imágenes
            embed = discord.Embed(color=0x3498DB)
            embed.set_image(url=response)
            await ctx.send(embed=embed)

    @commands.command(name="grupos", aliases=["groups"])
    async def grupos(self, ctx: commands.Context):
        """Muestra todos los grupos de imágenes con el número de elementos en cada uno."""
        self.log_command_user(ctx, "grupos")
        lang = self.get_language(ctx)

        # Obtener todos los grupos
        texto = ""
        for group in self.link_service.link_groups:
            # Cargar los links del grupo si no están cargados
            if not group.data:
                self.link_service.load_links(group)

            count = len(group.data)
            texto += f"{group.name}: {count}\n"

        # Crear embed
        embed = discord.Embed(
            color=0x3498DB, title=leng.grupos[lang], description=texto
        )

        await ctx.send(embed=embed)


async def setup(bot):
    """Configura los comandos de imágenes."""
    await bot.add_cog(ImagesCommand(bot))
