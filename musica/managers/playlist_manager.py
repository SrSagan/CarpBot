import os
from types import SimpleNamespace
from typing import Dict, List, Optional

from musica.models.playlist import Playlist
from musica.models.server import Server
from repositories.json_repository import JsonRepository
from utils.constants import SAVED_PLAYLIST


class PlayListManager:
    def __init__(self, servers: Optional[Dict[int, Server]] = None):
        self._servers: Dict[int, Server] = servers or {}
        self.json_repository = JsonRepository(SAVED_PLAYLIST)

    @staticmethod
    def _song_to_dict(song) -> dict:
        if isinstance(song, dict):
            return {
                "name": song.get("name", "Unknown"),
                "link": song.get("link", ""),
                "length": song.get("length", "00:00:00"),
                "type": song.get("type", "yt"),
            }

        return {
            "name": getattr(song, "name", "Unknown"),
            "link": getattr(song, "link", ""),
            "length": getattr(song, "length", "00:00:00"),
            "type": getattr(song, "type", "yt"),
        }

    @staticmethod
    def _song_from_dict(song_data) -> SimpleNamespace:
        if isinstance(song_data, dict):
            return SimpleNamespace(
                name=song_data.get("name", "Unknown"),
                link=song_data.get("link", ""),
                length=song_data.get("length", "00:00:00"),
                type=song_data.get("type", "yt"),
            )

        return SimpleNamespace(
            name=getattr(song_data, "name", "Unknown"),
            link=getattr(song_data, "link", ""),
            length=getattr(song_data, "length", "00:00:00"),
            type=getattr(song_data, "type", "yt"),
        )

    def regsiter_servers_dict(self, servers: Dict[int, Server]) -> None:
        self._servers = servers

    def register_servers_dict(self, servers: Dict[int, Server]) -> None:
        self._servers = servers

    def add_playlist(self, playlist: Playlist, server: Server, user_id: int):
        if server.id not in self._servers:
            raise ValueError("Server does not exist")
        server.playlists.append(playlist)

    def save_playlist(self, server_id: int, user_id: int, name: str) -> int:
        """
        Reurn codes (Para mantener compatibilidad con el codigo anterior):
        1 - saved successfully
        0 - reached limit (>=5)
        2 - playlist name already exists
        """

        server = self._servers.get(server_id)
        current_songs = [
            self._song_to_dict(song) for song in (server.songs if server else [])
        ]

        playlist = {"name": name, "songs": current_songs}
        path = os.path.join(SAVED_PLAYLIST, f"{user_id}.json")

        if not os.path.exists(path):
            self.json_repository.write([playlist], file_path=path)
            return 1  # saved successfully

        if os.path.exists(path):
            saved_playlists = self.json_repository.read(file_path=path)

            if len(saved_playlists) >= 5:
                return 0  # reached limit

            for playlist in saved_playlists:
                if playlist.get("name") == name:
                    return 2  # playlist name already exists

            saved_playlists.append(playlist)
            self.json_repository.write(saved_playlists, file_path=path)

            return 1  # saved successfully

    def load_playlist(self, server_id: int, user_id: int, name: str):
        """
        If server exists: append songs to server.songs and return 1
        If server does not exist: return the list of songs for the playlist
        Return 0 if not found / no file
        """

        path = os.path.join(SAVED_PLAYLIST, f"{user_id}.json")
        if not os.path.exists(path):
            return 0  # no file

        saved_playlists = self.json_repository.read(file_path=path)

        for playlist in saved_playlists:
            if playlist.get("name") == name:
                normalized_songs = [
                    self._song_from_dict(song) for song in playlist.get("songs", [])
                ]
                server = self._servers.get(server_id)
                if server:
                    server.songs += normalized_songs
                    return 1
                return normalized_songs

        return 0  # not found

    def show_playlist(self, user_id: int):
        path = os.path.join(SAVED_PLAYLIST, f"{user_id}.json")
        if not os.path.exists(path):
            return 0  # no file

        return self.json_repository.read(file_path=path)

    def show_playlis(self, user_id: int):
        # Legacy typo alias for compatibility.
        return self.show_playlist(user_id)

    def remove_playlist(self, user_id: int, name: str) -> int:
        path = os.path.join(SAVED_PLAYLIST, f"{user_id}.json")
        if not os.path.exists(path):
            return 0  # no file

        saved_playlists = self.json_repository.read(file_path=path)

        for playlist in saved_playlists:
            if playlist.get("name") == name:
                saved_playlists.remove(playlist)
                self.json_repository.write(saved_playlists, file_path=path)
                return 1  # removed successfully

        return 0
