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
from pathlib import Path
from re import search as re_search
from sys import argv

from macos_tags import Color, Tag
from macos_tags import add as add_tag
from macos_tags import get_all as get_all_tags
from macos_tags import remove as remove_tag

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

MYLAR_FILES_TAGS = {
    Tag(name="Has series.json", color=GREEN): "series.json",
    Tag(name="Has cover.jpg", color=GREEN): "cover.jpg",
    Tag(name="Has cvinfo", color=GREEN): "cvinfo",
    Tag(name="Has folder.jpg", color=GREEN): "folder.jpg",
}

# Big problems (manual intervention required)
T_HAS_COMICS = Tag(name="Has comics", color=BLUE)
# Little problems (manually trigger Mylar to fix)

# Curiosities (no action required, but maybe take a look)
T_HAS_SERIES_TYPE_MISMATCH = Tag(name="Has series type mismatch", color=YELLOW)

# MARK: Functions


def get_series_type(p: Path) -> str:
    m = re_search(r"^\[(.+?)\]", p.name)
    return m.group(1) if m else ""


# MARK: The Loop
args = argv[1:]
for arg in args:

    print(f"Checking {arg}")

    P_series_dir = Path(arg)

    # Ensure a directory
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if not P_series_dir.is_dir():
        print("Not a directory")
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Remove existing tags
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    for tag in get_all_tags(file=str(P_series_dir)):
        if tag in [
            *MYLAR_FILES_TAGS.keys(),
            T_HAS_COMICS,
            T_HAS_SERIES_TYPE_MISMATCH,
        ]:
            remove_tag(tag, file=str(P_series_dir))
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Check for the presence of various files and series type mismatches
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    series_type = get_series_type(P_series_dir)
    with scandir(P_series_dir) as it:
        for entry in it:
            P_entry = Path(path_join(P_series_dir, entry.name))
            if not P_entry.is_file():
                continue
            for tag, filename in MYLAR_FILES_TAGS.items():
                if P_entry.name.lower() == filename:
                    add_tag(tag, file=str(P_series_dir))
                    break
            if P_entry.suffix.lower() in COMIC_FILE_SUFFIXES:
                if not T_HAS_COMICS in get_all_tags(str(P_series_dir)):
                    add_tag(T_HAS_COMICS, file=str(P_series_dir))
                if series_type != get_series_type(P_entry):
                    add_tag(T_HAS_SERIES_TYPE_MISMATCH, file=str(P_series_dir))
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
