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
from pathlib import Path
from operator import itemgetter

import ffmpeg
from macos_tags import Color, Tag
from macos_tags import add as add_tag
from macos_tags import get_all as get_all_tags
from macos_tags import remove as remove_tag

T_CORRUPT = Tag(name="Corrupt", color=Color.RED)

BLUE, GREEN = itemgetter("BLUE", "GREEN")(Color)

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
    Tag(name="Portrait", color=BLUE): lambda w, h: w / h < 1,
    Tag(name="Square", color=BLUE): lambda w, h: 1 == w / h,
    Tag(name="Landscape", color=BLUE): lambda w, h: 1 < w / h,
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

# MARK: Functions


# Shortcuts does this already when running the script in "production"
# (Assuming the Input is configured properly for Quick Actions)
# But doing it here helps when running it in "development"
def is_video(file: Path) -> bool:
    if not file.is_file():
        return False
    fn_suffix = file.suffix.lower()
    if fn_suffix not in MOVIE_SUFFIXES:
        return False
    # try:
    #     ffmpeg_check(file)
    # except Exception as e:
    #     print(f"🚫 {file.name} {e}")
    #     add_tag(T_CORRUPT, file=arg)
    #     return False
    if not ffmpeg_check(file)
        print(f"🚫 {file.name} {e}")
        add_tag(T_CORRUPT, file=arg)
        return False
    return True


# https://github.com/ftarlao/check-media-integrity/blob/master/check_mi.py
def ffmpeg_check(filename, error_detect="default", threads=0):
    if error_detect == "default":
        stream = ffmpeg.input(filename)
    else:
        if error_detect == "strict":
            custom = "+crccheck+bitstream+buffer+explode"
        else:
            custom = error_detect
        stream = ffmpeg.input(filename, **{"err_detect": custom, "threads": threads})

    stream = stream.output("pipe:", format="null")
    stream.run(capture_stdout=True, capture_stderr=True)


def remove_info_tags(file: Path):
    for tag in get_all_tags(str(file)):
        if tag in RES_TAGS.keys():
            remove_tag(tag, file=str(file))
        if tag in ORIENTATION_TAGS.keys():
            remove_tag(tag, file=str(file))
        if T_CORRUPT == tag:
            remove_tag(tag, file=str(file))


args = sys.argv[1:]

# MARK: The Loop
for arg in args:

    P_arg = Path(arg)

    # Skip if not an image
    if not is_video(P_arg):
        continue

    # Remove any existing resolution tags
    remove_info_tags(P_arg)

    # Get the image resolution
    # with ImageP.open(P_arg) as img:
    #     width, height = img.size

    # Get+set the tags
    # for tag in get_appropriate_tags(img):
    #     add_tag(tag, file=arg)
    #     print(f"〘{tag.name}〛👉 {P_arg.name}")
