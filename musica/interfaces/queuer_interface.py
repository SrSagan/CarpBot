from typing import Any, Optional, Tuple, Protocol


class QueuerInterface(Protocol):
    def queuer(self, songs: list | str, guild_id: int) -> None: ...

    async def youtube_queuer(
        self, ctx: Any, request: str
    ) -> Tuple[Optional[str], Optional[str]]: ...

    async def file_queuer(self, ctx: Any, url: str) -> Optional[str]: ...
