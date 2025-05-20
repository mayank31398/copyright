# **************************************************
# Copyright (c) 2025, Mayank Mishra
# **************************************************

import os
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

_CPP_HEADER = (
    f"// **************************************************\n"
    f"// {args.header}\n"
    "// **************************************************\n\n"
)

_PYTHON_HEADER = (
    f"# **************************************************\n"
    f"# {args.header}\n"
    "# **************************************************\n\n"
)

_HTML_HEADER = (
    f"<!-- **************************************************\n"
    f"{args.header}\n"
    "************************************************** -->\n\n"
)


def _check_and_add_copyright_header(file: str, header: str) -> None:
    code = open(file, "r").read()

    if len(code) == 0:
        return

    if not code.startswith(header):
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
            _check_and_add_copyright_header(file, _CPP_HEADER)
        elif any([file.endswith(i) for i in _PYTHON_LIKE_EXTENSIONS]):
            _check_and_add_copyright_header(file, _PYTHON_HEADER)
        elif any([file.endswith(i) for i in _HTML_LIKE_EXTENSIONS]):
            _check_and_add_copyright_header(file, _HTML_HEADER)
