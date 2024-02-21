from __future__ import annotations

import re
from pathlib import Path
from typing import List

from tealprint import TealPrint

from .models.loot_table import Count, Item, ItemPool, LootTable, Pool
from .patch import Patch


class LootTablePatch(Patch):
    dir = Path("the_vault", "gen", "1.0", "loot_tables")
    file_name_regex = re.compile(r"([a-z_]+)_(\d\d?).*\.json")

    def __init__(self) -> None:
        super().__init__("Loot Tables")

    def patch(self) -> None:
        files = LootTablePatch.get_item_files()
        for f in files:
            TealPrint.info(f"⬆️ Patching {f.name}", push_indent=True)

            self.loot_table = self.load(f, LootTable)

            for entry in self.loot_table.entries:
                for outer_pool in entry.pool:
                    self._patch_pool(f.name, outer_pool)

            self.save(f, self.loot_table)
            TealPrint.pop_indent()

        # files = LootTablePatch.get_treasure_files()
        # for f in files:
        #     TealPrint.info(f"⬆️ Patching {f.name}", push_indent=True)
        #     self.loot_table = self.load(f, LootTable)
        #     self._patch_rolls(f.name)

    def _patch_rolls(self, file_name: str) -> None:
        for entry in self.loot_table.entries:
            new_min = int(entry.roll.min * 1.5)
            new_max = int(entry.roll.max * 1.5)

            TealPrint.verbose(f"🔸 {file_name}: roll({entry.roll.min} -> {new_min}, {entry.roll.max} -> {new_max})")

            entry.roll.min = new_min
            entry.roll.max = new_max

    def _patch_pool(self, file_name: str, outer_pool: Pool) -> None:
        # Patch Items
        for item_pool in outer_pool.pool:
            item = item_pool.item

            if item is None:
                continue

            self._patch_item(file_name, item_pool, item)

        # Add additional items
        match = LootTablePatch.file_name_regex.match(file_name)
        if not match:
            return

        name = match.group(1)
        level = int(match.group(2))
        if name == "ornate_chest":
            # Add chromatic steel ingot
            # if level >= 10 and outer_pool.weight == 20:
            #     item_pool = self._item_pool_chromatic_steel_ingot()
            #     count = item_pool.item.count if item_pool.item is not None else Count("uniform", 0, 0)
            #     outer_pool.pool.append(item_pool)
            #     TealPrint.verbose(f"➕ the_vault:chromatic_steel_ingot min({count.min}) max({count.max})")

            # Add fundamental fundamental focus to level 27
            if level >= 27 and outer_pool.weight == 8:
                item_pool = self._item_pool_fundamental_focus()
                count = item_pool.item.count if item_pool.item is not None else Count("uniform", 0, 0)
                outer_pool.pool.append(item_pool)
                TealPrint.verbose(f"➕ the_vault:fundamental_focus min({count.min}) max({count.max})")

    def _patch_item(self, file_name: str, item_pool: ItemPool, item: Item) -> None:
        if item.id == "the_vault:carbon_nugget":
            new_min = int(item.count.min * 1)
            new_max = int(item.count.max * 1.5)
            if "ornate_chest" in file_name:
                new_min = int(item.count.min * 1.5)
                new_max = int(item.count.max * 1.5)

            TealPrint.verbose(f"🔸 {item.id} min({item.count.min} -> {new_min}) max({item.count.max} -> {new_max})")
            item.count.min = new_min
            item.count.max = new_max

        # elif item.id == "the_vault:chromatic_steel_nugget":
        #     new_weight = 8
        #     new_min = int(item.count.min * 1)
        #     new_max = int(item.count.max * 2)
        #     TealPrint.verbose(
        #         f"🔸 {item.id} weight({item_pool.weight} -> {new_weight}) "
        #         + f" min({item.count.min} -> {new_min}) max({item.count.max} -> {new_max})"
        #     )
        #     item_pool.weight = new_weight
        #     item.count.min = new_min
        #     item.count.max = new_max

        if item.id == "the_vault:fundamental_focus":
            new_weight = 0
            TealPrint.verbose(f"🔥 {item.id} as it's been added on EPIC level")
            item_pool.weight = new_weight

        # elif item.id == "the_vault:silver_scrap":
        #     new_min = int(item.count.min * 1)
        #     new_max = int(item.count.max * 3)
        #     TealPrint.verbose(f"🔸 {item.id} min({item.count.min} -> {new_min}) max({item.count.max} -> {new_max})")
        #     item.count.min = new_min
        #     item.count.max = new_max

    def _item_pool_chromatic_steel_ingot(self) -> ItemPool:
        return ItemPool(
            weight=4,
            item=Item(
                id="the_vault:chromatic_steel_ingot",
                nbt=None,
                count=Count(
                    type="uniform",
                    min=1,
                    max=1,
                ),
            ),
            reference=None,
        )

    def _item_pool_fundamental_focus(self) -> ItemPool:
        return ItemPool(
            weight=4,
            item=Item(
                id="the_vault:fundamental_focus",
                nbt=None,
                count=Count(
                    type="uniform",
                    min=1,
                    max=1,
                ),
            ),
            reference=None,
        )

    @staticmethod
    def get_item_files() -> List[Path]:
        files: List[Path] = []

        # Wooden chests
        files.extend(Patch.get_files_rglob(LootTablePatch.dir, "wooden_chest*.json"))

        # Ornate chests
        files.extend(Patch.get_files_rglob(LootTablePatch.dir, "ornate_chest*.json"))

        # Gilded chests
        files.extend(Patch.get_files_rglob(LootTablePatch.dir, "gilded_chest*.json"))

        # Living chests
        files.extend(Patch.get_files_rglob(LootTablePatch.dir, "living_chest*.json"))

        return files

    @staticmethod
    def get_treasure_files() -> List[Path]:
        files: List[Path] = []

        # Treasure chests
        files.extend(Patch.get_files_rglob(LootTablePatch.dir, "treasure_chest*.json"))

        return files
