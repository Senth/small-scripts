from pathlib import Path

from .patch import Patch
from tealprint import TealPrint
import toml


class SimpleBackup(Patch):
    json_file = Path("simplebackups-common.toml")

    def __init__(self):
        super().__init__("Simple Backup")

    def patch(self) -> None:
        config = self.load_toml(SimpleBackup.json_file)
        config["timer"] = 360
        config["backupsToKeep"] = 2
        config["maxDiskSize"] = "10 GB"
        self.save_toml(SimpleBackup.json_file, config)
