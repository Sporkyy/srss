import os
import sys
from pathlib import Path

from macos_tags import Color, Tag
from macos_tags import add as add_tag
from macos_tags import remove as remove_tag

args = sys.argv[1:]

tag_has_series_json = Tag(name="Green", color=Color.GREEN)
tag_missing_series_json = Tag(name="Red", color=Color.RED)

for arg in args:
    src = Path(arg)

    # Skip if not a directory
    if not src.is_dir():
        continue

    if "series.json" in os.listdir(src):
        remove_tag(tag_missing_series_json, file=str(src))
        add_tag(tag_has_series_json, file=str(src))
    else:
        remove_tag(tag_has_series_json, file=str(src))
        add_tag(tag_missing_series_json, file=str(src))
