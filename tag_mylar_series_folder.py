# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Tag Mylar Series Folder
#
# ## External Dependencies
#   * https://pypi.org/project/macos-tags/
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# MARK: Imports
import os
import sys
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

    P_arg = Path(arg)

    # Skip if not a directory
    if not P_arg.is_dir():
        continue

    did_find_sj = False
    did_find_comic = False

    for fn in os.listdir(P_arg):
        P_fn = Path(fn)
        if not P_fn.is_file():
            continue
        if "series.json" == P_fn.name.lower():
            did_find_sj = True
        if P_fn.suffix.lower() in [".cbz", ".cbr"]:
            did_find_comic = True
        if did_find_comic and did_find_sj:
            break

    if not did_find_sj:
        add_tag(T_no_sj, file=arg)
    else:
        remove_tag(T_no_sj, file=arg)

    if not did_find_comic:
        add_tag(T_no_comics, file=arg)
    else:
        remove_tag(T_no_comics, file=arg)
