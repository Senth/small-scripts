from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class AdditionalOutputRarityChances:
    SCRAPPY: float
    COMMON: float
    RARE: float
    EPIC: float
    OMEGA: float

    @staticmethod
    def from_dict(obj: Any) -> "AdditionalOutputRarityChances":
        _SCRAPPY = float(obj.get("SCRAPPY"))
        _COMMON = float(obj.get("COMMON"))
        _RARE = float(obj.get("RARE"))
        _EPIC = float(obj.get("EPIC"))
        _OMEGA = float(obj.get("OMEGA"))
        return AdditionalOutputRarityChances(_SCRAPPY, _COMMON, _RARE, _EPIC, _OMEGA)


@dataclass
class Output:
    chance: float
    stack: Stack
    minCount: int
    maxCount: int

    @staticmethod
    def from_dict(obj: Any) -> Output:
        _chance = float(obj.get("chance"))
        _stack = Stack.from_dict(obj.get("stack"))
        _minCount = int(obj.get("minCount"))
        _maxCount = int(obj.get("maxCount"))
        return Output(_chance, _stack, _minCount, _maxCount)


@dataclass
class MainOutput:
    chance: float
    stack: Stack
    minCount: int
    maxCount: int

    @staticmethod
    def from_dict(obj: Any) -> "MainOutput":
        _chance = float(obj.get("chance"))
        _stack = Stack.from_dict(obj.get("stack"))
        _minCount = int(obj.get("minCount"))
        _maxCount = int(obj.get("maxCount"))
        return MainOutput(_chance, _stack, _minCount, _maxCount)


@dataclass
class VaultRecycler:
    processingTickTime: int
    additionalOutputRarityChances: AdditionalOutputRarityChances
    gearRecyclingOutput: Outputs
    charmRecyclingOutput: Outputs
    magnetRecyclingOutput: Outputs
    trinketRecyclingOutput: Outputs
    jewelRecyclingOutput: Outputs
    inscriptionRecyclingOutput: Outputs

    @staticmethod
    def from_dict(obj: Any) -> VaultRecycler:
        _processingTickTime = int(obj.get("processingTickTime"))
        _additionalOutputRarityChances = AdditionalOutputRarityChances.from_dict(
            obj.get("additionalOutputRarityChances")
        )
        _gearRecyclingOutput = Outputs.from_dict(obj.get("gearRecyclingOutput"))
        _charmRecyclingOutput = Outputs.from_dict(obj.get("charmRecyclingOutput"))
        _magnetRecyclingOutput = Outputs.from_dict(obj.get("magnetRecyclingOutput"))
        _trinketRecyclingOutput = Outputs.from_dict(obj.get("trinketRecyclingOutput"))
        _jewelRecyclingOutput = Outputs.from_dict(obj.get("jewelRecyclingOutput"))
        _inscriptionRecyclingOutput = Outputs.from_dict(
            obj.get("inscriptionRecyclingOutput")
        )
        return VaultRecycler(
            _processingTickTime,
            _additionalOutputRarityChances,
            _gearRecyclingOutput,
            _charmRecyclingOutput,
            _magnetRecyclingOutput,
            _trinketRecyclingOutput,
            _jewelRecyclingOutput,
            _inscriptionRecyclingOutput,
        )


@dataclass
class Stack:
    item: str

    @staticmethod
    def from_dict(obj: Any) -> "Stack":
        _item = str(obj.get("item"))
        return Stack(_item)


@dataclass
class Outputs:
    mainOutput: Output
    extraOutput1: Output
    extraOutput2: Output

    @staticmethod
    def from_dict(obj: Any) -> Outputs:
        _mainOutput = Output.from_dict(obj.get("mainOutput"))
        _extraOutput1 = Output.from_dict(obj.get("extraOutput1"))
        _extraOutput2 = Output.from_dict(obj.get("extraOutput2"))
        return Outputs(_mainOutput, _extraOutput1, _extraOutput2)


# Example Usage
# jsonstring = json.loads(myjsonstring)
# root = Root.from_dict(jsonstring)
