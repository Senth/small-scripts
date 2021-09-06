#!/usr/bin/python

import argparse
from pathlib import Path
from subprocess import run

parser = argparse.ArgumentParser(description="Splits videos into smaller chunks")
parser.add_argument("input", help="Video to split")
parser.add_argument(
    "-t",
    "--time",
    type=int,
    default=600,
    help="Seconds to split the video into",
)

args = parser.parse_args()

# Check if file exists
input_path = Path(args.input)
if not input_path.exists():
    print("Input video file does not exist.")
    exit(1)

output_dir = input_path.parent
part = 1
reached_end_of_video = False

while not reached_end_of_video:
    start_time = (part - 1) * args.time
    output_filename = f"{input_path.stem}-part{part}{input_path.suffix}"
    output_path = output_dir.joinpath(output_filename)
    command = [
        "ffmpeg",
        "-i",
        input_path,
        "-ss",
        str(start_time),
        "-t",
        str(args.time),
        "-c",
        "copy",
        output_path,
    ]

    run(command)

    if output_path.stat().st_size < 500:
        reached_end_of_video = True
        output_path.unlink()

    part += 1

print("Done!")
