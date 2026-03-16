import json
from typing import Any, List, Dict
from repositories.base_repository import BaseRepository


class JsonRepository(BaseRepository):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def read(self, file_path: str | None = None) -> List[Dict[str, Any]]:
        """Lee y parsea el archivo JSON"""
        path = file_path or self.file_path

        try:
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def write(self, data: List[Dict[str, Any]], file_path: str | None = None) -> None:
        """Escribe datos al archivo JSON"""
        path = file_path or self.file_path
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def find_by_id(self, server_id: int) -> Dict[str, Any] | None:
        """Busca un servidor por ID."""
        data = self.read()
        for item in data:
            if item.get("id") == server_id:
                return item
        return None

    def update_by_id(self, server_id: int, updates: Dict[str, Any]) -> bool:
        """Actualiza un servidor por ID."""
        data = self.read()
        for item in data:
            if item.get("id") == server_id:
                item.update(updates)
                self.write(data)
                return True
        return False

    def add_server(self, server_data: Dict) -> None:
        """Agrega un nuevo servidor."""
        data = self.read()
        data.append(server_data)
        self.write(data)
