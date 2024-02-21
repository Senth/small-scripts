#!/usr/bin/python3
# A "Facade" in front of make for some additional features
from __future__ import annotations

import re
import subprocess
import sys
import os
from typing import List, Optional

from colored import fg
from tealprint import TealPrint


def main() -> None:
    create_extras()
    if is_empty_command():
        run_make(sys.argv)
        return
    extra = ExtraFunctionality.get_extra(sys.argv)
    if extra:
        extra.run(sys.argv)
    if not extra or extra.run_default:
        run_make(sys.argv)

def prepare(_: List[str]) -> None:
    """Prepare the build environment"""
    
    # Set correct JAVA_HOME for dataflow
    os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-11-openjdk-amd64"

def run_make(cmd: List[str], capture_output=False) -> str:
    prepare(cmd)

    # Get platform dependent path/binary
    cmd[0] = "/usr/bin/make"
    result = subprocess.run(cmd, capture_output=capture_output)
    if result:
        if capture_output:
            return str(result.stdout)
        elif result.returncode != 0:
            sys.exit(result.returncode)
    return ""


def is_empty_command() -> bool:
    return len(sys.argv) <= 1


def create_extras() -> None:
    ListTargets()
    RunIfExists()


class ExtraFunctionality:
    extras: List[ExtraFunctionality] = []

    def __init__(self, command: List[str], run_default: bool) -> None:
        self.command = command
        self.run_default = run_default
        ExtraFunctionality.extras.append(self)

    def should_run(self, cmd: List[str]) -> bool:
        if len(cmd) - 1 < len(self.command):
            return False

        for i in range(len(self.command)):
            if cmd[i + 1] != self.command[i]:
                return False

        return True

    def run(self, cmd: List[str]) -> None:
        pass

    @staticmethod
    def get_extra(cmd: List[str]) -> Optional[ExtraFunctionality]:
        for extra in ExtraFunctionality.extras:
            if extra.should_run(cmd):
                return extra


class ListTargets(ExtraFunctionality):
    def __init__(self) -> None:
        super().__init__(["list"], False)

    def run(self, cmd: List[str]) -> None:
        targets = get_make_targets()
        for target in targets:
            print(target)


class RunIfExists(ExtraFunctionality):
    def __init__(self) -> None:
        super().__init__(["--if-exists"], False)

    def run(self, cmd: List[str]) -> None:
        new_cmd = cmd[:1]
        targets = get_make_targets()
        for i in range(2, len(cmd)):
            target = cmd[i]
            if target in targets:
                new_cmd.append(target)
            else:
                TealPrint.info(f"Skipping missing target {target}", color=fg("yellow"))

        run_make(new_cmd)


target_re = re.compile(r"^\s*([^\s:]+)\s*:")


def get_make_targets() -> List[str]:
    targets = []
    with open("Makefile", "r") as f:
        for line in f.readlines():
            match = target_re.match(line)
            if match:
                targets.append(match.group(1))

    return targets


try:
    main()
except KeyboardInterrupt:
    sys.exit(1)
