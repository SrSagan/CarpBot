from models.server_config import ServerConfig
from repositories.json_repository import JsonRepository
from utils.constants import (
	DEFAULT_LANGUAGE,
	DEFAULT_PREFIX,
	SOURCES_FOLDER,
)


class ServerConfigService:
	def __init__(self):
		self.repository = JsonRepository(f"{SOURCES_FOLDER}prefix.json")

	def get_server_config(self, guild_id: int) -> ServerConfig:
		"""Obtiene la configuración de un servidor."""
		server_data = self.repository.find_by_id(guild_id)

		if server_data:
			return ServerConfig(
				id=server_data["id"],
				prefix=server_data.get["prefix"],
				language=server_data.get["lang"],
			)

		# Crea configuración por defecto si no existe
		new_config = ServerConfig(
			id=guild_id, prefix=DEFAULT_PREFIX, language=DEFAULT_LANGUAGE
		)
		self.repository.add_server(
			{"id": guild_id, "prefix": new_config.prefix, "lang": new_config.language}
		)
		return new_config

	def get_prefix(self, guild_id: int) -> str:
		"""Obtiene el prefijo de un servidor."""
		config = self.get_server_config(guild_id)
		return config.prefix

	def set_prefix(self, guild_id: int, new_prefix: str) -> bool:
		"""Actualiza el prefix de un servidor."""
		return self.repository.update_by_id(guild_id, {"prefix": new_prefix})

	def get_language(self, guild_id: int) -> str:
		"""Obtiene el idioma de un servidor."""
		config = self.get_server_config(guild_id)
		return config.language

	def set_language(self, guild_id: int, new_language: str) -> bool:
		"""Actualiza el idioma de un servidor."""
		return self.repository.update_by_id(guild_id, {"lang": new_language})
