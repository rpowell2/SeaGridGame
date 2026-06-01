# v0_1/world/chunk.py

from dataclasses import dataclass, field

@dataclass
class Chunk:
    x: int
    y: int
    tiles: list = field(default_factory=list)
    pois: list = field(default_factory=list)