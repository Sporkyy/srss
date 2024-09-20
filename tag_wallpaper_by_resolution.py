# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Tag Wallpaper by Resolution
#
# Resolutions are tagged by the nearest smallest "named" resolution.
#
# ## Orientation Tags
#   * Portrait
#   * Landscape
#   * Square
#
# ## Resoltuion Tags
#   * 8K (7680x4320)
#   * 6K (6144x3456),
#   * 5K (5120x2880),
#   * 4K (3840x2160),
#   * 1080p (1920x1080),
#   * Tiny (0x0),
#
# ## External Dependencies
#   * https://pypi.org/project/macos-tags/
#   * https://pypi.org/project/pillow/
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

import sys

# MARK: Imports
from ast import List
from os import remove
from pathlib import Path
from re import T

from macos_tags import Color, Tag
from macos_tags import add as add_tag
from macos_tags import get_all as get_all_tags
from macos_tags import remove as remove_tag
from PIL import Image

res_tags = {
    # For tagging purposes the `(width, height)` tuple is the minimum resolution
    Tag(name="8K", color=Color.BLUE): (7680, 4320),
    Tag(name="6K", color=Color.BLUE): (6144, 3456),
    Tag(name="5K", color=Color.GREEN): (5120, 2880),
    Tag(name="4K", color=Color.GREEN): (3840, 2160),
    Tag(name="1080p", color=Color.YELLOW): (1920, 1080),
    Tag(name="Tiny", color=Color.RED): (0, 0),
}

T_portrait = Tag(name="Portrait", color=Color.PURPLE)

T_landscape = Tag(name="Landscape", color=Color.PURPLE)

T_square = Tag(name="Square", color=Color.PURPLE)


# MARK: Functions


# Shortcuts does this already when running the script in "production"
# (Assuming the Input is configured properly for Quick Actions)
# But doing it here helps when running it in "development"
def is_image(file: Path) -> bool:
    if not file.is_file():
        return False
    fn_suffix = file.suffix.lower()
    image_suffixes = [".bmp", ".gif", ".jpeg", ".jpg", ".png", ".tiff"]
    return fn_suffix in image_suffixes


# This should work since `dict`s have a guaranteed order in Python 3.7+
def get_tags_by_dimensions(width: int, height: int) -> list:
    tags = []
    if width < height:
        tags.append(T_portrait)
    elif height < width:
        tags.append(T_landscape)
    else:
        tags.append(T_square)
    for tag, (min_width, min_height) in res_tags.items():
        if min_width <= width and min_height <= height:
            tags.append(tag)
    return tags


args = sys.argv[1:]

# MARK: The Loop
for arg in args:

    P_arg = Path(arg)

    # Skip if not an image
    if not is_image(P_arg):
        continue

    # Get the image resolution
    with Image.open(P_arg) as img:
        width, height = img.size

    # Remove any existing resolution tags
    remove_tag(T_portrait, file=arg)
    remove_tag(T_landscape, file=arg)
    remove_tag(T_square, file=arg)
    for tag in get_all_tags(arg):
        if tag.name in res_tags.keys():
            remove_tag(tag, file=arg)

    # Get+set the tags
    for tag in get_tags_by_dimensions(width, height):
        add_tag(tag, file=arg)
        print(f"〘{tag.name}〛👉 {P_arg.name}")
