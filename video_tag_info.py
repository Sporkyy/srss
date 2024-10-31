# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Video: Tag Info
#
# ## External Dependencies
#   * https://pypi.org/project/macos-tags/
#   * https://pypi.org/project/imageio_ffmpeg/
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# MARK: Imports

import re
import sys
from operator import itemgetter
from os import environ, pathsep
from pathlib import Path

from imageio_ffmpeg import read_frames
from macos_tags import Color, Tag
from macos_tags import add as add_tag
from macos_tags import get_all as get_all_tags
from macos_tags import remove as remove_tag

from plex_tag_music_video_type import PURPLE

# MARK: PATH Additions
# To allow `imageio_ffmpeg` to find the binaries from Homebrew

environ["PATH"] += pathsep + "/usr/local/bin"
environ["PATH"] += pathsep + "/opt/homebrew/bin"
environ["PATH"] += pathsep + "/opt/homebrew/sbin"

# MARK: Constants

(
    BLUE,
    GREY,
    GREEN,
    ORANGE,
    PURPLE,
    RED,
) = itemgetter(
    "BLUE",
    "GREEN",
    "GREY",
    "ORANGE",
    "PURPLE",
    "RED",
)(Color)

T_CORRUPT = Tag(name="Corrupt", color=RED)

ORIENTATION_TAGS = {
    Tag(name="Portrait", color=ORANGE): lambda ratio: ratio < 1,
    Tag(name="Square", color=GREY): lambda ratio: 1 == ratio,
    Tag(name="Landscape", color=PURPLE): lambda ratio: 1 < ratio,
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


def ratio(w: int, h: int) -> float:
    return w / h


# MARK: The Loop
args = sys.argv[1:]
for arg in args:

    path = Path(arg)

    # Skip if the path is not a file
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if not path.is_file():
        print(f"🛑 {path.name} 👉 not a file")
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Skip if the path does not have a recognized suffix
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if not path.suffix.lower() in MOVIE_SUFFIXES:
        print(f"🛑 {path.suffix} 👉 not a movie suffix")
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Remove any pre-existing tags (that look like they were set by this script)
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    for tag in get_all_tags(file=str(path)):
        if (
            tag in [T_CORRUPT, *ORIENTATION_TAGS.keys()]
            or re.search(r"\d+x\d+", tag.name)  # resolution tag
            or re.search(r"\d{2}:\d{2}:\d{2}", tag.name)  # duration tag
        ):
            remove_tag(tag, file=str(path))
    # Resolution tags are easy to do together since they are mutually exclusive
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # (Try to) get the metadata or skip+tag if the video is corrupt
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    try:
        reader = read_frames(str(path))
        meta = reader.__next__()
    except Exception as e:
        print(f"🚫 {path.name} 👉 corrupt")
        print(e)
        add_tag(T_CORRUPT, file=str(path))
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Add the resolution-based tags
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    vid_width, vid_height = meta["size"]
    vid_ratio = ratio(vid_width, vid_height)

    for tag, test in ORIENTATION_TAGS.items():
        if test(vid_ratio):
            add_tag(tag, file=str(path))
            print(f"〘{tag.name}〛👉 {path.name}")
            break

    # Set the video resolution-based tags
    res_tag = Tag(name=f"{vid_width}x{vid_height}", color=GREEN)
    add_tag(res_tag, file=str(path))
    print(f"〘{res_tag.name}〛👉 {path.name}")
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Add the duration tag
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    duration = meta["duration"]
    duration_secs = int(duration)
    hours, remainder = divmod(duration_secs, 3600)
    minutes, seconds = divmod(remainder, 60)
    duration_tag = Tag(name=f"{hours:02}:{minutes:02}:{seconds:02}", color=BLUE)
    add_tag(duration_tag, file=str(path))
    print(f"〘{duration_tag.name}〛👉 {path.name}")
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
