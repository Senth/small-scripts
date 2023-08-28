#!/usr/bin/python3

import argparse
import re
from datetime import datetime
from pathlib import Path
import shutil
from tealprint import TealPrint, TealConfig, TealLevel
import colored

from exif import Image

parser = argparse.ArgumentParser()
parser.add_argument("in_dir")
parser.add_argument("out_dir")
parser.add_argument("--keep-name", action="store_true", help="Appends the original filename to the new name")
parser.add_argument("--keep-structure", action="store_true", help="Keep the original directory structure. Can't be used with --sort-by")
parser.add_argument("--move", action="store_true", help="Move files instead of copying")
parser.add_argument("--sort-by", choices=["none", "year"], default="none", help="Create folders by year. Can't be used with --keep-structure")
parser.add_argument("--verbose", action="store_true", help="Print more information")
args = parser.parse_args()

if args.verbose:
    TealConfig.level = TealLevel.verbose


exif_regex = r"(\d{4}).(\d{2}).(\d{2}) (\d{2}).(\d{2}).(\d{2})"

valid_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp", ".cr2", ".nef", ".dng", ".raf", ".arw", ".rw2", ".nrw", ".k25", ".orf", ".srw", ".pef", ".3fr", ".mef", ".mos", ".mrw", ".sr2", ".x3f", ".erf", ".srw"]

def rename_exif(date: str) -> str:
    matches = re.match(exif_regex, date)
    if matches:
        year, month, day, hour, minute, second = matches.groups()
        return f"{year}-{month}-{day} {hour}.{minute}.{second}"

    return ""


def generate_out_file(file: Path, full_name: str, date: datetime, out_dir: Path) -> Path:
    if len(full_name) == 0:
        full_name = date.strftime("%Y-%m-%d %H.%M.%S")
    if args.keep_name:
        full_name += f" {file.name}"
    else:
        full_name += f"{file.suffix}"
        
    # Set the correct year folder
    if args.sort_by == "year" and not args.keep_structure:
        out_dir = out_dir.joinpath(str(date.year))
        out_dir.mkdir(exist_ok=True)

    return out_dir.joinpath(full_name)
    
def is_valid_file(file: Path) -> bool:
    if file.suffix.lower() in valid_extensions:
        return True
    
    return False

def copy_file(file: Path, out_name: Path):
    if not file.exists():
        return
    
    if args.move:
        TealPrint.verbose(f"{file} -> {out_name}")
        file.replace(out_name)
    elif not out_name.exists():
        TealPrint.verbose(f"{file} -> {out_name}")
        shutil.copy2(file, out_name)
    else:
        TealPrint.debug(f"{file} -> {out_name} (already exists)", color=colored.fg("blue"))

def rename_files(in_dir: Path, out_dir: Path):
    for file in Path(in_dir).iterdir():
        # Directory
        if file.is_dir():
            TealPrint.info(f"{file}", color=colored.attr("bold"), push_indent=True)
            
            next_out_dir = out_dir
            if args.keep_structure:
                next_out_dir = out_dir.joinpath(file.name)
                next_out_dir.mkdir(exist_ok=True)
                
            rename_files(file, next_out_dir)
            
            if args.move:
                file.rmdir()
                
            TealPrint.pop_indent()
            continue
            
        # File
        if not is_valid_file(file):
            if file.suffix.lower() != ".xmp":
                TealPrint.warning(f"Unspported extension: {file}")
            continue
        
        mtime = file.stat().st_mtime
        date = datetime.fromtimestamp(mtime)

        full_name = ""
        try:
            with open(file, "rb") as image_file:
                image = Image(image_file)
                if image.has_exif:
                    datetime_original = image.get("datetime_original")
                    datetime_ = image.get("datetime")
                    if datetime_original:
                        full_name = rename_exif(datetime_original)
                    elif datetime_:
                        full_name = rename_exif(datetime_)
        except Exception:
            pass

        
        out_name = generate_out_file(file, full_name, date, out_dir)
        copy_file(file, out_name)
        
        # Copy XMP file if it exists
        copy_file(file.with_suffix(".xmp"), out_name.with_suffix(".xmp"))
        copy_file(file.with_suffix(".XMP"), out_name.with_suffix(".xmp"))


rename_files(Path(args.in_dir), Path(args.out_dir))
