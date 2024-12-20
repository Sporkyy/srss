# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Mylar: Tag Series Folder
#
# - No comic (`*.cbz`` or `*.cbr``)
# - No `cover.jpg`
# - No `cvinfo`
# - No `folder.jpg`
# - No `series.json`
#
# ## External Dependencies
#   * https://pypi.org/project/macos-tags/
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# MARK: Imports

from operator import itemgetter
from os import PathLike, scandir
from os.path import join as path_join
from pathlib import Path, PurePath
from re import search as re_search
from sys import argv
from typing import Union

from macos_tags import Color, Tag
from macos_tags import add as add_tag_original
from macos_tags import get_all as get_all_tags_original
from macos_tags import remove as remove_tag_original

# MARK: Constants

COMIC_FILE_SUFFIXES = [".cbz", ".cbr"]

SERIES_TYPES = [
    "Digital",
    "GN",  # Graphic Novel
    "HC",  # Hard Cover
    "One-Shot",
    "Series",
    "TPB",  # Trade Paper Back
]

# MARK: Tags

BLUE, GREEN, YELLOW = itemgetter("BLUE", "GREEN", "YELLOW")(Color)

MYLAR_METADATA_FILES_TAGS = {
    Tag(name="Has series.json", color=GREEN): "series.json",
    Tag(name="Has cover.jpg", color=GREEN): "cover.jpg",
    Tag(name="Has cvinfo", color=GREEN): "cvinfo",
    Tag(name="Has folder.jpg", color=GREEN): "folder.jpg",
}

# Big problems (manual intervention required)
TAG_HAS_COMICS = Tag(name="Has comics", color=BLUE)
# Little problems (manually trigger Mylar to fix)

# Curiosities (no action required, but maybe take a look)
TAG_HAS_SERIES_TYPE_MISMATCH = Tag(name="Has series type mismatch", color=YELLOW)

# MARK: Functions


# Extend `add_tag` to accept `PathLike` objects
def add_tag(tag: Tag, file: Union[PathLike, str]) -> None:
    add_tag_original(tag, file=str(file))


def get_series_type(p: Path) -> str:
    m = re_search(r"^\[(.+?)\]", p.name)
    return m.group(1) if m else ""


def get_all_tags(file: Union[PathLike, str]) -> list[Tag]:
    return get_all_tags_original(file=str(file))


def remove_tag(tag: Tag, file: Union[PathLike, str]) -> None:
    remove_tag_original(tag, file=str(file))


def remove_tag_by_name(tag_name: str, file: Union[PathLike, str]) -> None:
    file = PurePath(file)
    for tag in get_all_tags(file=str(file)):
        if tag.name == tag_name:
            remove_tag(tag, file=str(file))
            break


def remove_tags_by_name(tag_names: list[str], file: Union[PathLike, str]) -> None:
    file = PurePath(file)
    if 1 == len(tag_names):
        remove_tag_by_name(tag_names[0], file=file)
        return
    for tag in get_all_tags(file=str(file)):
        if tag.name in tag_names:
            remove_tag(tag, file=str(file))


# MARK: The Loop
args = argv[1:]
for arg in args:

    print(f"Checking {arg}")

    series_path = Path(arg)

    # Ensure a directory
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if not series_path.is_dir():
        print("Not a directory")
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Remove existing tags
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    remove_tags_by_name(
        [
            *[tag.name for tag in MYLAR_METADATA_FILES_TAGS.keys()],
            TAG_HAS_COMICS.name,
            TAG_HAS_SERIES_TYPE_MISMATCH.name,
        ],
        file=series_path,
    )

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Check for the presence of various files and series type mismatches
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    series_type = get_series_type(series_path)
    with scandir(series_path) as it:
        for entry in it:
            P_entry = Path(path_join(series_path, entry.name))
            if not P_entry.is_file():
                continue
            for tag, filename in MYLAR_METADATA_FILES_TAGS.items():
                if P_entry.name.lower() == filename:
                    add_tag(tag, file=str(series_path))
                    break
            if P_entry.suffix.lower() in COMIC_FILE_SUFFIXES:
                if not TAG_HAS_COMICS in get_all_tags(str(series_path)):
                    add_tag(TAG_HAS_COMICS, file=str(series_path))
                if series_type != get_series_type(P_entry):
                    add_tag(TAG_HAS_SERIES_TYPE_MISMATCH, file=str(series_path))
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
