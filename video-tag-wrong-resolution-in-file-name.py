# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Video: Tag Wrong Resolution in File Name
#
# ## External Dependencies
#   * https://pypi.org/project/imageio_ffmpeg/
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# MARK: Imports

from operator import itemgetter
from os import PathLike, environ, pathsep
from pathlib import Path
from re import compile as re_compile
from re import search as re_search
from sys import argv
from typing import Union

from imageio_ffmpeg import read_frames
from macos_tags import Color, Tag
from macos_tags import add as add_tag_original
from macos_tags import get_all as get_all_tags_original
from macos_tags import remove as remove_tag_original

# MARK: PATH Additions
# To allow `imageio_ffmpeg` to find the binaries from Homebrew

environ["PATH"] += pathsep + "/usr/local/bin"
environ["PATH"] += pathsep + "/opt/homebrew/bin"
environ["PATH"] += pathsep + "/opt/homebrew/sbin"

# MARK: Constants

MOVIE_SUFFIXES = [
    ".asf",
    ".avi",
    ".divx",
    ".flv",
    ".m4v",
    ".mkv",
    ".mov",
    ".mp4",
    ".mpg",
    ".mpeg",
    ".ogv",
    ".ogm",
    ".rm",
    ".rmvb",
    ".ts",
    ".vob",
    ".webm",
    ".wmv",
]

RED = itemgetter("RED")(Color)

TAG_WRONG_RESOLTUION = Tag(name="Wrong Resolution", color=RED)

# MARK: Functions


# Extend `macos_tags.add` to accept a `PathLike` object
def add_tag(tag: Tag, file: Union[PathLike, str]) -> None:
    add_tag_original(tag, file=str(file))


# MARK: The Loop
args = argv[1:]
for arg in args:

    path = Path(arg).resolve()

    # ♻️ Skip if the path is not a file
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if not path.is_file():
        print(f"🛑 {path.name} 👉 not a file")
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # ♻️ Skip if the path does not have a recognized suffix
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if not path.suffix.lower() in MOVIE_SUFFIXES:
        print(f"🛑 {path.suffix} 👉 not a movie suffix")
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # (Try to) get the metadata or skip+tag if the video is corrupt
    # And if the video is corrupt, rename it to indicate that
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    try:
        reader = read_frames(path)
        meta = reader.__next__()
    except Exception as e:
        print(f"🚫 {path.name} 👉 corrupt")
        path.rename(path.with_stem(f"_CORRUPT_ {path.stem}"))
        print(e)
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Get the video resolution
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    vid_width, vid_height = meta["size"]
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Skip if the resolution is already in the file name
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    pattern_resolution = re_compile(rf"{vid_height}[pP]")
    if re_search(pattern_resolution, path.name):
        print(f"🛑 {path.name} 👉 has correct resolution")
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Rename the file to append the resolution
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    add_tag(TAG_WRONG_RESOLTUION, file=path)
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
