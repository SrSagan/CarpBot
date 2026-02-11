from musica.interfaces.player_interface import PlayerInterface


class Player(PlayerInterface):
    def __init__(self):
        super().__init__()

    async def youtube_player(self, voice_client, id):
        return await super().youtube_player(voice_client, id)
    
    async def file_player(self, voice_client, id):
        return await super().file_player(voice_client, id)