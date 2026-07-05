from abc import ABC, abstractmethod
from typing import Any

class BaseRepository(ABC):
	@abstractmethod
	def read(self) -> Any:
		"""Lee datos del almacenamiento."""
		pass

	@abstractmethod
	def write(self, data: Any) -> None:
		"""Escribe datos en el almacenamiento."""
		pass