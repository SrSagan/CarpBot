import yt_dlp
from musica.interfaces.queuer_interface import QueuerInterface
from musica.managers.server_manager import ServerManager
from musica.models.server import Server


class Queuer(QueuerInterface):
    _YDL_OPTIONS = {
        "quiet": False,
        "extract_flat": "in_playlist",
        "youtube_include_dash_manifest": False,
        "youtube_include_hls_manifest": False,
    }

    def __init__(self):
        self._server_manager = ServerManager()

    def queuer(self, songs, guild_id):
        if self._server_manager.exists(guild_id):
            server = self._server_manager.get_server(guild_id)
            self._save_from_type(songs, server)
        else:
            new_server = Server(guild_id)
            self._save_from_type(songs, new_server)
            self._server_manager.add_server(new_server)

    def _save_from_type(self, songs, server: Server):
        if isinstance(songs, list):
            server.songs += songs
        else:
            server.songs.append(songs)

    async def youtube_queuer(self, ctx, request):
        ydl = yt_dlp.YoutubeDL(self._YDL_OPTIONS)
        return await super().youtube_queuer(ctx, request)

    async def file_queuer(self, ctx, url):
        return await super().file_queuer(ctx, url)
