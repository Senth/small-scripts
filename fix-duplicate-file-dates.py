#!/usr/bin/python3
import argparse
from pathlib import Path
import re
from tealprint import TealPrint
import colored

parser = argparse.ArgumentParser()
parser.add_argument("dir", help="The directory to fix the file names in")
parser.add_argument("--dry-run", action="store_true", help="Don't actually fix the file names, just print them")

args = parser.parse_args()
dir = Path(args.dir)

regex = r"\d{4}-\d{2}-\d{2} \d{2}\.\d{2}\.\d{2} (\d{4}.\d{2}.\d{2}.\d{2}.\d{2}.\d{2}|\d{11}|\d{8}_\d{6})"

def fix_dir(dir: Path):
    TealPrint.info(f"{dir}", color=colored.attr('bold'), push_indent=True)
    for file in dir.iterdir():
        if file.is_dir():
            fix_dir(file)
            continue
                
        matches = re.match(regex, file.name)
        if matches:
            extra = matches.groups()
            new_name = file.name.replace(f" {extra[0]}", "")
            TealPrint.info(f"{file.name} -> {new_name}", color=colored.fg('green'))
            
            if not args.dry_run:
                file.rename(file.parent / new_name)
    
    TealPrint.pop_indent()

fix_dir(dir)
