#!/usr/bin/python3
from pathlib import Path
from shutil import move
from subprocess import run
import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--pretend", action="store_true")
parser.add_argument("-v", "--verbose", action="store_true")
args = parser.parse_args()

input_dir = Path("/mnt/lvm/temp/objective_personality")
plex_dir = Path("/mnt/lvm/personal_development/Objective Personality")
tmp_dir = Path("/mnt/lvm/temp")


def log(message):
    if args.verbose:
        print(message)


shows = {
    "OP Class": [],
    "OP QA": [],
}

new_files = {}

# Create metadata title for files
for show in shows:
    new_files[show] = []
    for filepath in input_dir.glob(show + " - *.mp4"):
        basename = Path(filepath).name
        new_files[show].append(basename)

        # Get title from file format
        title = re.sub(r"^.*s\d{2}e\d+ - ", "", basename)
        # Remove part name and extension
        title = re.sub(r"(?: - pt\d|).mp4", "", title)

        # File locations
        file_input = input_dir.joinpath(filepath)
        temp_file_output = tmp_dir.joinpath(basename)

        log("Found file: {} ————> Title: {}".format(basename, title))

        # Metadata ffmpeg conversion
        if not args.pretend:
            log("ffmpeg metadata title conversion")
            completed_process = (
                run(
                    [
                        "ffmpeg",
                        "-i",
                        str(file_input),
                        "-c",
                        "copy",
                        "-metadata",
                        "title={}".format(title),
                        temp_file_output,
                    ]
                ).returncode
                == 0
            )

            # Remove original file
            if completed_process:
                log("Removing original file")
                file_input.unlink()

log("")

# Move files to Plex location
for show in shows:
    for filepath in new_files[show]:
        temp_file = tmp_dir.joinpath(filepath)
        out_file = plex_dir.joinpath(show, "Season 01", filepath)

        log("Move {} ————> {}".format(temp_file, out_file))

        if not args.pretend:
            move(str(temp_file), str(out_file))
