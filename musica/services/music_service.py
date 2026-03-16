import asyncio
import datetime
import random
import time
from typing import Any

import discord
import discord.utils
import yt_dlp
from loguru import logger

import data
import lenguajes as leng
from musica.managers.server_manager import ServerManager
from musica.services.player_service import Player
from musica.services.queuer_service import Queuer


a = data.datos()
q = Queuer()
p = Player()
sm = ServerManager()


class MusicService:
	def __init__(self):
		self._data = a
		self._queuer = q
		self._player = p
		self._server_manager = sm

	@staticmethod
	def _song_attr(song: Any, attr: str, default: Any = None) -> Any:
		if isinstance(song, dict):
			return song.get(attr, default)
		return getattr(song, attr, default)

	@staticmethod
	def _playlist_attr(playlist: Any, attr: str, default: Any = None) -> Any:
		if isinstance(playlist, dict):
			return playlist.get(attr, default)
		return getattr(playlist, attr, default)

	def _song_index(self, playlist: Any) -> int:
		index = self._playlist_attr(playlist, "current_song_index")
		if index is not None:
			return index
		return self._playlist_attr(playlist, "cplaying", -1)

	def _started_at(self, playlist: Any):
		value = self._playlist_attr(playlist, "started_at")
		if value is not None:
			return value
		return self._playlist_attr(playlist, "time")

	def _paused_at(self, playlist: Any):
		value = self._playlist_attr(playlist, "paused_at")
		if value is not None:
			return value
		return self._playlist_attr(playlist, "ptime")

	def _is_active(self, playlist: Any) -> bool:
		value = self._playlist_attr(playlist, "is_active")
		if value is not None:
			return value
		return bool(self._playlist_attr(playlist, "status", False))

	async def _extract_info_async(self, yt: yt_dlp.YoutubeDL, link: str) -> dict:
		return await asyncio.to_thread(yt.extract_info, link, False)

	async def _wait_until_idle(self, vc) -> None:
		while vc.is_playing() or vc.is_paused():
			await asyncio.sleep(0.25)

	def _normalize_play_index(self, server) -> None:
		if server.loop_mode == 2:
			server.current_song_index -= 1

	def _playback_finished(self, server, guild_id: int) -> bool:
		return (
			server.current_song_index + 1 > len(server.songs)
			or server.is_active is False
			or not self._server_manager.exists(guild_id)
		)

	async def _handle_finished_queue(self, server, guild_id: int, ctx) -> bool:
		if server.loop_mode == 1 and self._server_manager.exists(guild_id):
			server.current_song_index = 0
			return False

		server.is_active = False
		server.current_song_index = -1
		embed = discord.Embed(
			title=leng.qo[self._data.get_lenguaje(ctx.message)], color=0x3498DB
		)
		await ctx.send(embed=embed)
		return True

	async def _start_song(self, server, vc, guild_id: int, ctx):
		while True:
			if server.current_song_index >= len(server.songs):
				return None, None, False

			song_type = self._song_attr(server.songs[server.current_song_index], "type")
			if song_type == "yt":
				vid_thumbnail, url = await self._player.youtube_player(vc, guild_id)
				if vid_thumbnail or url:
					return vid_thumbnail, url, True
				await ctx.send("Video unavailable")
				server.current_song_index += 1
				continue

			if song_type == "fl":
				file_thumbnail = await self._player.file_player(vc, guild_id)
				vid_thumbnail = None if file_thumbnail == 0 else file_thumbnail
				return vid_thumbnail, None, True

			await ctx.send("Unsupported song type")
			server.current_song_index += 1

	async def _send_now_playing(self, server, ctx, bot, msg_sent, msg, url, vid_thumbnail):
		if msg_sent and discord.utils.get(bot.cached_messages, id=msg.id) is not None:
			await msg.delete()

		current_song = server.songs[server.current_song_index]
		embed = discord.Embed(
			title=leng.ar[self._data.get_lenguaje(ctx.message)],
			color=0x3498DB,
			description=self._song_attr(current_song, "name", "Unknown"),
			url=url,
		)
		if vid_thumbnail:
			embed.set_image(url=vid_thumbnail)
		embed.set_footer(
			text=leng.posicion[self._data.get_lenguaje(ctx.message)]
			+ ": "
			+ str(server.current_song_index + 1)
		)
		return await ctx.send(embed=embed)

	async def play(self, vc, ctx, bot):
		guild_id = ctx.message.guild.id
		msg_sent = False
		msg = None

		while True:
			if not self._server_manager.exists(guild_id):
				break

			server = self._server_manager.get_server(guild_id)
			server.is_active = True
			self._normalize_play_index(server)

			await self._wait_until_idle(vc)

			if self._playback_finished(server, guild_id):
				should_break = await self._handle_finished_queue(server, guild_id, ctx)
				if should_break:
					break

			vid_thumbnail, url, started = await self._start_song(server, vc, guild_id, ctx)
			if not started:
				if await self._handle_finished_queue(server, guild_id, ctx):
					break
				continue

			msg = await self._send_now_playing(
				server, ctx, bot, msg_sent, msg, url, vid_thumbnail
			)
			msg_sent = True
			server.current_song_index = server.current_song_index + 1
			server.started_at = time.strftime("%H:%M:%S", time.localtime())

	def _queue_pages(self, songs):
		pages = []
		page = []
		for song in songs:
			page.append(song)
			if len(page) == 10:
				pages.append(page)
				page = []
		pages.append(page)
		return pages

	def shuffler(self, ctx):
		guild_id = ctx.message.guild.id

		if self._server_manager.exists(guild_id):
			server = self._server_manager.get_server(guild_id)

			final = []
			current_song_index = server.current_song_index
			already_played = range(0, current_song_index)

			for idx in already_played:
				final.append(server.songs[idx])

			out = server.songs
			for _ in already_played:
				out.pop(0)

			random.shuffle(out)
			final += out
			server.songs = final

	async def queuer(self, ctx, request, song_type):
		if song_type == "yt":
			await self._queuer.youtube_queuer(ctx, request)
		elif song_type == "fl":
			msg = ctx.message
			url = None
			for attachment in msg.attachments:
				url = attachment.url

			if url is None:
				await ctx.send("No file attachment provided")
				return

			await self._queuer.file_queuer(ctx, url)

	def print_queue(self, playlist, arg, looping, ctx):
		cpage = 0
		if looping != -1:
			vc = ctx.voice_client
			start_time = self._started_at(playlist)
			cplaying = self._song_index(playlist)
			time_left = self.calculate_queue_time(start_time, playlist, cplaying, vc)
		else:
			cplaying = -1
			time_left = "--:--:--"

		songs = self._playlist_attr(playlist, "songs", [])
		pages = self._queue_pages(songs)
		logger.debug(str(arg) + "page")

		if (arg <= len(pages)) and (arg != 0):
			cpage = arg - 1
		else:
			return 0

		if arg == -1:
			cpage = len(pages) - 1

		text = ""
		index = 10 * cpage
		for song in pages[cpage]:
			song_name = self._song_attr(song, "name", "Unknown")
			song_length = self._song_attr(song, "length", "Unknown")
			if index + 1 == cplaying:
				text += (
					"**"
					+ str(index + 1)
					+ ") "
					+ song_name
					+ "** • *"
					+ leng.tr[self._data.get_lenguaje(ctx.message)]
					+ " "
					+ time_left
					+ "*\n"
				)
			else:
				text += (
					"**"
					+ str(index + 1)
					+ ")** "
					+ song_name
					+ " • *"
					+ leng.duracion[self._data.get_lenguaje(ctx.message)]
					+ ": "
					+ song_length
					+ "*\n"
				)
			index += 1

		embed = discord.Embed(title="**Queue**", color=0x3498DB, description=text)

		if len(songs) - (cpage + 1) * 10 > 0 and looping != -1:
			embed.add_field(
				name="Songs left", value=str(len(songs) - (cpage + 1) * 10), inline=True
			)

		if looping != 2 and looping != -1:
			embed.add_field(
				name="Looping",
				value=leng.arlq_ca_d[self._data.get_lenguaje(ctx.message)][looping],
				inline=True,
			)
		embed.set_footer(text="Page: " + str(cpage + 1) + "/" + str(len(pages)))

		return embed

	async def get_video_info(self, guild_id, ctx, *index):
		if self._server_manager.exists(guild_id):
			server = self._server_manager.get_server(guild_id)
			ydl_opts = {
				"quiet": False,
				"youtube_include_dash_manifest": False,
				"youtube_include_hls_manifest": False,
				"format": "bestaudio",
			}
			yt = yt_dlp.YoutubeDL(ydl_opts)

			if len(index) != 0:
				song_index = int(index[0])
				if song_index <= len(server.songs):
					song = server.songs[song_index - 1]
					video = await self._extract_info_async(yt, self._song_attr(song, "link"))
				else:
					return leng.cfdr[self._data.get_lenguaje(ctx.message)]
			else:
				song = server.songs[server.current_song_index - 1]
				video = await self._extract_info_async(yt, self._song_attr(song, "link"))

			date = "/" + video["upload_date"][0:4]
			date = "/" + video["upload_date"][4:6] + date
			date = video["upload_date"][6:] + date

			youtube_info = "**Youtube Information**\n"
			youtube_info += "-**Title:** " + video["title"] + "\n"
			youtube_info += "-**Uploader:** " + video["uploader"] + "\n"
			youtube_info += (
				"-**Views:** " + str(round(video["view_count"] / 1000, 1)) + "K\n"
			)
			youtube_info += "-**Length:** " + video["duration_string"] + "\n"
			youtube_info += (
				"-**Likes:** " + str(round(video["like_count"] / 1000, 1)) + "K\n"
			)
			youtube_info += "-**Uploaded:** " + date + "\n"
			youtube_info += "-**Link:** " + video["webpage_url"] + "\n"
			youtube_info += "-**Channel Link:** " + video["channel_url"] + "\n"
			youtube_info += "-**Thumbnail:** " + video["thumbnail"] + "\n\n"
			final_text = youtube_info

			if "track" in video:
				music_info = "**Music information**\n"
				music_info += "-**Track name:** " + video["track"] + "\n"
				music_info += "-**Artist:** " + video["artist"] + "\n"
				music_info += "-**Album:** " + video["album"] + "\n"
				if video["release_year"] is None:
					release_year = "Unknown"
				else:
					release_year = str(video["release_year"])
				music_info += "-**Release year:** " + release_year + "\n\n"
				final_text += music_info

			file_info = "**File information**\n"
			file_info += "-**Audio codec**: " + video["acodec"] + "\n"
			file_info += "-**Sample rate**: " + str(video["asr"] / 1000) + "Khz\n"
			file_info += "-**Size**: " + str(round(video["filesize"] / 1000000, 2)) + "MB\n"
			file_info += "-**Channels**: " + str(video["audio_channels"]) + "\n"
			file_info += "-**Youtube format**: " + video["format"] + "\n"
			final_text += file_info

			embed = discord.Embed(
				title="Video Information", color=0x3498DB, description=final_text
			)
			embed.set_thumbnail(url=video["thumbnail"])
			return embed

		return None

	def calculate_queue_time(self, start_time, playlist, cplaying, vc):
		songs = self._playlist_attr(playlist, "songs", [])
		if not start_time:
			return "--:--:--"
		if cplaying > len(songs):
			return "Done"

		x = time.strptime(start_time.split(",")[0], "%H:%M:%S")
		start_seconds = datetime.timedelta(
			hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec
		).total_seconds()

		current_song = songs[cplaying - 1]
		x = time.strptime(self._song_attr(current_song, "length").split(",")[0], "%H:%M:%S")
		length_seconds = datetime.timedelta(
			hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec
		).total_seconds()

		playlist_status = self._is_active(playlist)
		if vc.is_paused() and playlist_status is True:
			x = time.strptime(self._paused_at(playlist).split(",")[0], "%H:%M:%S")
			current_seconds = datetime.timedelta(
				hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec
			).total_seconds()
		else:
			x = time.strptime(time.strftime("%H:%M:%S", time.localtime()).split(",")[0], "%H:%M:%S")
			current_seconds = datetime.timedelta(
				hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec
			).total_seconds()

		time_elapsed = current_seconds - start_seconds
		time_left = time.strftime("%H:%M:%S", time.gmtime(length_seconds - time_elapsed))
		return time_left


class ControlChecker(discord.ui.View):
	def __init__(self, *, timeout=800, playlist, arg, looping, ctx):
		super().__init__(timeout=timeout)
		self.playlist = playlist
		self.arg = arg
		self.looping = looping
		self.ctx = ctx
		self.service = MusicService()

	@discord.ui.button(label="◄◄", style=discord.ButtonStyle.gray)
	async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
		self.arg = 1
		embed = self.service.print_queue(self.playlist, self.arg, self.looping, self.ctx)
		if embed != 0:
			await interaction.response.edit_message(view=self, embed=embed)

	@discord.ui.button(label="◄", style=discord.ButtonStyle.gray)
	async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
		self.arg = self.arg - 1
		if self.arg < 1:
			self.arg = 1
		embed = self.service.print_queue(self.playlist, self.arg, self.looping, self.ctx)
		if embed != 0:
			await interaction.response.edit_message(view=self, embed=embed)

	@discord.ui.button(label="►", style=discord.ButtonStyle.gray)
	async def forward(self, interaction: discord.Interaction, button: discord.ui.Button):
		self.arg = self.arg + 1
		embed = self.service.print_queue(self.playlist, self.arg, self.looping, self.ctx)
		if embed != 0:
			await interaction.response.edit_message(view=self, embed=embed)

	@discord.ui.button(label="►►", style=discord.ButtonStyle.gray)
	async def end(self, interaction: discord.Interaction, button: discord.ui.Button):
		self.arg = int(len(self.service._playlist_attr(self.playlist, "songs", [])) / 10) + 1
		embed = self.service.print_queue(self.playlist, self.arg, self.looping, self.ctx)
		if embed != 0:
			await interaction.response.edit_message(view=self, embed=embed)


musicManager = MusicService
control_checker = ControlChecker

