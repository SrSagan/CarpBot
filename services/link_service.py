import random
from typing import List, Optional

from models.link_group import LinkGroup
from repositories.link_repository import LinkRepository
from utils.constants import LINK_GROUPS_CONFIG, SUPPORTED_FORMATS


class LinkService:
	def __init__(self):
		self.link_groups = self._initialize_groups()

	def _initialize_groups(self) -> List[LinkGroup]:
		"""Inicializa los grupos de links"""
		return [
			LinkGroup(group=config["group"], name=config["name"])
			for config in LINK_GROUPS_CONFIG
		]

	def get_group_by_name(self, name: str) -> Optional[LinkGroup]:
		"""Obtiene un grupo por su nombre"""
		for group in self.link_groups:
			if group.name.lower() == name.lower():
				return group
		return None

	def load_links(self, group: LinkGroup) -> None:
		"""Carga los links de un grupo"""
		repo = LinkRepository(group)
		group.data = repo.get_all_links()

	def get_random_link(self, group_name: str) -> Optional[str]:
		"""Obtiene un link aleatorio de un grupo"""
		group = self.get_group_by_name(group_name)
		if not group:
			return None

		if not group.data:
			self.load_links(group)

		if not group.data:
			return None

		return random.choice(group.data).strip()

	def add_link(self, group_name: str, link: str) -> bool:
		"""Agrega un link a un grupo"""
		group = self.get_group_by_name(group_name)
		if not group:
			return False

		repo = LinkRepository(group)
		repo.add_link(link)
		group.data.append(link)

		return True

	def remove_link(self, group_name: str, link: str) -> bool:
		"""Elimina un link de un grupo"""
		group = self.get_group_by_name(group_name)
		if not group:
			return False

		repo = LinkRepository(group)
		success = repo.remove_link(link.strip())

		if success and link.strip() in group.data:
			group.data.remove(link.strip())

		return success

	def get_supported_formats(self) -> List[str]:
		"""Obtiene los formatos soportados."""
		return SUPPORTED_FORMATS

	def get_all_group_names(self) -> List[str]:
		"""Obtiene todos los nombres de grupos disponibles"""
		return [group.name for group in self.link_groups]
