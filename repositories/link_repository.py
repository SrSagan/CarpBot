from typing import List
from repositories.file_repository import FileRepository
from models.link_group import LinkGroup
from utils.constants import LINKS_FOLDER 

class LinkRepository:
    def __init__(self, link_group: LinkGroup):
        self.link_group = link_group
        file_path = f"{LINKS_FOLDER}{link_group.value}.txt"
        self.file_repo = FileRepository(file_path)

    def get_all_links(self) -> List[str]:
        """Obtiene todos los links del grupo"""
        return self.file_repo.read()
    
    def add_link(self, link: str) -> None:
        """Agrega un link al grupo"""
        self.file_repo.append(link)

    def remove_link(self, link: str) -> bool:
        """Elimina un link del grupo"""
        return self.file_repo.remove(link)