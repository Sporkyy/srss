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
from pathlib import Path

from macos_tags import Color, Tag
from macos_tags import add as add_tag
from macos_tags import get_all as get_all_tags
from macos_tags import remove as remove_tag
from PIL import Image as ImageP

# from wand.image import Image as ImageW

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
# def magick_check(filename: Path, flip=True):
#     # very useful for xcf, psd and aslo supports pdf
#     img = ImageW(filename=filename)
#     if flip:
#         temp = img.flip
#     else:
#         temp = img.make_blob(format="bmp")
#     img.close()
#     return temp


# MARK: The Loop
args = sys.argv[1:]
for arg in args:

    path = Path(arg)

    # Ensure it's a file
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if not path.is_file():
        print(f"🛑 {path.name} 👉 Not a file")
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Ensure it's an image
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if not path.suffix.lower() in IMAGE_SUFFIXES:
        print(f"🛑 {path.name} 👉 Not an image")
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Remove existing tags
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    for tag in get_all_tags(file=str(path)):
        if tag in [T_CORRUPT, *ORIENTATION_TAGS.keys()] or re.search(
            r"\d+x\d+", tag.name
        ):
            remove_tag(tag, file=str(path))
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Ensure it's not corrupt
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    try:
        pil_check(path)
        # magick_check(path)
    except Exception as e:
        print(f"🚫 {path.name} 👉 Corrupt")
        print(e)
        add_tag(T_CORRUPT, file=str(path))
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Apply the appropriate tags
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # Get the image resolution
    with ImageP.open(path) as img:
        img_width, img_height = img.size
        img_ratio = ratio(img_width, img_height)

    # Set the orientation tags
    for tag, test in ORIENTATION_TAGS.items():
        if test(img_ratio):
            add_tag(tag, file=str(path))
            print(f"〘{tag.name}〛👉 {path.name}")
            break

    # Set the resolution tag
    res_tag = Tag(name=f"{img_width}x{img_height}", color=GREEN)
    add_tag(res_tag, file=str(path))
    print(f"〘{res_tag.name}〛👉 {path.name}")
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
