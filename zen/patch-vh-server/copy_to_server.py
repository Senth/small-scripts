import shutil
from dataclasses import dataclass
from pathlib import Path

import colored
from tealprint import TealPrint


@dataclass
class _DirInfo:
    from_dir: str
    to_dir: str


_curse_dir = Path("D:\\Curse\\Minecraft\\Instances\\Vault-Hunters")
_nextcloud_dir = Path("E:\\nextcloud\\Minecraft\\server files\\VaultHunters 1.18")

_dirs_and_files = [
    _DirInfo("config", "config"),
    _DirInfo("config", "config_unmodified"),
    _DirInfo("defaultconfigs", "defaultconfigs"),
    _DirInfo("mods", "mods"),
    _DirInfo("packmenu", "packmenu"),
    _DirInfo("patchouli_books", "patchouli_books"),
    _DirInfo("scripts", "scripts"),
    _DirInfo("patchouli_data.json", "patchouli_data.json"),
]


def server_needs_update() -> bool:
    """Checks if the files are newer in curseforge than in nextcloud"""

    TealPrint.info("Checking if server needs update", color=colored.attr("bold"), push_indent=True)

    curse_path = _curse_dir / "patchouli_data.json"
    nextcloud_path = _nextcloud_dir / "patchouli_data.json"

    if not nextcloud_path.exists():
        TealPrint.info("⬇️ Server needs update", pop_indent=True)
        return True

    # Check if curse is newer
    curse_mod_time = curse_path.stat().st_mtime
    nextcloud_mod_time = nextcloud_path.stat().st_mtime
    if curse_mod_time > nextcloud_mod_time:
        TealPrint.info("⬇️ Server needs update", pop_indent=True)
        return True

    TealPrint.info("✅ Server is up to date", pop_indent=True)
    return False


def copy_to_server():
    TealPrint.info("Copying files to nextcloud server", color=colored.attr("bold"), push_indent=True)

    for current in _dirs_and_files:
        TealPrint.info(f"{current.from_dir} -> {current.to_dir}", push_indent=True)
        curse_path = _curse_dir / current.from_dir
        nextcloud_path = _nextcloud_dir / current.to_dir

        # Remove existing in nextcloud
        if nextcloud_path.is_dir():
            TealPrint.info("🔥 Removing existing dir")
            shutil.rmtree(nextcloud_path)
        elif nextcloud_path.is_file():
            TealPrint.info("🔥 Removing existing file")
            nextcloud_path.unlink()

        # Copy
        TealPrint.info("Copying...")
        if curse_path.is_dir():
            shutil.copytree(curse_path, nextcloud_path)
        elif curse_path.is_file():
            shutil.copy2(curse_path, nextcloud_path)

        TealPrint.pop_indent()

    TealPrint.pop_indent()
