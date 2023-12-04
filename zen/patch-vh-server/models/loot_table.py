from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional

from .dict import asdict_remove_none


@dataclass
class Count:
    type: str
    min: int
    max: int

    @staticmethod
    def from_dict(obj: Any) -> Count:
        _type = str(obj.get("type"))
        _min = int(obj.get("min"))
        _max = int(obj.get("max"))
        return Count(_type, _min, _max)


@dataclass
class Entry:
    roll: Roll
    pool: List[Pool]

    @staticmethod
    def from_dict(obj: Any) -> Entry:
        _roll = Roll.from_dict(obj.get("roll"))
        _pool = [Pool.from_dict(y) for y in obj.get("pool")]
        return Entry(_roll, _pool)


@dataclass
class Item:
    id: str
    nbt: Optional[str]
    count: Count

    @staticmethod
    def from_dict(obj: Any) -> Item:
        _id = str(obj.get("id"))
        _count = Count.from_dict(obj.get("count"))

        _nbt = None
        if "nbt" in obj:
            _nbt = str(obj.get("nbt"))

        return Item(_id, _nbt, _count)


@dataclass
class Pool:
    weight: int
    pool: List[ItemPool]

    @staticmethod
    def from_dict(obj: Any) -> Pool:
        _weight = int(obj.get("weight"))
        _pool = [ItemPool.from_dict(y) for y in obj.get("pool")]
        return Pool(_weight, _pool)


@dataclass
class ItemPool:
    weight: int
    item: Optional[Item]
    reference: Optional[str]

    @staticmethod
    def from_dict(obj: Any) -> ItemPool:
        _weight = int(obj.get("weight"))

        _item = None
        if "item" in obj:
            _item = Item.from_dict(obj.get("item"))

        _reference = None
        if "reference" in obj:
            _reference = str(obj.get("reference"))

        return ItemPool(_weight, _item, _reference)


@dataclass
class Roll:
    type: str
    min: int
    max: int

    @staticmethod
    def from_dict(obj: Any) -> Roll:
        _type = str(obj.get("type"))
        _min = int(obj.get("min"))
        _max = int(obj.get("max"))
        return Roll(_type, _min, _max)


@dataclass
class LootTable:
    entries: List[Entry]

    @staticmethod
    def from_dict(obj: Any) -> LootTable:
        _entries = [Entry.from_dict(y) for y in obj.get("entries")]
        return LootTable(_entries)

    def as_dict(self) -> Any:
        return asdict_remove_none(self)
