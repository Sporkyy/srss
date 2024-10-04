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

import os
import re
import sys
from operator import itemgetter
from os import PathLike

# MARK: Imports
from os.path import join as path_join
from pathlib import Path

from macos_tags import Color, Tag
from macos_tags import add as add_tag
from macos_tags import remove as remove_tag

# MARK: Constants

ORANGE, RED, YELLOW = itemgetter("ORANGE", "RED", "YELLOW")(Color)

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

# Big problems (manual intervention required)
T_MISSING_COMICS = Tag(name="Missing comics", color=RED)
# Little problems (manually trigger Mylar to fix)
T_MISSING_SERIES_JSON = Tag(name="Missing series.json", color=ORANGE)
T_MISSING_COVER_IMAGE = Tag(name="Missing cover.jpg", color=ORANGE)
T_MISSING_CVINFO = Tag(name="Missing cvinfo", color=ORANGE)
T_MISSING_FOLDER_IMAGE = Tag(name="Missing folder.jpg", color=ORANGE)
# Curiosities (no action required, but maybe take a look)
T_HAS_UNIDENTIFIED_FILES = Tag(name="Has unidentified files", color=YELLOW)
T_HAS_SERIES_TYPE_MISMATCH = Tag(name="Has series type mismatch", color=YELLOW)

# MARK: Functions


def get_series_type(p: Path) -> str:
    m = re.search(r"\[(.+?)\]", p.name)
    return m.group(1) if m else ""


def is_comic(p: Path) -> bool:
    return p.suffix.lower() in COMIC_FILE_SUFFIXES


# def has_no_comics

# MARK: The Loop
for arg in sys.argv[1:]:

    print(f"Checking {arg}")

    path_series = Path(arg)

    # Skip if not a directory
    if not path_series.is_dir():
        print("Not a directory")
        continue

    cnt_total_files = 0
    cnt_identified_files = 0
    did_find_series_json = False
    did_find_cover_image = False
    did_find_cvinfo = False
    did_find_folder_image = False
    did_find_a_comic = False
    is_series_type_mismatch = False
    series_type = get_series_type(path_series)

    # MARK: Scan Directory

    with os.scandir(path_series) as it:
        for series_child in it:
            path_series_child = Path(path_join(path_series, series_child.name))
            cnt_total_files += 1
            path_child_type = get_series_type(path_series_child)
            if not series_child.is_file():
                continue
            if "series.json" == series_child.name.lower():
                did_find_series_json = True
                cnt_identified_files += 1
            if "cover.jpg" == series_child.name.lower():
                did_find_cover_image = True
                cnt_identified_files += 1
            if "cvinfo" == series_child.name.lower():
                did_find_cvinfo = True
                cnt_identified_files += 1
            if "folder.jpg" == series_child.name.lower():
                did_find_folder_image = True
                cnt_identified_files += 1
            for suffix in COMIC_FILE_SUFFIXES:
                if series_child.name.lower().endswith(suffix):
                    did_find_a_comic = True
                    cnt_identified_files += 1
            if series_type == path_child_type:
                is_series_type_mismatch = True

    # MARK: Add/Remove Tags

    if cnt_identified_files != cnt_total_files:
        add_tag(T_HAS_UNIDENTIFIED_FILES, file=str(path_series))

    if not did_find_series_json:
        add_tag(T_MISSING_SERIES_JSON, file=str(path_series))
    else:
        remove_tag(T_MISSING_SERIES_JSON, file=str(path_series))

    if not did_find_a_comic:
        add_tag(T_MISSING_COMICS, file=str(path_series))
    else:
        remove_tag(T_MISSING_COMICS, file=str(path_series))

    if not did_find_cover_image:
        add_tag(T_MISSING_COVER_IMAGE, file=str(path_series))
    else:
        remove_tag(T_MISSING_COVER_IMAGE, file=str(path_series))

    if not did_find_cvinfo:
        add_tag(T_MISSING_CVINFO, file=str(path_series))
    else:
        remove_tag(T_MISSING_CVINFO, file=str(path_series))

    if not did_find_folder_image:
        add_tag(T_MISSING_FOLDER_IMAGE, file=str(path_series))
    else:
        remove_tag(T_MISSING_FOLDER_IMAGE, file=str(path_series))
