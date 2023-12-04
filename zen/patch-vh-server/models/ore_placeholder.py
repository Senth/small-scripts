from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List


@dataclass
class Level:
    level: int
    probability: float
    success: Dict[str, int]
    failure: Dict[str, int]

    @staticmethod
    def from_dict(obj: Any) -> Level:
        _level = int(obj.get("level"))
        _probability = float(obj.get("probability"))
        _success = obj.get("success")
        _failure = obj.get("failure")
        return Level(_level, _probability, _success, _failure)


@dataclass
class OrePlaceholder:
    tile_processors: List[TileProcessor]

    @staticmethod
    def from_dict(obj: Any) -> OrePlaceholder:
        _tile_processors = [TileProcessor.from_dict(y) for y in obj.get("tile_processors")]
        return OrePlaceholder(_tile_processors)

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TileProcessor:
    type: str
    target: str
    levels: List[Level]

    @staticmethod
    def from_dict(obj: Any) -> TileProcessor:
        _type = str(obj.get("type"))
        _target = str(obj.get("target"))
        _levels = [Level.from_dict(y) for y in obj.get("levels")]
        return TileProcessor(_type, _target, _levels)
