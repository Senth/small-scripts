#!/usr/bin/python3
import argparse
import re
from os import path
from pathlib import Path
from subprocess import run

VIDEO_EXTENSIONS = ["mp4", "mkv", "webm", "mpeg", "mpg"]

parser = argparse.ArgumentParser()
parser.add_argument("files", help="Files or directories you want to convert")
parser.add_argument(
    "-r",
    "--recursive",
    action="store_true",
    help="Recursively convert files in directories",
)
parser.add_argument(
    "-i", "--include", help="If defined, only convert files matching this regex pattern"
)
parser.add_argument(
    "-o",
    "--output-dir",
    help="Where to output all files, by default outputs the same location as the input file",
)
parser.add_argument(
    "-v", "--verbose", action="store_true", help="Print what is happening"
)
parser.add_argument(
    "-p",
    "--pretend",
    action="store_true",
    help="Don't do any conversion, useful with --verbose.",
)
args = parser.parse_args()


def log_message(message: str):
    if args.verbose:
        print(message)


def convert_dir(dirpath: Path):
    # List all files in the directory
    for filepath in dirpath.glob("*"):
        if filepath.is_dir() and args.recursive:
            convert_dir(filepath)
        elif filepath.is_file():
            convert_file(filepath)


def file_matches_include(filepath: Path):
    matches = re.findall(args.include, filepath.name)
    return len(matches) > 0


def is_video_file(filepath: Path):
    for extension in VIDEO_EXTENSIONS:
        if filepath.name.lower().endswith(extension):
            return True
    return False


def get_metadata(filepath: Path):
    metadata = ""

    # Title
    metadata += "title="
    metadata += filepath.name.split("-")[0]

    return metadata


def convert_file(filepath: Path):
    outfile_name = path.splitext(filepath.name)[0] + ".mp3"

    # Use args.outputdir
    if args.output_dir:
        outdir = args.output_dir
        # Create dir if it doesn't exist
        if not Path(outdir).exists() and not args.pretend:
            Path(outdir).mkdir(parents=True, exist_ok=True)

    # No default output dir has been set, use the file's parent dir
    else:
        outdir = filepath.parent.as_posix()

    metadata = get_metadata(filepath)
    outfile = path.join(outdir, outfile_name)
    command = [
        "ffmpeg",
        "-i",
        filepath,
        "-metadata",
        metadata,
        "-threads",
        "4",
        "-acodec",
        "libmp3lame",
        "-ac",
        "2",
        "-ab",
        "256k",
        "-vn",
        "-y",
        outfile,
    ]

    log_message("Converting ||| {} -----> {}".format(filepath.as_posix(), outfile))

    if not args.pretend:
        run(command)


def convert_file_or_dir(file):
    filepath = Path(file)
    if not filepath.exists():
        log_message("File not found: " + file)
    if filepath.is_dir():
        convert_dir(filepath)
    elif filepath.is_file():
        # Only convert matching video files
        if is_video_file(filepath) and (
            not args.include or file_matches_include(filepath)
        ):
            convert_file(filepath)


# --- MAIN ---
for file in args.files:
    convert_file_or_dir(file)
