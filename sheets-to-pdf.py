#!/usr/bin/env python3

import os
import argparse
from os import path
from subprocess import call

parser = argparse.ArgumentParser()

parser.add_argument(
    "-d",
    "--dir",
    default=".",
    help="Where to (recursively) look for images and convert them into a single PDF.",
)

args = parser.parse_args()

IMAGE_TYPES = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]


def full_path(filename: str):
    return path.join(args.dir, filename)


def is_image(filename: str):
    for image_type in IMAGE_TYPES:
        if filename.lower().endswith(image_type):
            return True
    return False


def convert_to_pdf(images: list, out_file):
    command = ["convert"]
    command.extend(images)
    command.append(out_file)
    call(command)


for outer_dir in os.listdir(args.dir):
    # For all subdirectories, check if there are any images that needs to be converted
    if path.isdir(full_path(outer_dir)):
        images = []
        for file in os.listdir(full_path(outer_dir)):
            if is_image(file):
                relative_path = path.join(outer_dir, file)
                full_filepath = full_path(relative_path)
                images.append(full_filepath)

        if len(images) > 0:
            images.sort()
            out_file = full_path(outer_dir + ".pdf")
            convert_to_pdf(images, out_file)
