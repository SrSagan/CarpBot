from dataclasses import dataclass
from typing import List, Optional


@dataclass
class LinkGroup:
	group: str
	name: str
	data: Optional[List[str]] = None

	def __post_init__(self):
		if self.data is None:
			self.data = []
