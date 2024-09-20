# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Tag Image by Resolution
#
# Resolutions are tagged by the nearest smallest "named" resolution.
#
# ## Resoltuion Tags
#   * 8K (7680x4320)
#   * 6K (6144x3456),
#   * 5K (5120x2880),
#   * 4K (3840x2160),
#   * 1080p (1920x1080),
#   * 720p (1280x720),
#   * 480p (720x480),
#   * 360p (640x360),
#   * trash (0x0),
#
# ## External Dependencies
#   * https://pypi.org/project/macos-tags/
#   * https://pypi.org/project/pillow/
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# MARK: Imports
import sys
from pathlib import Path

from macos_tags import Color, Tag
from macos_tags import add as add_tag
from macos_tags import get_all as get_all_tags
from macos_tags import remove as remove_tag
from PIL import Image

tags = {
    # For tagging purposes the `(width, height)` tuple is the minimum resolution
    Tag(name="8K", color=Color.BLUE): (7680, 4320),
    Tag(name="6K", color=Color.BLUE): (6144, 3456),
    Tag(name="5K", color=Color.GREEN): (5120, 2880),
    Tag(name="4K", color=Color.GREEN): (3840, 2160),
    Tag(name="1080p", color=Color.YELLOW): (1920, 1080),
    Tag(name="720p", color=Color.YELLOW): (1280, 720),
    Tag(name="480p", color=Color.YELLOW): (720, 480),
    Tag(name="360p", color=Color.YELLOW): (640, 360),
    Tag(name="Tiny", color=Color.RED): (0, 0),
}


# MARK: Functions
def is_image(file: Path) -> bool:
    if not file.is_file():
        return False
    fn_suffix = file.suffix.lower()
    image_suffixes = [".bmp", ".gif", ".jpeg", ".jpg", ".png", ".tiff"]
    return fn_suffix in image_suffixes


# This shoudl work since `dict`s have a guaranteed order in Python 3.7+
def get_tag_by_dimensions(width: int, height: int) -> Tag:
    for tag in tags:
        (min_width, min_height) = tags[tag]
        if min_width <= width and min_height <= height:
            return tag
    return list(tags.keys())[-1]


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
    for tag in get_all_tags(arg):
        if tag.name in tags.keys():
            remove_tag(tag, file=arg)

    # Get the resolution tag
    res_tag = get_tag_by_dimensions(width, height)

    # Add the resolution tag
    add_tag(res_tag, file=arg)
    print(f"Tagged {P_arg.name} with {res_tag.name}")
