from dataclasses import dataclass

@dataclass
class ServerConfig:
    id: int
    prefix: str
    language: str