from typing import Dict, List, Optional
from musica.models.server import Server


class ServerManager:
    def __init__(self):
        self._servers = Dict[int, Server] = {}

    def add_server(self, server: Server):
        self._servers[server.id] = server

    def get_server(self, id: int) -> Optional[Server]:
        return self._servers.get(id)

    def remove_server(self, id: int) -> bool:
        deleted_server = self._servers.pop(id, None)
        return deleted_server is not None

    def list_servers(self) -> List[Server]:
        return list(self._servers.values())

    def exists(self, id: int) -> bool:
        return id in self._servers
