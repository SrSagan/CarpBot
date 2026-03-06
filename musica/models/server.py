from dataclasses import dataclass, field
from typing import List
from musica.models.playlist import Playlist

@dataclass
class Server:
    id: int
    name: str
    playlists: List[Playlist] = field(default_factory=list)
    songs: List[int] = field(default_factory=list)