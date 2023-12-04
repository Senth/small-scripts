from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class SealLayout:
    type: str
    tunnel_span: int
    objective_probability: Optional[float]
    half_length: Optional[int]
    rotation: Optional[str]
    vertices: Optional[List[Vertex]]

    @staticmethod
    def from_dict(obj: Any) -> SealLayout:
        _type = str(obj.get("type"))
        _tunnel_span = int(obj.get("tunnel_span"))

        _objective_probability = None
        if "objective_probability" in obj:
            _objective_probability = float(obj.get("objective_probability"))

        _half_length = None
        if "half_length" in obj:
            _half_length = int(obj.get("half_length"))

        _rotation = None
        if "rotation" in obj:
            _rotation = str(obj.get("rotation"))

        _vertices = None
        if "vertices" in obj:
            _vertices = [Vertex.from_dict(y) for y in obj.get("vertices")]

        return SealLayout(_type, _tunnel_span, _objective_probability, _half_length, _rotation, _vertices)


@dataclass
class Modifier:
    modifier: str
    count: int

    @staticmethod
    def from_dict(obj: Any) -> "Modifier":
        _modifier = str(obj.get("modifier"))
        _count = int(obj.get("count"))
        return Modifier(_modifier, _count)


@dataclass
class MODIFIERSTABILITY:
    craftsBeforeInstability: int
    instabilityPerCraft: float
    instabilityCap: float
    curseInstabilityThreshold: float
    curseChanceMin: float
    curseChanceMax: float
    curseColor: str

    @staticmethod
    def from_dict(obj: Any) -> "MODIFIERSTABILITY":
        _craftsBeforeInstability = int(obj.get("craftsBeforeInstability"))
        _instabilityPerCraft = float(obj.get("instabilityPerCraft"))
        _instabilityCap = float(obj.get("instabilityCap"))
        _curseInstabilityThreshold = float(obj.get("curseInstabilityThreshold"))
        _curseChanceMin = float(obj.get("curseChanceMin"))
        _curseChanceMax = float(obj.get("curseChanceMax"))
        _curseColor = str(obj.get("curseColor"))
        return MODIFIERSTABILITY(
            _craftsBeforeInstability,
            _instabilityPerCraft,
            _instabilityCap,
            _curseInstabilityThreshold,
            _curseChanceMin,
            _curseChanceMax,
            _curseColor,
        )


@dataclass
class MOTES:
    clarityLevelCost: int
    purityLevelCost: int
    sanctityLevelCost: int

    @staticmethod
    def from_dict(obj: Any) -> "MOTES":
        _clarityLevelCost = int(obj.get("clarityLevelCost"))
        _purityLevelCost = int(obj.get("purityLevelCost"))
        _sanctityLevelCost = int(obj.get("sanctityLevelCost"))
        return MOTES(_clarityLevelCost, _purityLevelCost, _sanctityLevelCost)


@dataclass
class OBJECTIVE:
    minLevel: int
    pool: List[ObjectivePool]

    @staticmethod
    def from_dict(obj: Any) -> "OBJECTIVE":
        _minLevel = int(obj.get("minLevel"))
        _pool = [ObjectivePool.from_dict(y) for y in obj.get("pool")]
        return OBJECTIVE(_minLevel, _pool)


@dataclass
class ObjectivePool:
    value: SealObjective
    weight: int

    @staticmethod
    def from_dict(obj: Any) -> "ObjectivePool":
        _value = SealObjective.from_dict(obj.get("value"))
        _weight = int(obj.get("weight"))
        return ObjectivePool(_value, _weight)


@dataclass
class SealObjective:
    type: str
    objective_probability: Optional[float]
    target: Optional[Target]

    @staticmethod
    def from_dict(obj: Any) -> "SealObjective":
        _type = str(obj.get("type"))

        _objective_probability = None
        if "objective_probability" in obj:
            _objective_probability = float(obj.get("objective_probability"))

        _target = None
        if "target" in obj:
            _target = Target.from_dict(obj.get("target"))

        return SealObjective(_type, _objective_probability, _target)


@dataclass
class ThemePool:
    value: str
    weight: int

    @staticmethod
    def from_dict(obj: Any) -> "ThemePool":
        _value = str(obj.get("value"))
        _weight = int(obj.get("weight"))
        return ThemePool(_value, _weight)


@dataclass
class VaultCrystal:
    MODIFIER_STABILITY: MODIFIERSTABILITY
    MOTES: MOTES
    THEMES: Dict[str, List[Theme]]
    LAYOUTS: List[Layout]
    OBJECTIVES: List[OBJECTIVE]
    SEALS: Dict[str, List[Seal]]

    @staticmethod
    def from_dict(obj: Any) -> VaultCrystal:
        _MODIFIER_STABILITY = MODIFIERSTABILITY.from_dict(obj.get("MODIFIER_STABILITY"))
        _MOTES = MOTES.from_dict(obj.get("MOTES"))
        _THEMES = {k: [Theme.from_dict(theme) for theme in v] for k, v in obj.get("THEMES").items()}
        _LAYOUTS = [Layout.from_dict(y) for y in obj.get("LAYOUTS")]
        _OBJECTIVES = [OBJECTIVE.from_dict(y) for y in obj.get("OBJECTIVES")]
        _SEALS = {k: [Seal.from_dict(seal) for seal in v] for k, v in obj.get("SEALS").items()}
        return VaultCrystal(_MODIFIER_STABILITY, _MOTES, _THEMES, _LAYOUTS, _OBJECTIVES, _SEALS)


@dataclass
class Target:
    type: str
    min: Optional[int]
    max: Optional[int]
    count: Optional[int]

    @staticmethod
    def from_dict(obj: Any) -> Target:
        _type = str(obj.get("type"))

        _min = None
        if "min" in obj:
            _min = int(obj.get("min"))

        _max = None
        if "max" in obj:
            _max = int(obj.get("max"))

        _count = None
        if "count" in obj:
            _count = int(obj.get("count"))
        return Target(_type, _min, _max, _count)


@dataclass
class ThemeIdentifier:
    type: str
    id: str

    @staticmethod
    def from_dict(obj: Any) -> ThemeIdentifier:
        _type = str(obj.get("type"))
        _id = str(obj.get("id"))
        return ThemeIdentifier(_type, _id)


@dataclass
class Seal:
    level: Optional[int]
    preventRandomModifiers: Optional[bool]
    canBeModified: Optional[bool]
    input: Optional[List[str]]
    objective: Optional[SealObjective]
    layout: Optional[SealLayout]
    theme: Optional[ThemeIdentifier]
    modifiers: Optional[List[Modifier]]

    @staticmethod
    def from_dict(obj: Any) -> Seal:
        _level = None
        if "level" in obj:
            _level = int(obj.get("level"))

        _preventRandomModifiers = None
        if "preventRandomModifiers" in obj:
            _preventRandomModifiers = bool(obj.get("preventRandomModifiers"))

        _canBeModified = None
        if "canBeModified" in obj:
            _canBeModified = bool(obj.get("canBeModified"))

        _input = None
        if "input" in obj:
            _input = [str(x) for x in obj.get("input")]

        _objective = None
        if "objective" in obj:
            _objective = SealObjective.from_dict(obj.get("objective"))

        _layout = None
        if "layout" in obj:
            _layout = SealLayout.from_dict(obj.get("layout"))

        _theme = None
        if "theme" in obj:
            _theme = ThemeIdentifier.from_dict(obj.get("theme"))

        _modifiers = None
        if "modifiers" in obj:
            _modifiers = [Modifier.from_dict(y) for y in obj.get("modifiers")]

        return Seal(_level, _preventRandomModifiers, _canBeModified, _input, _objective, _layout, _theme, _modifiers)


@dataclass
class Theme:
    minLevel: int
    pool: List[ThemePool]

    @staticmethod
    def from_dict(obj: Any) -> Theme:
        _minLevel = int(obj.get("minLevel"))
        _pool = [ThemePool.from_dict(y) for y in obj.get("pool")]
        return Theme(_minLevel, _pool)


@dataclass
class Vertex:
    x: int
    z: int

    @staticmethod
    def from_dict(obj: Any) -> Vertex:
        _x = int(obj.get("x"))
        _z = int(obj.get("z"))
        return Vertex(_x, _z)


@dataclass
class Layout:
    minLevel: int
    pool: List[LayoutPool]

    @staticmethod
    def from_dict(obj: Any) -> Layout:
        _minLevel = int(obj.get("minLevel"))
        _pool = [LayoutPool.from_dict(y) for y in obj.get("pool")]
        return Layout(_minLevel, _pool)


@dataclass
class LayoutPool:
    value: LayoutAlgorithm
    weight: int

    @staticmethod
    def from_dict(obj: Any) -> LayoutPool:
        _value = LayoutAlgorithm.from_dict(obj.get("value"))
        _weight = int(obj.get("weight"))
        return LayoutPool(_value, _weight)


@dataclass
class LayoutAlgorithm:
    type: str
    tunnel_span: Optional[int]
    half_length: Optional[int]
    rotation: Optional[str]
    radius: Optional[int]
    vertices: Optional[List[Vertex]]

    @staticmethod
    def from_dict(obj: Any) -> LayoutAlgorithm:
        _type = str(obj.get("type"))

        _tunnel_span = None
        if "tunnel_span" in obj:
            _tunnel_span = int(obj.get("tunnel_span"))

        _half_length = None
        if "half_length" in obj:
            _half_length = int(obj.get("half_length"))

        _rotation = None
        if "rotation" in obj:
            _rotation = str(obj.get("rotation"))

        _radius = None
        if "radius" in obj:
            _radius = int(obj.get("radius"))

        _vertices = None
        if "vertices" in obj:
            _vertices = [Vertex.from_dict(y) for y in obj.get("vertices")]

        return LayoutAlgorithm(_type, _tunnel_span, _half_length, _rotation, _radius, _vertices)
