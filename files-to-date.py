#!/usr/bin/python3

import argparse
import re
from datetime import datetime
from pathlib import Path

from exif import Image

parser = argparse.ArgumentParser()
parser.add_argument("in_dir")
parser.add_argument("out_dir")
parser.add_argument("--keep-name", action="store_true")
args = parser.parse_args()

exif_regex = r"(\d{4}).(\d{2}).(\d{2}) (\d{2}).(\d{2}).(\d{2})"


def rename_exif(date: str) -> str:
    matches = re.match(exif_regex, date)
    if matches:
        year, month, day, hour, minute, second = matches.groups()
        return f"{year}-{month}-{day} {hour}.{minute}.{second}"

    return ""


def rename_files(in_dir: Path, out_dir: Path):
    for file in Path(in_dir).iterdir():
        if file.is_dir():
            print("Dir: {file}")
            next_out_dir = out_dir.joinpath(file.name)
            next_out_dir.mkdir(exist_ok=True)
            rename_files(file, next_out_dir)
            file.rmdir()
        else:
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

            if len(full_name) == 0:
                full_name = date.strftime("%Y-%m-%d %H.%M.%S")
            if args.keep_name:
                full_name += f" {file.name}"
            else:
                full_name += f"{file.suffix}"

            new_name = out_dir.joinpath(full_name)
            print(f"{file} -> {new_name}")
            file.rename(new_name)


rename_files(Path(args.in_dir), Path(args.out_dir))
