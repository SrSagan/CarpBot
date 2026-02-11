import discord
from discord.ext import commands
from commands.music.base_music import BaseMusicCommand
import lenguajes as leng
import musica.servermanager as sm

class PlayListCommand(BaseMusicCommand):
	"""Comandos de lista de reproducción: create, add, remove, show."""

	def __init__(self, bot):
		super().__init__(bot)
		self.server_manager = sm.serverManager()

	@commands.Command(name="new_save_playlist", aliases=["svp"])
	async def save_playlist(self, ctx: commands.Context, *args):
		"""Guarda la lista de reproducción actual con un nombre."""
		self.log_command_user(ctx, "save_playlist")

		if not self.has_permission(ctx):
			lang = self.get_language(ctx)
			await ctx.send(leng.neencdv[lang])
			return
		
		guild_id = ctx.guild.id

		if not self.server_manager.exists(guild_id):
			return
		
		server = self.server_manager.get_server(guild_id)
		lang = self.get_language(ctx)

		if len(args) == 0:
			await ctx.send(leng.namereq[lang])
			return
		
		playlist_name = " ".join(args).strip()
		playlists = self.server_manager.show_playlist()

		if playlist_name in server.playlists:
			await ctx.send(leng.plalrext[lang].format(playlist_name))
			return
		
		server.playlists[playlist_name] = list(server.current_playlist)

		await ctx.send(leng.plsaved[lang].format(playlist_name))
