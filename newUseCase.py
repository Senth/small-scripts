#!/usr/bin/python3

import os
import argparse

script_location = os.path.abspath(__file__)
script_dir = os.path.dirname(script_location)
asset_dir = os.path.join(script_dir, 'assets/newUseCase')
current_dir = os.path.abspath(os.getcwd())

files_to_copy = [
    '$NAME$Input.ts',
    '$NAME$Output.ts',
    '$NAME$Repository.ts',
    '$NAME$Interactor.ts',
    '$NAME$Interactor.test.ts',
    'README.md'
]

parser = argparse.ArgumentParser()
parser.add_argument(
    'names', nargs='*', help='Name of the use cases to create files for. Example: transaction-create')
parser.add_argument('-s', '--skip-parent-name', action='store_true',
                    help=" Don't append the parent folder (if it exists) to the class names")

args = parser.parse_args()


def find_core_relative_path():
    name_prefix = ''
    parent_dir = current_dir
    parent_count = 1
    found = False

    while not found:
        core_test_dir = os.path.join(parent_dir, 'core')
        if os.path.exists(core_test_dir):
            found = True
        elif len(parent_dir) <= 3:
            raise RuntimeError("Couldn't find 'core' directory")
        else:
            # If we go up one directory structure, remember the directory name so
            # we can append it to the file names later
            if not args.skip_parent_name:
                name_prefix = os.path.basename(parent_dir) + '-' + name_prefix
            parent_dir = os.path.dirname(parent_dir)
            parent_count += 1
            print("Trying with parent dir: " + parent_dir)

    path = ''
    for i in range(parent_count):
        path += '../'
    path += 'core'

    return path, name_prefix


def create_out_dir(name):
    try:
        os.mkdir(name)
    except FileExistsError:
        pass


def copy_files(out_dir, core_dir, name_camel_case):
    for filename in files_to_copy:
        in_file = os.path.join(asset_dir, filename)
        out_filename = filename.replace('$NAME$', name_camel_case)
        out_file = os.path.join(out_dir, out_filename)

        # Skip if output file already exists (we don't want to overwrite it)
        if os.path.exists(out_file):
            continue

        with open(in_file, 'r') as file:
            file_data = file.read()

        file_data = file_data.replace('$NAME$', name_camel_case)
        file_data = file_data.replace('$CORE$', core_dir)

        with open(out_file, 'w') as file:
            file.write(file_data)


def convert_to_camel_case(name):
    words = name.split('-')

    camel_case = ''

    for word in words:
        if len(word) > 0:
            camel_case += word.capitalize()

    return camel_case


for name in args.names:
    out_dir = os.path.join(current_dir, name)
    core_dir, name_prefix = find_core_relative_path()
    name_camel_case = convert_to_camel_case(name_prefix + name)
    create_out_dir(out_dir)
    copy_files(out_dir, core_dir, name_camel_case)
