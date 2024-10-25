# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Image: Tag Info
#
# Resolutions are tagged by the nearest smallest "named" resolution.
#
# ## How to configure `imagemagick` for `wand` in `fish`
# ```fish
# set -gx MAGICK_HOME /opt/homebrew/opt/imagemagick
# fish_add_path {$MAGICK_HOME}/bin
#
# ## External Dependencies
#   * https://pypi.org/project/macos-tags/
#   * https://pypi.org/project/pillow/
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# MARK: Imports

import re
import sys
from operator import itemgetter
from os import environ, pathsep
from pathlib import Path

from macos_tags import Color, Tag
from macos_tags import add as add_tag
from macos_tags import get_all as get_all_tags
from macos_tags import remove as remove_tag
from PIL import Image

# MARK: Tags

GREEN, RED, YELLOW = itemgetter("GREEN", "RED", "YELLOW")(Color)

T_CORRUPT = Tag(name="Corrupt", color=RED)

ORIENTATION_TAGS = {
    Tag(name="Portrait", color=YELLOW): lambda ratio: ratio < 1,
    Tag(name="Square", color=YELLOW): lambda ratio: 1 == ratio,
    Tag(name="Landscape", color=YELLOW): lambda ratio: 1 < ratio,
}

IMAGE_SUFFIXES = [
    ".bmp",
    ".gif",
    ".jpeg",
    ".jpg",
    ".png",
    ".tiff",
    ".webp",
]

# MARK: Functions


def ratio(w: int, h: int) -> float:
    return w / h


# MARK: The Loop
args = sys.argv[1:]
for arg in args:

    path = Path(arg)

    # Skip if the path is not a file
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if not path.is_file():
        print(f"🛑 {path.name} 👉 Not a file")
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Skip if the path suffix is not a recognized image
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if not path.suffix.lower() in IMAGE_SUFFIXES:
        print(f"🛑 {path.name} 👉 Not an image")
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Remove any pre-existing tags (that look like they were set by this script)
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    for tag in get_all_tags(file=str(path)):
        if tag in [T_CORRUPT, *ORIENTATION_TAGS.keys()] or re.search(
            r"\d+x\d+", tag.name
        ):
            remove_tag(tag, file=str(path))
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Try to get the dimensinos or kkip and tag the path if the image is corrupt
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    try:
        with Image.open(path) as img:
            img.verify()
        # The image needs to be re-opened after the `verify` call
        with Image.open(path) as img:
            # Some corrupted image need to be manipulated to be detected
            img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            # Get the image resolution
            img_width, img_height = img.size
    except Exception as e:
        print(f"🚫 {path.name} 👉 Corrupt")
        print(e)
        add_tag(T_CORRUPT, file=str(path))
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Add the appropriate tags
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    img_ratio = ratio(img_width, img_height)

    # Set the orientation tags
    for tag, test in ORIENTATION_TAGS.items():
        if test(img_ratio):
            add_tag(tag, file=str(path))
            print(f"〘{tag.name}〛👉 {path.name} ({img_ratio})")
            break

    # Set the resolution tag
    res_tag = Tag(name=f"{img_width}x{img_height}", color=GREEN)
    add_tag(res_tag, file=str(path))
    print(f"〘{res_tag.name}〛👉 {path.name}")
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
