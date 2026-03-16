from dataclasses import dataclass, field
from typing import Any, List, Optional
from musica.models.playlist import Playlist


@dataclass
class Server:
    id: int
    name: str = ""
    playlists: List[Playlist] = field(default_factory=list)
    songs: List[Any] = field(default_factory=list)
    current_song_index: int = 0
    paused_at: Optional[str] = None
    started_at: Optional[str] = None
    is_active: bool = False
    total_length_seconds: int = 0
    loop_mode: int = 0

    @property
    def cplaying(self) -> int:
        return self.current_song_index

    @cplaying.setter
    def cplaying(self, value: int) -> None:
        self.current_song_index = value

    @property
    def ptime(self) -> Optional[str]:
        return self.paused_at

    @ptime.setter
    def ptime(self, value: Optional[str]) -> None:
        self.paused_at = value

    @property
    def time(self) -> Optional[str]:
        return self.started_at

    @time.setter
    def time(self, value: Optional[str]) -> None:
        self.started_at = value

    @property
    def status(self) -> bool:
        return self.is_active

    @status.setter
    def status(self, value: bool) -> None:
        self.is_active = value

    @property
    def tlength(self) -> int:
        return self.total_length_seconds

    @tlength.setter
    def tlength(self, value: int) -> None:
        self.total_length_seconds = value

    @property
    def looping(self) -> int:
        return self.loop_mode

    @looping.setter
    def looping(self, value: int) -> None:
        self.loop_mode = value