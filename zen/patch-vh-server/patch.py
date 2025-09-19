import json
import toml
from pathlib import Path
from typing import Any, Dict, List, TypeVar

from tealprint import TealPrint

from .models.dict import asdict_remove_none

K = TypeVar("K")


class Patch:
    save_dir = Path("config")
    load_dir = Path("config")

    def __init__(self, name: str):
        self.name = name

    def patch(self):
        raise NotImplementedError("Patch.patch() is not implemented")

    @staticmethod
    def get_files_rglob(searchIn: Path, glob: str) -> List[Path]:
        searchIn = Patch.load_dir / searchIn

        files: List[Path] = []
        for f in searchIn.rglob(glob):
            # Remove parent "config_unmodified" from path
            files.append(f.relative_to(Patch.load_dir))

        return files

    def save(self, file: Path, object: Any) -> None:
        file = Patch.save_dir / file
        with file.open("w") as f:
            json.dump(asdict_remove_none(object), f, indent=2)
            TealPrint.info(f"💾 Saved {file.name}")

    def load(self, file: Path, Klass: K) -> K:
        file = Patch.load_dir / file
        with file.open() as f:
            json_dict = json.load(f)
            return Klass.from_dict(json_dict)

    def save_toml(self, file: Path, object: Dict[str, Any]) -> None:
        file = Patch.save_dir / file
        with file.open("w") as f:
            toml.dump(object, f)
            TealPrint.info(f"💾 Saved {file.name}")

    def load_toml(self, file: Path) -> Dict[str, Any]:
        file = Patch.load_dir / file
        with file.open() as f:
            return toml.load(f)

    def save_json(self, file: Path, object: Dict[str, Any]) -> None:
        file = Patch.save_dir / file
        with file.open("w") as f:
            json.dump(object, f, indent=2)
            TealPrint.info(f"💾 Saved {file.name}")

    def load_json(self, file: Path) -> Dict[str, Any]:
        file = Patch.load_dir / file
        with file.open() as f:
            return json.load(f)

    def save_raw(self, file: Path, data: str) -> None:
        file = Patch.save_dir / file
        with file.open("w") as f:
            f.write(data)
            TealPrint.info(f"💾 Saved {file.name}")

    def load_raw(self, file: Path) -> str:
        file = Patch.load_dir / file
        with file.open() as f:
            return f.read()
