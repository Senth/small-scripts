from tealprint import TealPrint
from pathlib import Path

from .patch import Patch
from .models.vault_recycler import VaultRecycler, Outputs


class Recycler(Patch):
    json_file = Path("the_vault", "vault_recycler.json")

    def __init__(self):
        super().__init__("Vault Recycler")

    def patch(self) -> None:
        self.recycler = self.load(Recycler.json_file, VaultRecycler)
        self._vault_scrap_quantity()
        self.save(Recycler.json_file, self.recycler)

    def _vault_scrap_quantity(self) -> None:
        """Increases the quantity of vault scraps."""

        self._patch_outputs(self.recycler.gearRecyclingOutput, "Gear")
        self._patch_outputs(self.recycler.charmRecyclingOutput, "Charm")
        self._patch_outputs(self.recycler.magnetRecyclingOutput, "Magnet")

    def _patch_outputs(self, outputs: Outputs, name: str) -> None:
        """Patches the outputs of the recycler."""

        TealPrint.info(f"⬆️ Patching {name} Recycling Output", push_indent=True)

        min_prev = outputs.mainOutput.minCount
        max_prev = outputs.mainOutput.maxCount

        outputs.mainOutput.minCount = 8
        outputs.mainOutput.maxCount = 16

        TealPrint.info(
            f"🔸 the_vault:vault_scrap {min_prev}-{max_prev} -> {outputs.mainOutput.minCount}-{outputs.mainOutput.maxCount}"
        )

        TealPrint.pop_indent()
