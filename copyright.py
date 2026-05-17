# **************************************************
# Copyright (c) 2026, Mayank Mishra
# **************************************************

import os
import re
import subprocess
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
    if comment_char:
        header = [f"{comment_char} {i}" for i in header]
    header = "\n".join(header)
    return header + "\n"


def _get_git_authors(file: str) -> list[str]:
    result = subprocess.run(
        ["git", "log", "--follow", "--numstat", "--format=%an", "--", file],
        capture_output=True,
        text=True,
    )
    contributions: dict[str, int] = {}
    current_author = None
    for line in result.stdout.splitlines():
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) == 3:
            try:
                contributions[current_author] = contributions.get(current_author, 0) + int(parts[0])
            except (ValueError, TypeError):
                pass
        else:
            current_author = line
    return [a for a, _ in sorted(contributions.items(), key=lambda x: (-x[1], x[0]))]


def _resolve_copyright_line(file: str) -> str:
    authors = _get_git_authors(file)
    if authors:
        return args.header.replace("__authors__", ", ".join(authors))
    return args.header.replace(", __authors__", "").replace("__authors__", "")


# Structural patterns — flexible on year and author content
_CPP_PATTERN = re.compile(r"// \*+\n// Copyright[^\n]*\n// \*+\n\n")
_PYTHON_PATTERN = re.compile(r"# \*+\n# Copyright[^\n]*\n# \*+\n\n")
_HTML_PATTERN = re.compile(r"<!-- \*+\n\s*Copyright[^\n]*\n\*+ -->\n\n")


def _build_cpp_header(file: str) -> str:
    return (
        "// **************************************************\n"
        f"{_make_header(_resolve_copyright_line(file), '//')}"
        "// **************************************************\n\n"
    )


def _build_python_header(file: str) -> str:
    return (
        "# **************************************************\n"
        f"{_make_header(_resolve_copyright_line(file), '#')}"
        "# **************************************************\n\n"
    )


def _build_html_header(file: str) -> str:
    return (
        "<!-- **************************************************\n"
        f"{_make_header(_resolve_copyright_line(file), '')}"
        "************************************************** -->\n\n"
    )


def _check_and_add_copyright_header(file: str, build_header_fn, pattern: re.Pattern) -> None:
    code = open(file, "r").read()

    if len(code) == 0:
        return

    header = build_header_fn(file)
    code_stripped = pattern.sub("", code)
    if code_stripped != code:
        code = f"{header}{code_stripped.lstrip(chr(10))}"
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
            _check_and_add_copyright_header(file, _build_cpp_header, _CPP_PATTERN)
        elif any([file.endswith(i) for i in _PYTHON_LIKE_EXTENSIONS]):
            _check_and_add_copyright_header(file, _build_python_header, _PYTHON_PATTERN)
        elif any([file.endswith(i) for i in _HTML_LIKE_EXTENSIONS]):
            _check_and_add_copyright_header(file, _build_html_header, _HTML_PATTERN)
