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
    Tag(name="8K", color=GREEN): (7680, 4320),
    Tag(name="6K", color=GREEN): (6144, 3456),
    Tag(name="5K", color=GREEN): (5120, 2880),
    Tag(name="4K", color=GREEN): (3840, 2160),
    Tag(name="1080p", color=GREEN): (1920, 1080),
    Tag(name="720p", color=GREEN): (1280, 720),
    Tag(name="480p", color=GREEN): (640, 480),
    Tag(name="360p", color=GREEN): (480, 360),
    Tag(name="240p", color=GREEN): (352, 240),
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
    for tag, [tag_width, tag_height] in RES_TAGS.items():
        if tag_width < width and tag_height < height:
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
        duration_word = "Sec"
        # duration_word = p.plural("Sec", duration_num)
    else:
        duration_num = int(duration // 60)
        # duration_word = p.plural("Min", duration_num)
        duration_word = "Min"
    add_tag(Tag(name=f"{duration_num} {duration_word}", color=BLUE), file=str(path))
    print(f"〘{duration_num} {duration_word}〛👉 {path.name}")


# MARK: The Loop
for arg in sys.argv[1:]:

    path = Path(arg)

    if not path.is_file():
        print(f"{path.name} is not a file")
        continue

    # Skip if the file has an unrecognized suffix
    if not path.suffix.lower() in MOVIE_SUFFIXES:
        print(f"{path.suffix} is not a movie suffix")
        continue

    # Get the video metadata
    # Or skip if the file is corrupt
    try:
        reader = read_frames(str(path))
        meta = reader.__next__()
    except:
        print(f"{path.name} is corrupt")
        add_tag(T_CORRUPT, file=str(path))
        continue

    # Remove tags previously added by this script
    remove_existing_tags(path)
    # Resolution tags are easy to do together since they are mutually exclusive

    # Get the metadata
    reader = read_frames(path)
    meta = reader.__next__()

    # Get the video resolution
    width, height = meta["width"], meta["height"]
    # Set the video resolution-based tags
    add_resolution_tag(path, width, height)
    add_orientation_tag(path, width, height)

    # Get the video duration
    duration = meta["duration"]
    # Set the video duration-based tag
    add_duration_tag(path, duration)
