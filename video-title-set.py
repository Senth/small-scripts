#!/usr/bin/python3
from pathlib import Path
from os import remove
from shutil import copy2
from subprocess import run
import re

# Get all mp4 files in the current directory
files = Path(".").glob("*.mp4")
tmp_file = "/tmp/metadata-title.tmp.mp4"

for file in files:
    title = re.sub(r"^.*s\d{2}e\d+ - ", "", str(file))
    title = title.replace(".mp4", "")
    print("Title: {}, file: {}".format(title, file))
    run(
        [
            "ffmpeg",
            "-i",
            str(file),
            "-c",
            "copy",
            "-metadata",
            "title={}".format(title),
            tmp_file,
        ]
    )

    if Path(tmp_file).exists():
        remove(str(file))
        copy2(tmp_file, str(file))
        remove(tmp_file)
