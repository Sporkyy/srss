import os
import sys
from pathlib import Path, PurePath

from macos_tags import Color, Tag
from macos_tags import add as add_tag
from macos_tags import remove as remove_tag

# MARK: Tags
T_no_sj = Tag(name="No series.json", color=Color.RED)
T_no_comic = Tag(name="No comic", color=Color.RED)

args = sys.argv[1:]

# MARK: The Loop
for arg in args:
    src = Path(arg)

    # Skip if not a directory
    if not src.is_dir():
        continue

    did_find_sj = False
    did_find_comic = False

    for fn in os.listdir(src):
        fn = PurePath(fn)
        if "series.json" == fn.name.lower():
            did_find_sj = True
        if fn.suffix.lower() in [".cbz", ".cbr"]:
            did_find_comic = True
        if did_find_comic and did_find_sj:
            break

    if not did_find_sj:
        add_tag(T_no_sj, file=str(src))
    else:
        remove_tag(T_no_sj, file=str(src))

    if not did_find_comic:
        add_tag(T_no_comic, file=str(src))
    else:
        remove_tag(T_no_comic, file=str(src))
