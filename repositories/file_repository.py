from typing import List
from repositories.base_repository import BaseRepository

class FileRepository(BaseRepository):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def read(self) -> List[str]:
        """Lee líneas del archivo, filtrando líneas vacías."""
        with open(self.file_path, "r", encoding="utf-8") as file:
            return [line.strip() for line in file if line.strip()]
        
    def write(self, data: List[str]) -> None:
        """Escribe líneas en el archivo."""
        with open(self.file_path, "w", encoding="utf-8") as file:
            for line in data:
                file.write(f"{line}\n")

    def append(self, line:str) -> None:
        """Agrega una línea al archivo."""
        data = self.read()
        data.append(line)
        self.write(data)

    def remove(self, line:str) -> bool:
        """Elimina una línea del archivo."""
        data = self.read()
        if line in data:
            data.remove(line)
            self.write(data)
            return True
        return False