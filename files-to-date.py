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
parser.add_argument("--invalid-files-dir", help="Directory to copy or move invalid files and files without a date to")
parser.add_argument("--keep-name", action="store_true", help="Appends the original filename to the new name")
parser.add_argument("--keep-structure", action="store_true", help="Keep the original directory structure. Can't be used with --sort-by")
parser.add_argument("--move", action="store_true", help="Move files instead of copying")
parser.add_argument("--sort-by", choices=["none", "year"], default="none", help="Create folders by year. Can't be used with --keep-structure")
parser.add_argument("--verbose", action="store_true", help="Print more information")
parser.add_argument("--dry-run", action="store_true", help="Don't actually rename the files, just print them")
args = parser.parse_args()

if args.verbose:
    TealConfig.level = TealLevel.verbose

invalid_dir: Path | None = None
no_date_dir: Path | None = None
if args.invalid_files_dir:
    dir = Path(args.invalid_files_dir)
    dir.mkdir(exist_ok=True)
    
    invalid_dir = dir / "invalid format"
    invalid_dir.mkdir(exist_ok=True)
    
    no_date_dir = dir / "no date"
    no_date_dir.mkdir(exist_ok=True)
    


exif_regex = r"(\d{4}).(\d{2}).(\d{2}) (\d{2}).(\d{2}).(\d{2})"

valid_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp", ".cr2", ".nef", ".dng", ".raf", ".arw", ".rw2", ".nrw", ".k25", ".orf", ".srw", ".pef", ".3fr", ".mef", ".mos", ".mrw", ".sr2", ".x3f", ".erf", ".srw"]

def rename_exif(date_str: str) -> (str, datetime):
    matches = re.match(exif_regex, date_str)
    if matches:
        
        year, month, day, hour, minute, second = matches.groups()
        date_str = f"{year}-{month}-{day} {hour}.{minute}.{second}"
        
        # Convert to datetime
        date = datetime.strptime(date_str, "%Y-%m-%d %H.%M.%S")
        
        return date_str, date

    return "", None

date_regex = r"((\d{4}).(\d{2}).(\d{2}).(\d{2}).(\d{2}).(\d{2})|\d{11}|\d{8}_\d{6})"

def rename_date_filename(file: Path) -> (str, datetime):
    matches = re.search(date_regex, file.stem)
    if matches:
        match_str = matches.group(0)
        
        # Convert to datetime
        if len(match_str) == 19:
            _, year, month, day, hour, minute, second = matches.groups()
            date_str = f"{year}-{month}-{day} {hour}.{minute}.{second}"
            date = datetime.strptime(date_str, "%Y-%m-%d %H.%M.%S")
        elif len(match_str) == 11:
            day = match_str[:-3]
            date = datetime.strptime(day, "%Y%m%d")
        elif len(match_str) == 15:
            date = datetime.strptime(match_str, "%Y%m%d_%H%M%S")
            
        
        # Convert to the string format we want
        dateStr = date.strftime("%Y-%m-%d %H.%M.%S")
        
        return dateStr, date

    return "", None


def generate_out_file(file: Path, full_name: str, date: datetime, out_dir: Path) -> Path:
    if len(full_name) == 0:
        full_name = date.strftime("%Y-%m-%d %H.%M.%S")
    if args.keep_name:
        # Strip the date from the original filename
        if re.match(date_regex, file.stem):
            stripped_filename = re.sub(date_regex, "", file.stem).strip()
            if len(stripped_filename) > 0:
                full_name += f" {stripped_filename}"
            else:
                full_name += file.suffix
        else:
            full_name += f" {file.name}"
    else:
        full_name += f"{file.suffix}"
        
    # Convert jpeg to jpg
    if full_name.lower().endswith(".jpeg"):
        full_name = full_name[:-4] + "jpg"
        
    # Convert uppercase extensions to lowercase for all extensions
    # suffix = file.suffix.lower()
    # full_name = full_name[:-len(suffix)] + suffix
        
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
        if not args.dry_run:
            file.replace(out_name)
    elif not out_name.exists():
        TealPrint.verbose(f"{file} -> {out_name}")
        if not args.dry_run:
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
                copy_file(file, invalid_dir / file.name)
            continue
        
        mtime = file.stat().st_mtime
        ctime = file.stat().st_ctime
        
        if mtime < ctime:
            date = datetime.fromtimestamp(ctime)
        else:
            date = datetime.fromtimestamp(mtime)

        full_name = ""
        try:
            with open(file, "rb") as image_file:
                image = Image(image_file)
                if image.has_exif:
                    datetime_original = image.get("datetime_original")
                    datetime_ = image.get("datetime")
                    if datetime_original:
                        full_name, date = rename_exif(datetime_original)
                    elif datetime_:
                        full_name, date = rename_exif(datetime_)
                else: # No exif data
                    TealPrint.warning(f"No exif data: {file}")
                    copy_file(file, no_date_dir / file.name)
                    continue
                    
        except Exception as e:
            TealPrint.warning(f"Error reading exif data: {file}, exception: {e}")
            copy_file(file, no_date_dir / file.name)
            pass

        
        out_name = generate_out_file(file, full_name, date, out_dir)
        copy_file(file, out_name)
        
        # Copy XMP file if it exists
        copy_file(file.with_suffix(".xmp"), out_name.with_suffix(".xmp"))
        copy_file(file.with_suffix(".XMP"), out_name.with_suffix(".xmp"))


Path(args.out_dir).mkdir(exist_ok=True)
rename_files(Path(args.in_dir), Path(args.out_dir))
