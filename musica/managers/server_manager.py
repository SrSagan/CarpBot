from typing import ClassVar, Dict, List, Optional

from musica.models.server import Server


class ServerManager:
    _servers: ClassVar[Dict[int, Server]] = {}

    def add_server(self, server: Server):
        ServerManager._servers[server.id] = server

    def ensure_server(self, guild_id: int, name: str = "") -> Server:
        server = self.get_server(guild_id)
        if server is None:
            server = Server(id=guild_id, name=name)
            self.add_server(server)
        return server

    def get_server(self, id: int) -> Optional[Server]:
        return ServerManager._servers.get(id)

    def remove_server(self, id: int) -> bool:
        deleted_server = ServerManager._servers.pop(id, None)
        return deleted_server is not None

    def clear(self, id: int) -> bool:
        return self.remove_server(id)

    def list_servers(self) -> List[Server]:
        return list(ServerManager._servers.values())

    def exists(self, id: int) -> bool:
        return id in ServerManager._servers

    def get_server_store(self) -> Dict[int, Server]:
        return ServerManager._servers
