import os
import sys
from pathlib import Path

from macos_tags import Color, Tag
from macos_tags import add as _add_tag
from macos_tags import remove as _remove_tag


def add_tag(tag, file):
    _add_tag(tag, file=str(file))


def remove_tag(tag, file):
    _remove_tag(tag, file=str(file))


T_no_sj = Tag(name="No series.json", color=Color.RED)
T_no_comic = Tag(name="No comic", color=Color.RED)

args = sys.argv[1:]

for arg in args:
    src = Path(arg)

    # Skip if not a directory
    if not src.is_dir():
        continue

    did_find_sj = False
    did_find_comic = False

    for fn in os.listdir(src):
        if fn == "series.json":
            did_find_sj = True
        if str.lower(fn.suffix) in [".cbz", ".cbr"]:
            did_find_comic = True
        if did_find_comic and did_find_sj:
            break

    if not did_find_sj:
        add_tag(T_no_sj, file=src)
    else:
        remove_tag(T_no_sj, file=src)

    if not did_find_comic:
        add_tag(T_no_comic, file=src)
    else:
        remove_tag(T_no_comic, file=src)
