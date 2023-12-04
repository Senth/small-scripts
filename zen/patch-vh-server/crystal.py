import copy
from pathlib import Path
from typing import List, Optional

from tealprint import TealPrint

from .models.vault_crystal import OBJECTIVE, Seal, Theme, ThemePool, VaultCrystal
from .patch import Patch


class Crystal(Patch):
    json_file = Path("the_vault", "vault_crystal.json")

    def __init__(self):
        super().__init__("Crystal - Increasing the chance of getting Monoliths in the vault")

    def patch(self) -> None:
        self.crystal = self.load(Crystal.json_file, VaultCrystal)
        self._objective_probabilities()
        # self._objective_min_max()
        # self._remove_christmas_themes()
        self.save(Crystal.json_file, self.crystal)

    def _objective_probabilities(self) -> None:
        """Adds and changes the ranges of the objective probabilities."""

        objectives = self.crystal.OBJECTIVES

        # Safety check to make sure we have the correct number of objectives
        if len(objectives) != 2:
            TealPrint.warning(f"Expected 2 objectives, got {len(objectives)}. Might already be patched.")
            return

        TealPrint.info("🔸 Applying lvl 10-29 objective probabilities", push_indent=True)

        # Copy the second objective to the third objective
        c = copy.deepcopy(objectives[1])
        objectives.append(c)

        # Change the second objective's weights
        # lvl 10-29
        # 40% Monolith
        # 20% Boss
        # 40% Scavenger
        self._patch_objective(objectives[1], "monolith", weight=4)
        self._patch_objective(objectives[1], "boss", weight=2)
        self._patch_objective(objectives[1], "scavenger", weight=4)

        # Change the third objective's level
        objectives[2].minLevel = 30

        TealPrint.pop_indent()

    def _patch_objective(
        self,
        objective: OBJECTIVE,
        type: str,
        min: Optional[int] = None,
        max: Optional[int] = None,
        weight: Optional[int] = None,
    ) -> None:
        """Patches the objective with the given type and weight."""
        for pool in objective.pool:
            if pool.value.type == type:
                if weight:
                    TealPrint.verbose(f"🔸 {type}({objective.minLevel}) weight({pool.weight} -> {weight})")
                    pool.weight = weight
                if min and pool.value.target:
                    TealPrint.verbose(f"🔸 {type}({objective.minLevel}) min({pool.value.target.min} -> {min})")
                    pool.value.target.min = min
                if max and pool.value.target:
                    TealPrint.verbose(f"🔸 {type}({objective.minLevel}) max({pool.value.target.max} -> {max})")
                    pool.value.target.max = max
                break

    def _objective_min_max(self) -> None:
        TealPrint.info("🔸 Applying lvl objective min/max differences", push_indent=True)

        # Patch regular objectives first
        objectives = self.crystal.OBJECTIVES

        # Get a copy of the last objective
        last_objective = copy.deepcopy(objectives[-1])

        for objective in objectives:
            self._patch_objective(objective, "monolith", min=1, max=2)
            self._patch_objective(objective, "boss", min=2, max=3)

        # Patch the last objective
        last_objective.minLevel = 50
        self._patch_objective(last_objective, "monolith", min=2, max=3)
        self._patch_objective(last_objective, "boss", min=3, max=5)
        objectives.append(last_objective)

        # Patch seals
        seals = self.crystal.SEALS
        for seal_name, seal_levels in seals.items():
            if seal_name == "the_vault:crystal_seal_executioner":
                self._patch_seal_objective(seal_name, seal_levels, 2, 3)
            elif seal_name == "the_vault:crystal_seal_cake":
                self._patch_seal_objective(seal_name, seal_levels, 20, 30)

        # Patch an additional level for seals
        TealPrint.info("🔸 Adding an additional level for seals", push_indent=True)
        self._add_seal_objective("the_vault:crystal_seal_executioner", 50, 3, 5)
        self._add_seal_objective("the_vault:crystal_seal_cake", 50, 20, 35)
        TealPrint.pop_indent()
        TealPrint.pop_indent()

    def _add_seal_objective(self, seal_name: str, level: int, min: int, max: int) -> None:
        last_seal = copy.deepcopy(self.crystal.SEALS[seal_name][-1])

        if last_seal.objective is None or last_seal.objective.target is None:
            TealPrint.warning(f"⚠️ No seal objective or target found for {seal_name}")
            return

        last_seal.level = level
        last_seal.objective.target.min = min
        last_seal.objective.target.max = max
        TealPrint.verbose(f"🔸 {seal_name}({last_seal.level}) min({min}) max({max})")

        self.crystal.SEALS[seal_name].append(last_seal)

    def _patch_seal_objective(self, seal_name: str, seal_levels: List[Seal], min: int, max: int) -> None:
        for seal in seal_levels:
            if seal.objective is None or seal.objective.target is None:
                continue

            TealPrint.verbose(
                f"🔸 {seal_name}({seal.level}) "
                + "min({seal.objective.target.min} -> {min}) max({seal.objective.target.max} -> {max})"
            )

            seal.objective.target.min = min
            seal.objective.target.max = max

    def _remove_christmas_themes(self) -> None:
        TealPrint.info("🔸 Removing Christmas themes from the vault")

        for theme_levels in self.crystal.THEMES.values():
            for theme in theme_levels:
                self._patch_theme(theme)

    def _patch_theme(self, theme: Theme) -> None:
        for theme_pool in theme.pool:
            if self._is_christmas_theme(theme_pool):
                theme_pool.weight = 0

    def _is_christmas_theme(self, theme: ThemePool) -> bool:
        if theme.value == "the_vault:classic_vault_festive":
            return True

        if theme.value == "the_vault:classic_vault_gingerbread":
            return True

        return False
