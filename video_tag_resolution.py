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
from operator import itemgetter
from pathlib import Path

# import ffmpeg
from re import search as re_search

import inflect
from imageio_ffmpeg import read_frames
from macos_tags import Color, Tag
from macos_tags import add as add_tag
from macos_tags import get_all as get_all_tags
from macos_tags import remove as remove_tag

# MARK: Constants
T_CORRUPT = Tag(name="Corrupt", color=Color.RED)

BLUE, GREEN, YELLOW = itemgetter("BLUE", "GREEN", "YELLOW")(Color)

RES_TAGS = {
    # The conditionals use minimum resolutions for simplicity
    Tag(name="8K", color=GREEN): lambda w, h: 7680 < w and 4320 < h,
    Tag(name="6K", color=GREEN): lambda w, h: 6144 < w and 3456 < h,
    Tag(name="5K", color=GREEN): lambda w, h: 5120 < w and 2880 < h,
    Tag(name="4K", color=GREEN): lambda w, h: 3840 < w and 2160 < h,
    Tag(name="1080p", color=GREEN): lambda w, h: 1920 < w and 1080 < h,
    Tag(name="720p", color=GREEN): lambda w, h: 1280 < w and 720 < h,
    Tag(name="480p", color=GREEN): lambda w, h: 640 < w and 480 < h,
    Tag(name="360p", color=GREEN): lambda w, h: 480 < w and 360 < h,
    Tag(name="240p", color=GREEN): lambda w, h: 352 < w and 240 < h,
    Tag(name="Tiny", color=GREEN): lambda w, h: 0 < w and 0 < h,
}

ORIENTATION_TAGS = {
    Tag(name="Portrait", color=YELLOW): lambda w, h: w / h < 1,
    Tag(name="Square", color=YELLOW): lambda w, h: 1 == w / h,
    Tag(name="Landscape", color=YELLOW): lambda w, h: 1 < w / h,
}

MOVIE_SUFFIXES = [
    ".avi",
    ".divx",
    ".flv",
    ".m4v",
    ".mkv",
    ".mov",
    ".mp4",
    ".mpg",
    ".mpeg",
    ".vob",
    ".webm",
]

# MARK: Variables

p = inflect.engine()

# MARK: Functions


def add_resolution_tag(path: Path, width: int, height: int):
    for tag, test in RES_TAGS.items():
        if test(width, height):
            add_tag(tag, file=str(path))
            print(f"〘{tag.name}〛👉 {path.name}")
            break


def add_orientation_tag(path: Path, width: int, height: int):
    for tag, test in ORIENTATION_TAGS.items():
        if test(width, height):
            add_tag(tag, file=str(path))
            print(f"〘{tag.name}〛👉 {path.name}")
            break


def remove_existing_tags(path: Path):
    for tag in get_all_tags(str(path)):
        if T_CORRUPT == tag:
            remove_tag(tag, file=str(path))
        if tag in RES_TAGS.keys():
            remove_tag(tag, file=str(path))
        if tag in ORIENTATION_TAGS.keys():
            remove_tag(tag, file=str(path))
        if re_search(r"^\d Mins?$", tag.name):
            remove_tag(tag, file=str(path))


# Duration tags are all an integer number of mintues (rounded down)
# e.g. 90 Mins
def add_duration_tag(path: Path, duration: float):
    if duration < 60:
        duration_num = int(duration)
        duration_word = p.plural("Sec", duration_num)
    else:
        duration_num = int(duration // 60)
        duration_word = p.plural("Min", duration_num)
    add_tag(Tag(name=f"{duration_num} {duration_word}", color=BLUE), file=str(path))
    print(f"〘{duration_num} {duration_word}〛👉 {path.name}")


# MARK: The Loop
for arg in sys.argv[1:]:

    P_arg = Path(arg)

    if not P_arg.is_file():
        print(f"{P_arg.name} is not a file")
        continue

    # Skip if the file has an unrecognized suffix
    if not P_arg.suffix.lower() in MOVIE_SUFFIXES:
        print(f"{P_arg.suffix} is not a movie suffix")
        continue

    # Get the video metadata
    # Or skip if the file is corrupt
    try:
        reader = read_frames(str(P_arg))
        meta = reader.__next__()
    except:
        print(f"{P_arg.name} is corrupt")
        add_tag(T_CORRUPT, file=str(P_arg))
        continue

    # Remove tags previously added by this script
    remove_existing_tags(P_arg)
    # Resolution tags are easy to do together since they are mutually exclusive

    # Get the metadata
    reader = read_frames(P_arg)
    meta = reader.__next__()

    # Get the video resolution
    width, height = meta["width"], meta["height"]
    # Set the video resolution-based tags
    add_resolution_tag(P_arg, width, height)
    add_orientation_tag(P_arg, width, height)

    # Get the video duration
    duration = meta["duration"]
    # Set the video duration-based tag
    add_duration_tag(P_arg, duration)
