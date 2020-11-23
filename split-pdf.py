#!/usr/bin/python3

import argparse
from PyPDF3 import PdfFileReader
import os
from os import path
from subprocess import call

parser = argparse.ArgumentParser()
parser.add_argument("input_pdf", help="input PDF")
parser.add_argument(
    "pages",
    nargs="*",
    help="Specify where the next part should start. E.g., specifying 4 would in a 10 page PDF create a two PDFs, one with pages 1-3 and the other 4-10.",
)
parser.add_argument(
    "-s", "--start", type=int, default=1, help="Specify which page to start splitting"
)
parser.add_argument(
    "-e",
    "--end",
    type=int,
    help="Specify the last page to use. Will use the last page as default",
)
parser.add_argument(
    "-p",
    "--prefix",
    help="Set a prefix for all files (will use the input file otherwise.",
)
args = parser.parse_args()

if not path.isfile(args.input_pdf):
    parser.error("Could not find input PDF")


def last_page_number():
    reader = PdfFileReader(open(args.input_pdf, "rb"))
    return reader.getNumPages()


def split_pdf(from_page, to_page, output_file):
    command = [
        "pdftk",
        args.input_pdf,
        "cat",
        "{}-{}".format(from_page, to_page),
        "output",
        output_file,
    ]
    call(command)


def create_output_filename(basename, file_number):
    return "{}-{}.pdf".format(basename, file_number)


# Iterate and split pages
from_page = args.start
file_number = 1
basename = args.input_pdf[:-4]
for page in args.pages:
    to_page = int(page) - 1
    output_file = create_output_filename(basename, file_number)
    split_pdf(from_page, to_page, output_file)
    from_page = page
    file_number += 1

# Create the last split (until the last page)
if args.end:
    to_page = args.end
else:
    to_page = last_page_number()
output_file = create_output_filename(basename, file_number)
split_pdf(from_page, to_page, output_file)
