import discord
from commands.music.base_music import BaseMusicCommand
from discord.ext import commands
import lenguajes as leng
from musica.managers.server_manager import ServerManager
from musica.services.music_service import ControlChecker, MusicService


class QueueCommand(BaseMusicCommand):
    """Comandos de gestión de cola: queue, clear, remove, move, shuffle, loop, search."""

    def __init__(self, bot):
        super().__init__(bot)
        self.music_manager = MusicService()
        self.server_manager = ServerManager()

    @commands.command(name="queue", aliases=["q"])
    async def queue(self, ctx: commands.Context, *args):
        """Muestra la cola de reproducción."""
        self.log_command_user(ctx, "queue")

        guild_id = ctx.guild.id

        if not self.server_manager.exists(guild_id):
            return

        playlist = self.server_manager.get_server(guild_id)
        looping = playlist.loop_mode

        # Corregir looping para display
        if looping == 0:
            looping = 2
        elif looping == 1:
            looping = 0
        elif looping == 2:
            looping = 1

        # Calcular página actual
        arg = int((playlist.current_song_index - 1) / 10) + 1
        if arg < 1:
            arg = 1
        if playlist.current_song_index > len(playlist.songs) - 1:
            arg = -1

        # Si se especifica una página
        if args and args[0].isnumeric():
            arg = int(args[0])

        embed = self.music_manager.print_queue(playlist, arg, looping, ctx)

        if embed != 0:
            await ctx.send(
                embed=embed,
                view=ControlChecker(
                    playlist=playlist, arg=arg, looping=looping, ctx=ctx
                ),
            )
        else:
            await ctx.send("Page out of range")

    @commands.command(name="clear", aliases=["c"])
    async def clear(self, ctx: commands.Context):
        """Limpia toda la cola de reproducción."""
        self.log_command_user(ctx, "clear")

        # Validar permisos
        if not self.has_permission(ctx):
            lang = self.get_language(ctx)
            await ctx.send(leng.neencdv[lang])
            return

        guild_id = ctx.guild.id
        voice_client = ctx.voice_client

        if not self.server_manager.exists(guild_id):
            return

        voice_client.stop()
        self.server_manager.clear(guild_id)

        lang = self.get_language(ctx)
        await ctx.send(leng.pv[lang])

    @commands.command(name="remove", aliases=["rm"])
    async def remove(self, ctx: commands.Context, *args):
        """Remueve una canción de la cola."""
        self.log_command_user(ctx, "remove")

        state = await self.validate_music_state(ctx)
        if not state:
            return

        server, voice_client, lang = state

        if not args:
            await ctx.send(leng.eenducar[lang])
            return

        deleted = None

        # Remover por índice numérico
        if args[0].isnumeric():
            index = int(args[0])
            if index <= len(server.songs) and index > 0:
                deleted = index - 1
                song = server.songs[deleted]

                embed = discord.Embed(
                    title=leng.removido[lang], color=0x3498DB, description=song.name
                )
                embed.set_footer(text=f"{leng.duracion[lang]}{song.length}")
                await ctx.send(embed=embed)
            else:
                await ctx.send(leng.cfdr[lang])
                return
        # Remover última canción
        elif args[0] == "last":
            deleted = len(server.songs) - 1
            song = server.songs[deleted]

            embed = discord.Embed(
                title=leng.removido[lang], color=0x3498DB, description=song.name
            )
            embed.set_footer(text=f"{leng.duracion[lang]}{song.length}")
            await ctx.send(embed=embed)
        else:
            await ctx.send(leng.eenduc[lang])
            return

        # Eliminar la canción
        server.songs.pop(deleted)

        # Ajustar índice de reproducción
        if deleted == server.current_song_index - 1:
            # Si es la canción actual
            if deleted == len(server.songs):
                # Si es la última, retroceder
                server.current_song_index = max(0, server.current_song_index - 2)
                voice_client.stop()
            else:
                # Reproducir la siguiente (que ahora está en la posición actual)
                server.current_song_index -= 1
                voice_client.stop()
        elif deleted < server.current_song_index:
            # Si se elimina antes de la canción actual, ajustar índice
            server.current_song_index -= 1

    @commands.command(name="move", aliases=["m"])
    async def move(self, ctx: commands.Context, *args):
        """Mueve una canción de una posición a otra."""
        self.log_command_user(ctx, "move")

        state = await self.validate_music_state(ctx)
        if not state:
            return

        server, _, lang = state

        if len(args) < 2:
            await ctx.send(leng.ecyl[lang])
            return

        # Validar que ambos argumentos son numéricos
        if not (args[0].isnumeric() and args[1].isnumeric()):
            await ctx.send(leng.eqcpmyadm[lang])
            return

        from_index = int(args[0])
        to_index = int(args[1])

        # Validar rangos
        if not (
            0 < from_index <= len(server.songs) and 0 < to_index <= len(server.songs)
        ):
            await ctx.send(leng.cfdr[lang])
            return

        # Realizar el movimiento
        moving_song = server.songs[from_index - 1]
        server.songs.pop(from_index - 1)
        server.songs.insert(to_index - 1, moving_song)

        # Ajustar índice de reproducción si es necesario
        if to_index <= server.current_song_index:
            server.current_song_index += 1

        embed = discord.Embed(
            title="Song moved",
            color=0x3498DB,
            description=f"{moving_song.name} moved to position {to_index}",
        )
        await ctx.send(embed=embed)

    @commands.command(name="shuffle", aliases=["sh"])
    async def shuffle(self, ctx: commands.Context):
        """Mezcla aleatoriamente la cola de reproducción."""
        self.log_command_user(ctx, "shuffle")

        self.music_manager.shuffler(ctx)

        lang = self.get_language(ctx)
        await ctx.send(leng.mm[lang])

    @commands.command(name="loop", aliases=["lup"])
    async def loop(self, ctx: commands.Context):
        """Cambia el modo de repetición (ninguno, canción, lista)."""
        self.log_command_user(ctx, "loop")

        guild_id = ctx.guild.id
        lang = self.get_language(ctx)

        if not self.server_manager.exists(guild_id):
            return

        server = self.server_manager.get_server(guild_id)

        # Rotar entre modos de loop: 0 (ninguno) → 1 (canción) → 2 (lista) → 0
        if server.loop_mode == 0:
            server.loop_mode = 1
            index = 0  # Loop en canción actual
        elif server.loop_mode == 1:
            server.loop_mode = 2
            index = 1  # Loop en toda la lista
        elif server.loop_mode == 2:
            server.loop_mode = 0
            index = 2  # Sin loop

        embed = discord.Embed(description=leng.arlq_ca_d[lang][index], color=0x3498DB)
        await ctx.send(embed=embed)

    @commands.command(name="search", aliases=["sr", "srch"])
    async def search(self, ctx: commands.Context, *args):
        """Busca canciones en la cola actual por nombre."""
        self.log_command_user(ctx, "search")

        guild_id = ctx.guild.id
        lang = self.get_language(ctx)

        if not args:
            await ctx.send("Especifica qué buscar ej: `search nombre_canción`")
            return

        if not self.server_manager.exists(guild_id):
            return

        server = self.server_manager.get_server(guild_id)
        search_term = args[0].lower()
        results = []
        max_results = 10

        # Buscar en todas las canciones
        for idx, song in enumerate(server.songs, 1):
            song_name = song.name.lower()
            if search_term in song_name:
                results.append((idx, song))
                if len(results) >= max_results:
                    break

        if results:
            text = ""
            for position, song in results:
                text += f"\n**{position})** {song.name} *({leng.duracion[lang]}: {song.length})*"

            embed = discord.Embed(
                title="Canciones encontradas", color=0x3498DB, description=text
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"No se encontraron canciones con '{args[0]}'")


async def setup(bot):
    """Registra el cog de comandos de cola."""
    await bot.add_cog(QueueCommand(bot))
