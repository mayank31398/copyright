# **************************************************
# Copyright (c) 2025, Mayank Mishra
# **************************************************

import os
import re
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--repo", type=str, required=True)
parser.add_argument("--exclude", type=str, required=False)
parser.add_argument("--header", type=str, required=True)
args = parser.parse_args()


_CPP_LIKE_EXTENSIONS = [".cu", ".h", ".c", ".cpp"]
_PYTHON_LIKE_EXTENSIONS = [
    ".py",
    ".yml",
    ".yaml",
    ".clang-format",
    "requirements-dev.txt",
    "requirements.txt",
    "setup.cfg",
    "Makefile",
]
_HTML_LIKE_EXTENSIONS = [".html", ".md"]

_BANNED = [".git"]
if args.exclude:
    exclude = open(args.exclude, "r").readlines()
    exclude = [i.strip() for i in exclude]
    _BANNED.extend(exclude)

_BANNED = [os.path.realpath(i) for i in _BANNED]


def _make_header(header: str, comment_char: str) -> str:
    header = header.split("\n")
    header = [f"{comment_char} {i}" for i in header]
    header = "\n".join(header)
    return header + "\n"


def _make_pattern(header: str) -> re.Pattern:
    pattern = re.escape(header)
    pattern = re.sub(r"\d{4}", r"\\d{4}", pattern)
    return re.compile(pattern)


_CPP_HEADER = (
    "// **************************************************\n"
    f"{_make_header(args.header, "//")}"
    "// **************************************************\n\n"
)

_PYTHON_HEADER = (
    "# **************************************************\n"
    f"{_make_header(args.header, "#")}"
    "# **************************************************\n\n"
)

_HTML_HEADER = (
    "<!-- **************************************************\n"
    f"{_make_header(args.header, "")}"
    "************************************************** -->\n\n"
)

_CPP_PATTERN = _make_pattern(_CPP_HEADER)
_PYTHON_PATTERN = _make_pattern(_PYTHON_HEADER)
_HTML_PATTERN = _make_pattern(_HTML_HEADER)


def _check_and_add_copyright_header(file: str, header: str, pattern: re.Pattern) -> None:
    code = open(file, "r").read()

    if len(code) == 0:
        return

    if pattern.match(code):
        code = pattern.sub(header, code, count=1)
    elif not code.startswith(header):
        code = f"{header}{code}"

    open(file, "w").writelines([code])


def _is_banned(path: str) -> bool:
    assert not path.endswith("/")

    for banned_directory in _BANNED:
        if path.startswith(banned_directory):
            return True

    return False


directory = os.path.realpath(args.repo)

for root, dirs, files in os.walk(directory):
    if _is_banned(root):
        continue

    for file in files:
        file = os.path.join(root, file)

        if _is_banned(file):
            continue

        if any([file.endswith(i) for i in _CPP_LIKE_EXTENSIONS]):
            _check_and_add_copyright_header(file, _CPP_HEADER, _CPP_PATTERN)
        elif any([file.endswith(i) for i in _PYTHON_LIKE_EXTENSIONS]):
            _check_and_add_copyright_header(file, _PYTHON_HEADER, _PYTHON_PATTERN)
        elif any([file.endswith(i) for i in _HTML_LIKE_EXTENSIONS]):
            _check_and_add_copyright_header(file, _HTML_HEADER, _HTML_PATTERN)
