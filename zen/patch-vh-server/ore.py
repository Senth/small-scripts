from copy import deepcopy
from pathlib import Path
from typing import List

from tealprint import TealPrint

from .models.ore_placeholder import Level, OrePlaceholder
from .patch import Patch


class Ore(Patch):
    dir = Path("the_vault", "gen", "1.0", "palettes")

    def __init__(self):
        super().__init__("Ore - Increasing the chance of getting ores in the vault")

    def patch(self) -> None:
        for f in Ore.get_files():
            self.ore = self.load(f, OrePlaceholder)

            TealPrint.info(f"⬆️ Patching {f.parent.name}/{f.name}", push_indent=True)
            self._all_ores()
            self._more_levels()

            self.save(f, self.ore)
            TealPrint.pop_indent()

    def _all_ores(self) -> None:
        for tile_processor in self.ore.tile_processors:
            for level in tile_processor.levels:
                self._patch_level(level)

    def _patch_level(self, level: Level) -> None:
        # Skip level 0
        if level.level == 0:
            return

        # Black Opal
        weight = Ore._get_ore(level, "black_opal")
        new_weight = int(weight * 2)
        Ore._set_ore(level, "black_opal", new_weight)
        TealPrint.verbose(f"🔸 Black Opal({level.level}): weight({weight} -> {new_weight})")

    def _more_levels(self) -> None:
        last_level = self.ore.tile_processors[0].levels[-1]

        # Add levels for 50-100, in steps of 10
        last_probability = last_level.probability
        for level in range(50, 101, 10):
            new_probability = round(last_probability + 0.02, 2)
            last_probability = new_probability

            new_level = deepcopy(last_level)
            new_level.level = level
            new_level.probability = new_probability

            self.ore.tile_processors[0].levels.append(new_level)
            TealPrint.verbose(f"➕ Level({level}): probability({last_level.probability} -> {new_probability})")

    @staticmethod
    def _get_ore(level: Level, name: str) -> int:
        success = level.success

        for key, value in success.items():
            if name in key:
                return value

        return 0

    @staticmethod
    def _set_ore(level: Level, name: str, value: int) -> None:
        success = level.success

        for key in success.keys():
            if name in key:
                success[key] = value
                return

    @staticmethod
    def get_files() -> List[Path]:
        return Patch.get_files_rglob(Ore.dir, "ore_placeholder*.json")
