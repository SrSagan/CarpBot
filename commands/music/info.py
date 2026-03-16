import discord
from commands.music.base_music import BaseMusicCommand
from discord.ext import commands
from musica.managers.server_manager import ServerManager
from musica.services.music_service import MusicService
import os
from dotenv import load_dotenv
from lyricsgenius import Genius


class InfoCommand(BaseMusicCommand):
    """Comandos de información: lyrics, videoinfo."""

    def __init__(self, bot):
        super().__init__(bot)
        self.music_manager = MusicService()
        self.server_manager = ServerManager()
        
        # Inicializar Genius para búsqueda de letras
        load_dotenv()
        lyrics_token = os.getenv("LYRICS")
        self.genius = Genius(lyrics_token) if lyrics_token else None

    @commands.command(name="lyrics", aliases=["letra", "lyr"])
    async def lyrics(self, ctx: commands.Context, *args):
        """Busca y muestra las letras de una canción."""
        self.log_command_user(ctx, "lyrics")

        if not self.genius:
            await ctx.send("🔴 No se pudo inicializar el servicio de letras")
            return

        guild_id = ctx.guild.id

        # Determinar término de búsqueda
        if args:
            search_term = " ".join(args)
        else:
            # Usar la canción actual si está disponible
            if not self.server_manager.exists(guild_id):
                await ctx.send("No hay canción actual en reproducción")
                return

            server = self.server_manager.get_server(guild_id)
            if server.current_song_index == -1:
                await ctx.send("No hay canción actual seleccionada")
                return

            current_song = server.songs[server.current_song_index - 1]
            search_term = current_song.name

        try:
            # Buscar canciones
            search_results = self.genius.search_songs(search_term)
            hits = search_results.get("hits", [])

            if not hits:
                await ctx.send(f"No se encontraron resultados para '{search_term}'")
                return

            # Limitar a 10 resultados
            hits = hits[:10]

            # Crear embed con opciones
            embed = discord.Embed(
                title=f"Búsqueda: {search_term}",
                color=0x3498DB,
                description="Selecciona un resultado (número 1-10):\n",
            )

            songs_data = []
            for idx, hit in enumerate(hits, 1):
                result = hit["result"]
                title = result["title"]
                artist = result["primary_artist"]["name"]
                song_id = result["id"]

                songs_data.append({"id": song_id, "title": title, "artist": artist})
                embed.add_field(
                    name=f"{idx}. {title}",
                    value=f"Artista: {artist}",
                    inline=False,
                )

            await ctx.send(embed=embed)

            # Esperar respuesta del usuario
            try:
                msg = await self.bot.wait_for(
                    "message",
                    check=lambda m: m.author == ctx.author,
                    timeout=60.0,
                )
            except discord.ext.commands.CommandError:
                await ctx.send("Tiempo agotado para seleccionar una canción")
                return

            # Procesar selección
            if msg.content.lower() == "cancel":
                await ctx.send("Búsqueda cancelada")
                return

            if msg.content.isdigit():
                choice = int(msg.content)
                if 1 <= choice <= len(songs_data):
                    selected_song = songs_data[choice - 1]
                    song = self.genius.search_song(song_id=selected_song["id"])

                    if not song or not song.lyrics:
                        await ctx.send("No se pudieron obtener las letras de esta canción")
                        return

                    # Limpiar texto embedido
                    lyrics_text = song.lyrics
                    embed_idx = lyrics_text.lower().rfind("embed")

                    if embed_idx != -1:
                        # Limpiar números antes de "embed"
                        idx = embed_idx - 1
                        while idx >= 0 and lyrics_text[idx].isdigit():
                            idx -= 1
                        lyrics_text = lyrics_text[: idx + 1]

                    # Dividir en páginas de 4000 caracteres
                    lyrics_pages = []
                    while len(lyrics_text) > 4000:
                        split_idx = lyrics_text[:4000].rfind("\n")
                        if split_idx == -1:
                            split_idx = 4000
                        lyrics_pages.append(lyrics_text[:split_idx])
                        lyrics_text = lyrics_text[split_idx:]

                    if lyrics_text:
                        lyrics_pages.append(lyrics_text)

                    # Enviar páginas
                    for page in lyrics_pages:
                        embed = discord.Embed(
                            title=f"{selected_song['title']} - {selected_song['artist']}",
                            color=0x3498DB,
                            description=page,
                        )
                        if hasattr(song, "header_image_url") and song.header_image_url:
                            embed.set_thumbnail(url=song.header_image_url)
                        await ctx.send(embed=embed)
                else:
                    await ctx.send("Número de selección inválido")
            else:
                await ctx.send("Respuesta inválida. Usa un número o 'cancel'")

        except Exception as e:
            await ctx.send(
                f"Error al buscar letras: {str(e)[:100]}"
            )

    @commands.command(name="videoinfo", aliases=["vi", "vinf"])
    async def videoinfo(self, ctx: commands.Context, *args):
        """Muestra información del video/canción actual o especificado."""
        self.log_command_user(ctx, "videoinfo")

        guild_id = ctx.guild.id

        song_index = None

        # Si se proporciona un índice
        if args:
            if args[0].isdigit():
                song_index = int(args[0])
            else:
                await ctx.send("Por favor especifica el número de la canción")
                return
        else:
            # Usar canción actual
            if not self.server_manager.exists(guild_id):
                return

            server = self.server_manager.get_server(guild_id)
            song_index = server.current_song_index

        embed = await self.music_manager.get_video_info(guild_id, ctx, song_index)

        if isinstance(embed, str):
            # Es un mensaje de error
            await ctx.send(embed)
        else:
            # Es un embed
            await ctx.send(embed=embed)


async def setup(bot):
    """Registra el cog de comandos de información."""
    await bot.add_cog(InfoCommand(bot))
