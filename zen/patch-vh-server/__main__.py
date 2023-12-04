import os
from typing import List

from argparse import ArgumentParser
from colored import attr
from tealprint import TealConfig, TealLevel, TealPrint

from .copy_to_server import copy_to_server, server_needs_update
from .ftbbackup import FtbBackup

# from .crystal import Crystal
from .loot_table import LootTablePatch
from .ore import Ore
from .patch import Patch

patches: List[Patch] = [
    LootTablePatch(),
    # Crystal(),
    # Ore(),
    FtbBackup(),
]

def main():
    parser = ArgumentParser()
    parser.add_argument("dir", help="The directory with all the configuration files to patch")
    
    args = parser.parse_args()
    os.chdir(args.dir)

    
    TealConfig.level = TealLevel.verbose

    # Copy files to server if needed
    if server_needs_update():
        copy_to_server()

    # Patch the game
    for patch in patches:
        TealPrint.info(patch.name, color=attr("bold"), push_indent=True)
        patch.patch()
        TealPrint.info("", pop_indent=True)


if __name__ == "__main__":
    main()
