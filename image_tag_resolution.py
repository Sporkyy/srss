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
import sys
from ast import List
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
    # Have to use `lambda`s here because floating point division is used
    Tag(name="Portrait", color=YELLOW): lambda ratio: ratio < 1,
    Tag(name="Square", color=YELLOW): lambda ratio: 1 == ratio,
    Tag(name="Landscape", color=YELLOW): lambda ratio: 1 < ratio,
}

RES_TAGS = {
    # For tagging purposes the `(width, height)` tuple is the minimum resolution
    Tag(name="8K", color=GREEN): (7680, 4320),
    Tag(name="6K", color=GREEN): (6144, 3456),
    Tag(name="5K", color=GREEN): (5120, 2880),
    Tag(name="4K", color=GREEN): (3840, 2160),
    Tag(name="1440p", color=GREEN): (2560, 1440),
    Tag(name="1K", color=GREEN): (1920, 1080),
    Tag(name="720p", color=GREEN): (1280, 720),
    Tag(name="480p", color=GREEN): (640, 480),
    Tag(name="360p", color=GREEN): (480, 360),
    Tag(name="240p", color=GREEN): (352, 240),
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
        if (
            tag in [T_CORRUPT]
            or tag in RES_TAGS.keys()
            or tag in ORIENTATION_TAGS.keys()
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

    print(f"📏 {path.name} 👉 {img_width}x{img_height} ({img_ratio})")

    # Set the orientation tags
    for tag, test in ORIENTATION_TAGS.items():
        if test(img_ratio):
            add_tag(tag, file=str(path))
            print(f"〘{tag.name}〛👉 {path.name}")
            break

    # Set the resolution tags. Only for if landscape orientation
    for tag, [req_width, req_height] in RES_TAGS.items():
        if 1 < img_ratio and req_width <= img_width and req_height <= img_height:
            add_tag(tag, file=str(path))
            print(f"〘{tag.name}〛👉 {path.name}")
            break
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
