# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Image: Tag Info
#
# Resolutions are tagged by the nearest smallest "named" resolution.
#
# ## How to configure `imagemagick` for `wand` in `fish`
# ```fish
# set -gx MAGICK_HOME /opt/homebrew/opt/imagemagick
# fish_add_path {$MAGICK_HOME}/bin
# ```
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
from math import e
from os import remove
from pathlib import Path

import PIL
from macos_tags import Color, Tag
from macos_tags import add as add_tag
from macos_tags import get_all as get_all_tags
from macos_tags import remove as remove_tag
from PIL import Image as ImageP
from wand.image import Image as ImageW

# MARK: Tags

T_CORRUPT = Tag(name="Corrupt", color=Color.RED)

RES_TAGS = {
    # For tagging purposes the `(width, height)` tuple is the minimum resolution
    Tag(name="8K", color=Color.BLUE): (7680, 4320),
    Tag(name="6K", color=Color.BLUE): (6144, 3456),
    Tag(name="5K", color=Color.GREEN): (5120, 2880),
    Tag(name="4K", color=Color.GREEN): (3840, 2160),
    Tag(name="1080p", color=Color.YELLOW): (1920, 1080),
}

ORIENTATION_TAGS = {
    Tag(name="Portrait", color=Color.PURPLE): lambda x: x < 1,
    Tag(name="Square", color=Color.PURPLE): lambda x: 1 == x,
    Tag(name="Landscape", color=Color.PURPLE): lambda x: 1 < x,
}


# MARK: Functions


# Shortcuts does this already when running the script in "production"
# (Assuming the Input is configured properly for Quick Actions)
# But doing it here helps when running it in "development"
def is_image(file: Path) -> bool:
    if not file.is_file():
        return False
    fn_suffix = file.suffix.lower()
    image_suffixes = [".bmp", ".gif", ".jpeg", ".jpg", ".png", ".tiff", ".webp"]
    if fn_suffix not in image_suffixes:
        return False
    try:
        pil_check(file)
        magick_check(file)
    except Exception as e:
        print(f"🚫 {file.name} {e}")
        add_tag(T_CORRUPT, file=arg)
        return False
    return True


# This should work since `dict`s have a guaranteed order in Python 3.7+
def get_tags_by_dimensions(width: int, height: int) -> list:
    tags = []
    for tag, orientation in ORIENTATION_TAGS.items():
        if orientation(width / height):
            tags.append(tag)
            break
    for tag, (min_width, min_height) in RES_TAGS.items():
        if min_width <= width and min_height <= height:
            tags.append(tag)
            break
    return tags


def remove_info_tags(file: Path):
    for tag in get_all_tags(file.absolute().as_posix()):
        if tag in RES_TAGS.keys():
            remove_tag(tag, file=file.absolute().as_posix())
        if tag in ORIENTATION_TAGS.keys():
            remove_tag(tag, file=file.absolute().as_posix())
        if T_CORRUPT == tag:
            remove_tag(tag, file=file.absolute().as_posix())


# https://github.com/ftarlao/check-media-integrity/blob/master/check_mi.py
def pil_check(filename: Path):
    img = ImageP.open(filename)  # open the image file
    img.verify()  # verify that it is a good image, without decoding it.. quite fast
    img.close()

    # Image manipulation is mandatory to detect few defects
    img = ImageP.open(filename)  # open the image file
    img.transpose(ImageP.Transpose.FLIP_LEFT_RIGHT)
    img.close()


# https://github.com/ftarlao/check-media-integrity/blob/master/check_mi.py
def magick_check(filename: Path, flip=True):
    # very useful for xcf, psd and aslo supports pdf
    img = ImageW(filename=filename)
    if flip:
        temp = img.flip
    else:
        temp = img.make_blob(format="bmp")
    img.close()
    return temp


args = sys.argv[1:]

# MARK: The Loop
for arg in args:

    P_arg = Path(arg)

    # Skip if not an image
    if not is_image(P_arg):
        continue

    # Remove any existing resolution tags
    remove_info_tags(P_arg)

    # Get the image resolution
    with ImageP.open(P_arg) as img:
        width, height = img.size

    # Get+set the tags
    for tag in get_tags_by_dimensions(width, height):
        add_tag(tag, file=arg)
        print(f"〘{tag.name}〛👉 {P_arg.name}")
