import os
from typing import Dict, List, Optional

from musica.models.playlist import Playlist
from musica.models.server import Server
from repositories.json_repository import JsonRepository
from utils.constants import SAVED_PLAYLIST


class PlayListManager:
	def __init__(self, servers: Optional[Dict[int, Server]] = None):
		self._servers = Dict[int, Server] = servers or {}
		self.json_repository = JsonRepository(SAVED_PLAYLIST)

	def regsiter_servers_dict(self, servers: Dict[int, Server]) -> None:
		self._servers = servers

	def add_playlist(self, playlist: Playlist, server: Server, user_id: int):
		if server.id not in self._servers:
			raise ValueError("Server does not exist")
		self._playlist[user_id] = playlist

	def save_playlist(self, server_id: int, user_id: int, name: str) -> int:
		"""
		Reurn codes (Para mantener compatibilidad con el codigo anterior):
		1 - saved successfully
		0 - reached limit (>=5)
		2 - playlist name already exists
		"""

		server = self._servers.get(server_id)
		current_songs: List[int] = server.songs if server else []

		playlist = {"name": name, "songs": current_songs}
		path = os.path.join(SAVED_PLAYLIST, f"{user_id}.json")

		if not os.path.exists(path):
			self.json_repository.write(path, [playlist])
			return 1  # saved successfully

		if os.path.exists(path):
			saved_playlists = self.json_repository.read(path)

			if len(saved_playlists) >= 5:
				return 0  # reached limit

			for playlist in saved_playlists:
				if playlist.get("name") == name:
					return 2  # playlist name already exists

			saved_playlists.append(playlist)
			self.json_repository.write(path, saved_playlists)

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

		saved_playlists = self.json_repository.read(path)

		for playlist in saved_playlists:
			if playlist.get("name") == name:
				server = self._servers.get(server_id)
				if server:
					server.songs += playlist.get("songs", [])
					return 1
				return playlist.get("songs", [])

		return 0  # not found

	def show_playlis(self, user_id: int):
		path = os.path.join(SAVED_PLAYLIST, f"{user_id}.json")
		if not os.path.exists(path):
			return 0  # no file

		return self.json_repository.read(path)

	def remove_playlist(self, user_id: int, name: str) -> int:
		path = os.path.join(SAVED_PLAYLIST, f"{user_id}.json")
		if not os.path.exists(path):
			return 0  # no file

		saved_playlists = self.json_repository.read(path)

		for playlist in saved_playlists:
			if playlist.get("name") == name:
				saved_playlists.remove(playlist)
				self.json_repository.write(path, saved_playlists)
				return 1  # removed successfully

		return 0
