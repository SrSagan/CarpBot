import random
from typing import List
from repositories.file_repository import FileRepository
from utils.constants import SOURCES_FOLDER


class PhraseService:
	def __init__(self):
		self.repository = FileRepository(f"{SOURCES_FOLDER}frases.txt")

	def add_phrase(self, phrase: str) -> bool:
		"""
		Agrega una frase al archivo
		Returns:
			True si se agregó, False si ya existía
		"""
		phrases = self.repository.read()
		if phrase in phrases:
			return False

		self.repository.append(phrase)
		return True
	
	def get_random_phrase(self) -> str:
		"""Obtiene una frase aleatoria"""
		phrases = self.repository.read()
		if not phrases:
			raise ValueError("No hay frases disponibles")
		return random.choice(phrases)

	def search_phrase(self, keyword: str) -> List[str]:
		"""
		Busca frases que contengan la palabra clave
		Returns: Lista de frases encontradas o lista vacía
		"""
		phrases = self.repository.read()
		return [phrase for phrase in phrases if keyword.lower() in phrase.lower()]

	def remove_phrase(self, phrase: str) -> bool:
		"""
		Elimina una frase del archivo.
		Returns: True si se eliminó, False si no se encontró
		"""
		return self.repository.remove(phrase)

	def get_all_phrases(self) -> List[str]:
		"""Obtiene todas las frases"""
		return self.repository.read()
