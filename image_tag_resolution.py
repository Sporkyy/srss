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

# MARK: Imports
import sys
from ast import List
from operator import itemgetter
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

BLUE, GREEN, YELLOW, PURPLE = itemgetter("BLUE", "GREEN", "YELLOW", "PURPLE")(Color)

RES_TAGS = {
    # For tagging purposes the `(width, height)` tuple is the minimum resolution
    Tag(name="8K", color=BLUE): lambda w, h: 7680 < w and 4320 < h,
    Tag(name="6K", color=BLUE): lambda w, h: 6144 < w and 3456 < h,
    Tag(name="5K", color=GREEN): lambda w, h: 5120 < w and 2880 < h,
    Tag(name="4K", color=GREEN): lambda w, h: 3840 < w and 2160 < h,
    Tag(name="1080p", color=YELLOW): lambda w, h: 1920 < w and 1080 < h,
}

ORIENTATION_TAGS = {
    Tag(name="Portrait", color=PURPLE): lambda w, h: w / h < 1,
    Tag(name="Square", color=PURPLE): lambda w, h: 1 == w / h,
    Tag(name="Landscape", color=PURPLE): lambda w, h: 1 < w / h,
}

IMAGE_SUFFIXES = [".bmp", ".gif", ".jpeg", ".jpg", ".png", ".tiff", ".webp"]

# MARK: Functions


# Shortcuts does this already when running the script in "production"
# (Assuming the Input is configured properly for Quick Actions)
# But doing it here helps when running it in "development"
def is_image(file: Path) -> bool:
    if not file.is_file():
        return False
    fn_suffix = file.suffix.lower()
    if fn_suffix not in IMAGE_SUFFIXES:
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
def get_appropriate_tags(img) -> list:
    tags = []
    width, height = img.size
    for tag, test in ORIENTATION_TAGS.items():
        if test(width, height):
            tags.append(tag)
            break
    for tag, test in RES_TAGS.items():
        if test(width, height):
            tags.append(tag)
            break
    return tags


def remove_info_tags(file: Path):
    for tag in get_all_tags(str(file)):
        if tag in RES_TAGS.keys():
            remove_tag(tag, file=str(file))
        if tag in ORIENTATION_TAGS.keys():
            remove_tag(tag, file=str(file))
        if T_CORRUPT == tag:
            remove_tag(tag, file=str(file))


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
    for tag in get_appropriate_tags(img):
        add_tag(tag, file=arg)
        print(f"〘{tag.name}〛👉 {P_arg.name}")
