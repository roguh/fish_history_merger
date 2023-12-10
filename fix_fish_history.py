#!/usr/bin/env python3
"""Fix or lint a fish_history file in various ways.

    Unparseable YAML and unsorted history is detected and fixed.
    The output should be a valid YAML file.
"""
import logging
import re
import sys
from typing import List, Tuple

import yaml

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("[%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

CMD_REGEX = re.compile("^- *cmd: *(.*)$")
# Assuming paths always start with 4 spaces
PATH_LIST_REGEX = re.compile("^    - *(.*)$")


def possibly_broken(line: str, line_num: int) -> bool:
    """Will the given string cause a YAML parse error?

    For example, this string contains two colon characters (:)
    - cmd: git commit -m 'unit test: add first'
    """
    try:
        yaml.safe_load(line)
        return False
    except (
        yaml.scanner.ScannerError,
        yaml.constructor.ConstructorError,
        yaml.parser.ParserError,
    ) as exc:
        logger.debug(
            "Fixing possibly bad yaml on line %s: %s\nError: %s", line_num, line, exc
        )
        return True


def fix_cmd_string(line: str) -> str:
    """This attempts to fix an unparseable fish_history cmd: line.

    This is done by converting it into a YAML folded block scalar, like this:
    - cmd: >
        cmd now goes on new line
    """
    match = re.match(CMD_REGEX, line)
    (string,) = match.groups() if match else ("(UNKNOWN)",)
    return f"- cmd: >\n    {string}\n"


def fix_path_string(line: str) -> str:
    """This attempts to fix an unparseable fish_history cmd: line.

    This is done by converting it into a YAML folded block scalar, like this:
    - cmd: x
      paths:
        - goodpath1
        - goodpath2
        - >
          bad path now goes on its own line, leading whitespace will be removed by yaml parser

    Assumes paths always start with 4 spaces
    """
    match = re.match(PATH_LIST_REGEX, line)
    (string,) = match.groups() if match else ("(UNKNOWN)",)
    return f"    - >\n      {string}\n"


def fix_unparseable_fish_history(history_str: str) -> Tuple[str, int]:
    """Attempt to fix unparseable yaml lines from a fish_history file."""
    lines = []
    fixed = 0
    history_lines = history_str.split('\n')
    for line_num, line in enumerate(history_lines):
        is_cmd = re.match(CMD_REGEX, line)
        is_path = re.match(PATH_LIST_REGEX, line)
        if is_cmd and possibly_broken(line, line_num):
            lines.append(fix_cmd_string(line))
            fixed += 1
        elif is_path and possibly_broken(line, line_num):
            lines.append(fix_path_string(line))
            fixed += 1
        else:
            lines.append(line)
    return "\n".join(lines), fixed


def sort_fish_history(history_str: str, count_differences=True) -> Tuple[str, int]:
    """Sorts the lines of history so that a valid fish_history file can be constructed.

    The history_lines must all be valid yaml first.

    History lines will be sorted oldest to newest by the 'when' key.
    """
    fixed = -1
    key = lambda obj: obj.get("when", 0)
    history_obj = yaml.safe_load(history_str)
    if not count_differences:
        history_obj.sort(key=key)
        sorted_history_obj = history_obj
    else:
        fixed = 0
        sorted_history_obj = list(sorted(history_obj, key=key))
        for obj1, obj2 in zip(history_obj, sorted_history_obj):
            if obj1 != obj2:
                fixed += 1
    return yaml.safe_dump(sorted_history_obj), fixed


def main():
    """Run this script with the given command line arguments."""
    # TODO OPTIONS:
    # lint vs fix
    # multiple files: lint all or fix all or just count fix Ns and do not fix
    # lint: just count the # of fixes and maybe line numbers
    # DEBUG logging
    # exclude a fix: nosort or nofixbad
    # fix config: nofixbad or erasepossiblybad
    filename = sys.argv[1]
    with open(filename, encoding="utf-8") as filehandle:
        fixed, fixed_count = fix_unparseable_fish_history(filehandle.read())
        print(fixed)
        logger.info("Fixed %s possibly unparseable yaml lines", fixed_count)


try:
    import pytest
except ImportError:
    pytest = None  # type: ignore

if pytest:

    @pytest.mark.parametrize(
        "history_str",
        [
            """
- cmd: ls
  when: 1621594050
- cmd: ls -lah ~/.ssh
  when: 1621594097
- cmd: ./update.sh
  when: 1621594083""",
            """
- cmd: ls -lah ~/.ssh
  when: 2
- cmd: ./update.sh
  when: 1""",
        ],
    )
    def test_unsorted_history(history_str: str):
        """Test linting and fixing an unsorted fish_history with no other errors."""
        # Each test case should have 2 elements that are out of place
        _, count = sort_fish_history(history_str)
        assert count == 2

    @pytest.mark.parametrize(
        "history_str",
        [
            """
- cmd: ls -lah ~/.ssh "um: bad"
- cmd: ./update.sh
  paths:
    - bad: bad: bad"""
        ],
    )
    def test_unparseable_history(history_str: str):
        """Test linting and fixing an unparseable fish_history with no other errors."""
        _, count = fix_unparseable_fish_history(history_str)
        assert count == 2

    @pytest.mark.parametrize(
        "history_str",
        [
            """
- cmd: ls -lah ~/.ssh "um: bad"
  when: 2
- cmd: ./update.sh
  when: 1
  paths:
    - bad: bad: bad
    - \\("""
        ],
    )
    def test_unsorted_and_unparseable_history(history_str: str):
        """Test linting and fixing an unparseable and unsorted fish_history with no other errors."""
        fixed, count = fix_unparseable_fish_history(history_str)
        assert count == 2
        _, count = sort_fish_history(fixed)
        assert count == 2


if __name__ == "__main__":
    main()
