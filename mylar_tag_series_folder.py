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
import sys

# MARK: Imports
from os.path import join as path_join
from pathlib import Path

from macos_tags import Color, Tag
from macos_tags import add as add_tag
from macos_tags import remove as remove_tag

# MARK: Tags
T_no_sj = Tag(name="No series.json", color=Color.ORANGE)
T_no_comics = Tag(name="No comics", color=Color.RED)

args = sys.argv[1:]

# MARK: The Loop
for arg in args:

    print(f"Checking {arg}")

    P_arg = Path(arg)

    # Skip if not a directory
    if not P_arg.is_dir():
        print("Not a directory")
        continue

    did_find_sj = False
    did_find_comic = False

    for fn in os.listdir(P_arg):
        P_fn = Path(path_join(arg, fn))
        print(f"Checking {P_fn}")
        if not P_fn.is_file():
            print("Not a file")
            continue
        if "series.json" == P_fn.name.lower():
            print("Found series.json")
            did_find_sj = True
        if P_fn.suffix.lower() in [".cbz", ".cbr"]:
            print("Found comic")
            did_find_comic = True
        if did_find_comic and did_find_sj:
            print("Breaking; Found a comic and a series.json")
            break

    if not did_find_sj:
        print("Adding tag for no series.json")
        add_tag(T_no_sj, file=arg)
    else:
        print("Removing tag for no series.json")
        remove_tag(T_no_sj, file=arg)

    if not did_find_comic:
        print("Adding tag for no comics")
        add_tag(T_no_comics, file=arg)
    else:
        print("Removing tag for no comics")
        remove_tag(T_no_comics, file=arg)
