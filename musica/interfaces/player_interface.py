from typing import Any, Optional, Protocol, Tuple


class PlayerInterface(Protocol):
    async def youtube_player(
        self, voice_client: Any, id: int
    ) -> Tuple[Optional[str], Optional[str]]:
        """Play audio from YouTube given a voice client and an identifier.

        Args:
            voice_client (Any): The voice client to play audio through.
            id: The identifier for the YouTube content.
        Returns:
            Tuple[Optional[str], Optional[str]]: A tuple containing the title and URL of the
            played content, or None if not applicable.
        """
        ...

    async def file_player(
        self, voice_client: Any, id: int
    ) -> Tuple[Optional[str], Optional[str]]:
        """Play audio from a file given a voice client and an identifier.

        Args:
            voice_client (Any): The voice client to play audio through.
            id: The identifier for the file content.
        Returns:
            Tuple[Optional[str], Optional[str]]: A tuple containing the title and URL of the
            played content, or None if not applicable.
        """
        ...
