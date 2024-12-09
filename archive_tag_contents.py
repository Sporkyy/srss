# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Archive: Tag Contents
#
# Notes:
#   * patool cannot list the contents of an archive in a way that can be captured and
#     put into a variable. That is by design because it would be difficult.
#
# External Dependencies
#   * https://pypi.org/project/macos-tags/
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# MARK: Imports

from operator import itemgetter
from os import PathLike
from pathlib import Path, PurePath
from re import Pattern as re_Pattern
from re import compile as re_compile
from re import search as re_search
from sys import argv
from typing import Sequence, Union
from zipfile import ZipFile

from macos_tags import Color, Tag
from macos_tags import add as original_add_tag
from macos_tags import get_all as original_get_all_tags
from macos_tags import remove as original_remove_tag

# MARK: Constants
ARCHIVE_SUFFIXES = [
    ".cbz",
    ".zip",
]

BLUE = itemgetter("BLUE")(Color)

# MARK: Functions


# Same as the macos_tags.add function but with the file parameter can also be
# a PathLike object
def add_tag(tag: Tag, file: Union[str, PathLike]) -> None:
    original_add_tag(tag, file=str(file))


# Same as the macos_tags.remove function but with the file parameter can also be
# a PathLike object
def remove_tag(tag: Tag, file: Union[str, PathLike]) -> None:
    original_remove_tag(file=str(file), tag=tag)


# Same as the macos_tags.get_all_tags function but with the file parameter can also be
# a PathLike object
def get_all_tags(file: Union[str, PathLike]) -> list[Tag]:
    return original_get_all_tags(file=str(file))


def is_hidden(path: Union[str, PathLike]) -> bool:
    return PurePath(path).stem.startswith(".")


def remove_tag_by_name(
    target_tag: Union[re_Pattern, str], file: Union[str, PathLike]
) -> None:
    # print(target_tag)
    for tag in get_all_tags(file=file):
        # print(tag.name)
        if isinstance(target_tag, re_Pattern):
            # print("re_Pattern")
            results = re_search(target_tag, tag.name)
            if results:
                remove_tag(tag, file=file)
                continue
        elif tag.name == target_tag:
            remove_tag(tag, file=file)
            break


def cnt_by_suffix(paths: Sequence[Union[str, PathLike]]) -> dict[str, int]:
    sfx_cnt = {}
    for path in paths:
        pp = PurePath(path)
        if is_hidden(pp):
            continue
        suffix = pp.suffix.lower()
        sfx_cnt[suffix] = sfx_cnt.get(suffix, 0) + 1
    return sfx_cnt


# MARK: The Loop
args = argv[1:]
for arg in args:
    arg_path = Path(arg)

    # Skip if not a file
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if not arg_path.is_file():
        print(f"🛑 {arg_path.name} 👉 Not a file")
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Skip if not an archive
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if not arg_path.suffix.lower() in ARCHIVE_SUFFIXES:
        print(f"🛑 {arg_path.name} 👉 Unrecognized suffix ({arg_path.suffix})")
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Remove existing tags
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    remove_tag_by_name(re_compile(r"^\.\w+\s\(\d+\)$"), file=arg_path)
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # List the contents of the archive
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    z = ZipFile(arg_path)
    contents = z.namelist()
    cnts = cnt_by_suffix(contents)
    # print(cnts)
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Add tags for the contents
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    for suffix, count in cnts.items():
        if count > 1:
            tag = Tag(name=f"{suffix} ({count})", color=BLUE)
            add_tag(tag, file=arg_path)
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
