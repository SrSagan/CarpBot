from typing import Any, Optional, Tuple

import discord
import yt_dlp

from musica.managers.server_manager import ServerManager
from musica.interfaces.player_interface import PlayerInterface


class Player(PlayerInterface):
    _FFMPEG_BEFORE_OPTIONS = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
    _YDL_OPTIONS = {
        "quiet": False,
        "youtube_include_dash_manifest": False,
        "youtube_include_hls_manifest": False,
        "format": "bestaudio",
    }

    def __init__(self):
        self._server_manager = ServerManager()

    def _get_current_song_link(self, guild_id: int) -> Optional[str]:
        server = self._server_manager.get_server(guild_id)
        if server.current_song_index < 0 or server.current_song_index >= len(server.songs):
            return None
        return server.songs[server.current_song_index].link

    async def youtube_player(
        self, voice_client: Any, id: int
    ) -> Tuple[Optional[str], Optional[str]]:
        song_link = self._get_current_song_link(id)
        if song_link is None:
            return None, None

        ydl = yt_dlp.YoutubeDL(self._YDL_OPTIONS)
        try:
            video_info = ydl.extract_info(song_link, download=False)
        except Exception:
            return None, None

        audio_url = video_info.get("url")
        if not audio_url:
            return None, None

        voice_client.play(
            discord.FFmpegPCMAudio(
                audio_url,
                before_options=self._FFMPEG_BEFORE_OPTIONS,
                options="-vn",
            )
        )

        return video_info.get("thumbnail"), video_info.get("webpage_url")

    async def file_player(
        self, voice_client: Any, id: int
    ) -> Tuple[Optional[str], Optional[str]]:
        song_link = self._get_current_song_link(id)
        if song_link is None:
            return None, None

        voice_client.play(
            discord.FFmpegPCMAudio(
                song_link,
                before_options=self._FFMPEG_BEFORE_OPTIONS,
            )
        )

        return None, None
