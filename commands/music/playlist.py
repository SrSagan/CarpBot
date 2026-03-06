import discord
from commands.music.base_music import BaseMusicCommand
from discord.ext import commands
import lenguajes as leng
from musica.music import musicManager
import musica.servermanager as sm
import musica.m_queuer


class PlaylistCommand(BaseMusicCommand):
    """Comandos de playlist: save, load, show, remove."""

    def __init__(self, bot):
        super().__init__(bot)
        self.music_manager = musicManager()
        self.server_manager = sm.serverManager()
        self.queuer = musica.m_queuer.queuer()

    @commands.command(name="save_playlist", aliases=["svp"])
    async def save_playlist(self, ctx: commands.Context, *args):
        """Guarda la lista de reproducción actual con un nombre."""
        self.log_command_user(ctx, "save_playlist")

        guild_id = ctx.guild.id
        user_id = ctx.author.id

        if not self.server_manager.exists(guild_id):
            return

        if not args:
            await ctx.send(
                "Especifica un nombre para la playlist ej: `sp nombre_playlist`"
            )
            return

        playlist_name = " ".join(args).strip()

        # TODO: Refactorizar sm.save_playlist para usar servicios modernos
        work = self.server_manager.save_playlist(guild_id, user_id, playlist_name)

        if work == 0:
            await ctx.send("No tienes espacio para más playlists")
        elif work == 2:
            await ctx.send(f"Ya existe una playlist llamada **{playlist_name}**")
        else:
            await ctx.send(f"Playlist **{playlist_name}** guardada ✓")

    @commands.command(name="load_playlist", aliases=["lp", "ldp"])
    async def load_playlist(self, ctx: commands.Context, *args):
        """Carga una playlist guardada en la cola actual."""
        self.log_command_user(ctx, "load_playlist")

        guild_id = ctx.guild.id
        user_id = ctx.author.id
        lang = self.get_language(ctx)

        # Validar que el usuario está en un canal de voz
        if not self.has_permission(ctx):
            await ctx.send(leng.neencdv[lang])
            return

        if not args:
            await ctx.send(
                "Especifica el nombre de la playlist ej: `lp nombre_playlist`"
            )
            return

        playlist_name = " ".join(args).strip()
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        # TODO: Refactorizar sm.load_playlist para usar servicios modernos
        work = self.server_manager.load_playlist(guild_id, user_id, playlist_name)

        if isinstance(work, list):
            # Se cargó la playlist correctamente
            await self.queuer.queuer(work, guild_id)
            await ctx.send(f"Playlist **{playlist_name}** cargada en la cola ✓")

            # Si el bot ya está conectado
            if voice_client and voice_client.is_connected():
                if not voice_client.is_playing():
                    await self.music_manager.play(voice_client, ctx, self.bot)
            # Si necesita conectarse
            elif ctx.author.voice:
                channel = ctx.author.voice.channel
                await channel.connect()
                voice_client = ctx.voice_client
                if not voice_client.is_playing():
                    await self.music_manager.play(voice_client, ctx, self.bot)

        elif work == 0:
            await ctx.send(f"No existe una playlist llamada **{playlist_name}**")
        elif work == 1:
            await ctx.send(f"Playlist **{playlist_name}** cargada pero sin reproducir")

    @commands.command(name="show_playlist", aliases=["sp", "shp"])
    async def show_playlist(self, ctx: commands.Context, *args):
        """Muestra las playlists guardadas o detalles de una específica."""
        self.log_command_user(ctx, "show_playlist")

        user_id = ctx.author.id

        # TODO: Refactorizar sm.show_playlist para usar servicios modernos
        playlists = self.server_manager.show_playlist(user_id)

        if not playlists or playlists == 0:
            await ctx.send("No tienes playlists guardadas")
            return

        # Si se especifica una playlist específica
        if args:
            playlist_name = " ".join(args).strip()
            found_playlist = None

            for playlist in playlists:
                if (
                    playlist.get("name") == playlist_name
                    or playlist.get("name") == args[0]
                ):
                    found_playlist = playlist
                    break

            if found_playlist:
                embed = self.music_manager.print_queue(found_playlist, 1, -1, ctx)
                if embed != 0:
                    # TODO: Mover control_checker a un módulo apropiado
                    import musica.music as f

                    await ctx.send(
                        embed=embed,
                        view=f.control_checker(
                            playlist=found_playlist, arg=1, looping=-1, ctx=ctx
                        ),
                    )
                else:
                    await ctx.send(f"No se pudo cargar la playlist **{playlist_name}**")
            else:
                await ctx.send(f"No encontré una playlist llamada **{playlist_name}**")

        else:
            # Mostrar todas las playlists
            text = ""
            for playlist in playlists:
                songs_count = len(playlist.get("songs", []))
                text += f"**{playlist.get('name', 'Sin nombre')}**\n"
                text += f"{songs_count} canciones\n\n"

            embed = discord.Embed(
                title="Mis Playlists", color=0x3498DB, description=text
            )
            await ctx.send(embed=embed)

    @commands.command(name="remove_playlist", aliases=["rp", "rmpl"])
    async def remove_playlist(self, ctx: commands.Context, *args):
        """Elimina una playlist guardada."""
        self.log_command_user(ctx, "remove_playlist")

        user_id = ctx.author.id

        if not args:
            await ctx.send("Especifica la playlist a eliminar ej: `rp nombre_playlist`")
            return

        playlist_name = " ".join(args).strip()

        # TODO: Refactorizar sm.remove_playlist para usar servicios modernos
        playlists = self.server_manager.show_playlist(user_id)

        if not playlists or playlists == 0:
            await ctx.send("No tienes playlists guardadas")
            return

        found = self.server_manager.remove_playlist(user_id, playlist_name)

        if found == 0:
            await ctx.send(f"No existe una playlist llamada **{playlist_name}**")
        else:
            await ctx.send(f"Playlist **{playlist_name}** eliminada ✓")


async def setup(bot):
    """Registra el cog de comandos de playlist."""
    await bot.add_cog(PlaylistCommand(bot))
