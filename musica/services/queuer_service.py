from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import aiohttp
import discord
import yt_dlp
from tinytag import TinyTag

import data
import lenguajes as leng
from musica.interfaces.queuer_interface import QueuerInterface
from musica.managers.server_manager import ServerManager
from musica.models.server import Server


@dataclass
class Song:
    name: str
    link: str
    length: str
    type: str


class Queuer(QueuerInterface):
    _AUDIO_ONLY_OPTIONS = {"format": "bestaudio/best", "forcethumbnail": "best"}
    _TEMP_DIR = Path("temp")
    _VIDEO_UNAVAILABLE = "Video unavailable"
    _FILE_UNAVAILABLE = "File unavailable"

    _YDL_OPTIONS = {
        "quiet": False,
        "extract_flat": "in_playlist",
        "youtube_include_dash_manifest": False,
        "youtube_include_hls_manifest": False,
    }

    def __init__(self):
        self._server_manager = ServerManager()
        self._data = data.datos()

    def queuer(self, songs, guild_id):
        server = self._server_manager.ensure_server(guild_id)
        self._save_from_type(songs, server)

    def _normalize_song(self, song) -> Song:
        if isinstance(song, Song):
            return song

        if isinstance(song, dict):
            return Song(
                name=song.get("name", "Unknown"),
                link=song.get("link", ""),
                length=song.get("length", "00:00:00"),
                type=song.get("type", "yt"),
            )

        return Song(
            name=getattr(song, "name", "Unknown"),
            link=getattr(song, "link", ""),
            length=getattr(song, "length", "00:00:00"),
            type=getattr(song, "type", "yt"),
        )

    def _save_from_type(self, songs, server: Server):
        if isinstance(songs, list):
            server.songs += [self._normalize_song(song) for song in songs]
        else:
            server.songs.append(self._normalize_song(songs))

    @staticmethod
    def _is_url(value: str) -> bool:
        parsed = urlparse(value)
        return bool(parsed.scheme and parsed.netloc)

    @staticmethod
    def _entry_link(entry: dict) -> str:
        entry_url = entry.get("url") or entry.get("webpage_url")
        if not entry_url:
            return ""
        if entry_url.startswith("http"):
            return entry_url
        return f"https://www.youtube.com/watch?v={entry_url}"

    async def _resolve_video(self, request: str):
        ydl = yt_dlp.YoutubeDL(self._YDL_OPTIONS)
        if self._is_url(request):
            return ydl.extract_info(request, download=False)
        search = ydl.extract_info(f"ytsearch:{request}", download=False)
        entries = search.get("entries", [])
        return entries[0] if entries else None

    async def _queue_playlist(self, ctx, video: dict) -> None:
        entries = video.get("entries", [])
        songs = []
        total_length = 0

        for entry in entries:
            duration = entry.get("duration")
            link = self._entry_link(entry)
            if duration is None or not link:
                continue
            total_length += int(duration)
            songs.append(
                Song(
                    name=entry.get("title", "Unknown"),
                    link=link,
                    length=self._data.get_time(int(duration)),
                    type="yt",
                )
            )

        if not songs:
            await ctx.send(self._VIDEO_UNAVAILABLE)
            return

        guild_id = ctx.message.guild.id
        self.queuer(songs, guild_id)

        lang = self._data.get_lenguaje(ctx.message)
        embed = discord.Embed(
            title="Queued " + str(video.get("title", "Playlist")),
            color=0x3498DB,
            description=str(len(songs)) + " " + leng.canciones[lang],
        )
        uploader = video.get("uploader", "Unknown")
        embed.set_footer(
            text=leng.duracion[lang]
            + ": "
            + self._data.get_time(total_length)
            + "\n"
            + uploader
        )
        await ctx.send(embed=embed)

    async def _queue_single_video(self, ctx, video: dict, source_type: str) -> None:
        guild_id = ctx.message.guild.id
        lang = self._data.get_lenguaje(ctx.message)

        vid_name = video.get("title", "Unknown")
        duration = int(video.get("duration") or 0)
        vid_length = self._data.get_time(duration)

        if source_type == "link":
            vid_link = video.get("webpage_url") or self._entry_link(video)
            vid_thumbnail = video.get("thumbnail")
        else:
            vid_link = self._entry_link(video)
            if not vid_link:
                await ctx.send(self._VIDEO_UNAVAILABLE)
                return
            details = yt_dlp.YoutubeDL(self._AUDIO_ONLY_OPTIONS).extract_info(
                vid_link, download=False
            )
            vid_thumbnail = details.get("thumbnail")

        song = Song(name=vid_name, link=vid_link, length=vid_length, type="yt")
        self.queuer(song, guild_id)

        server = self._server_manager.get_server(guild_id)
        if server.is_active:
            embed = discord.Embed(title="Queued", color=0x3498DB, description=vid_name)
            if vid_thumbnail:
                embed.set_image(url=vid_thumbnail)
            embed.set_footer(
                text=leng.duracion[lang]
                + ": "
                + vid_length
                + "\n"
                + leng.posicion[lang]
                + ": "
                + str(len(server.songs))
            )
            await ctx.send(embed=embed)

    async def youtube_queuer(self, ctx, request):
        try:
            video = await self._resolve_video(request)
        except Exception:
            await ctx.send(self._VIDEO_UNAVAILABLE)
            return

        if not video:
            await ctx.send(self._VIDEO_UNAVAILABLE)
            return

        if video.get("_type") == "playlist":
            await self._queue_playlist(ctx, video)
            return

        source_type = "link" if self._is_url(request) else "search"
        await self._queue_single_video(ctx, video, source_type)

    async def file_queuer(self, ctx, url):
        guild_id = ctx.message.guild.id
        lang = self._data.get_lenguaje(ctx.message)

        self._TEMP_DIR.mkdir(parents=True, exist_ok=True)
        name = url.rsplit("/", 1)[-1] or "audio.mp3"
        temp_path = self._TEMP_DIR / name

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=20) as response:
                if response.status != 200:
                    await ctx.send(self._FILE_UNAVAILABLE)
                    return
                with temp_path.open("wb") as temp_file:
                    async for chunk in response.content.iter_chunked(8192):
                        if chunk:
                            temp_file.write(chunk)

        audio = TinyTag.get(str(temp_path))
        title = audio.title if audio.title else name
        duration = int(audio.duration or 0)
        vid_length = self._data.get_time(duration)

        song = Song(name=title, link=url, length=vid_length, type="fl")
        self.queuer(song, guild_id)

        server = self._server_manager.get_server(guild_id)
        embed = discord.Embed(title="Queued", color=0x3498DB, description=str(title))
        embed.set_footer(
            text=leng.duracion[lang]
            + ": "
            + vid_length
            + "\n"
            + leng.posicion[lang]
            + ": "
            + str(len(server.songs))
        )
        await ctx.send(embed=embed)

        temp_path.unlink(missing_ok=True)
