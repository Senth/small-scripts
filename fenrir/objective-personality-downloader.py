#!/usr/bin/python3
import argparse
import re
from datetime import datetime
from os import makedirs
from pathlib import Path
from shutil import move
from subprocess import run
from typing import Set

import chromedriver_autoinstaller

input_dir = Path("/mnt/lvm/temp/objective_personality")

tmp_dir = Path("/tmp")


def main() -> None:
    # Install chromedriver if necessary
    chromedriver_autoinstaller.install()

    print(f"Next episode number: {get_next_episode_number()}")

    pass


def get_next_episode_number() -> int:
    season = datetime.now().year
    regexp = re.compile(rf"OP QA - s{season}e(\d+) - .*\.mp4")
    seasonDir = plex_dir / f"Season {season}"

    latest_episode = 0
    for file in seasonDir.glob("*.mp4"):
        match = regexp.match(file.name)
        if match:
            latest_episode = max(latest_episode, int(match.group(1)))

    return latest_episode + 1


# def log(message):
#     if args.verbose:
#         print(message)


# shows: Set[str] = {
#     "OP Class",
#     "OP QA",
# }


# new_files = {}

# Create metadata title for files
# for show in shows:
#     new_files[show] = []
#     for filepath in input_dir.glob(show + " - *.mp4"):
#         basename = Path(filepath).name
#         new_files[show].append(basename)

#         # Get title from file format
#         title = re.sub(r"^.*s\d+e\d+ - ", "", basename)
#         # Remove part name and extension
#         title = re.sub(r"(?: - pt\d|).mp4", "", title)

#         # File locations
#         file_input = input_dir.joinpath(filepath)
#         temp_file_output = tmp_dir.joinpath(basename)

#         log(f"Found file: {basename} ————> Title: {title}")

#         # Metadata ffmpeg conversion
#         if not args.pretend:
#             log("ffmpeg metadata title conversion")
#             completed_process = (
#                 run(
#                     [
#                         "ffmpeg",
#                         "-i",
#                         str(file_input),
#                         "-c",
#                         "copy",
#                         "-metadata",
#                         f"title={title}",
#                         temp_file_output,
#                     ]
#                 ).returncode
#                 == 0
#             )

#             # Remove original file
#             if completed_process:
#                 log("Removing original file")
#                 file_input.unlink()

# log("")

# # Move files to Plex location
# for show in shows:
#     for filepath in new_files[show]:
#         # Get season
#         match = re.search(r"s(\d+)e\d+", filepath)
#         if match:
#             season_number = match.group(1)
#             temp_file = tmp_dir.joinpath(filepath)
#             out_dir = plex_dir.joinpath(show, f"Season {season_number}")

#             # Create out dirs if they don't exist
#             makedirs(out_dir, exist_ok=True)

#             out_file = out_dir.joinpath(filepath)

#             log(f"Move {temp_file} ————> {out_file}")

#             if not args.pretend:
#                 move(str(temp_file), str(out_file))
#         else:
#             print(f"Could not find season in file {filepath}")


if __name__ == "__main__":
    main()
