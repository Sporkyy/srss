# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Video: Tag Info
#
# ## External Dependencies
#   * https://pypi.org/project/macos-tags/
#   * https://pypi.org/project/imageio_ffmpeg/
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# MARK: Imports

from operator import itemgetter
from os import PathLike, environ, pathsep
from pathlib import Path, PurePath
from re import Pattern
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

(
    RED,
    ORANGE,
    GREEN,
    BLUE,
    PURPLE,
    GRAY,
) = itemgetter(
    "RED",
    "ORANGE",
    "GREEN",
    "BLUE",
    "PURPLE",
    "GRAY",
)(Color)

TAG_CORRUPT = Tag(name="Corrupt", color=RED)

ORIENTATION_TAGS = {
    Tag(name="Portrait", color=ORANGE): lambda ratio: ratio < 1,
    Tag(name="Square", color=GRAY): lambda ratio: 1 == ratio,
    Tag(name="Landscape", color=PURPLE): lambda ratio: 1 < ratio,
}

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

# MARK: Functions


# Extend `macos_tags.add` to accept a `PathLike` object
def add_tag(tag: Tag, file: Union[PathLike, str]) -> None:
    add_tag_original(tag, file=str(file))


# Extend `macos_tags.get_all_tags` to accept a `PathLike` object
def get_all_tags(file: Union[PathLike, str]) -> list[Tag]:
    return get_all_tags_original(file=str(file))


# Extend `macos_tags.remove` to accept a `PathLike` object
def remove_tag(tag: Tag, file: Union[PathLike, str]) -> None:
    remove_tag_original(file=str(file), tag=tag)


def get_aspect_ratio(w: int, h: int) -> float:
    return w / h


def remove_tag_by_name(tag_name: str, file: Union[PathLike, str]) -> None:
    file = PurePath(file)
    for tag in get_all_tags(file=file):
        if tag.name == tag_name:
            remove_tag(tag, file=file)
            break


def remove_tag_by_re(
    tag_name_re: Union[Pattern, str], file: Union[PathLike, str]
) -> None:
    if isinstance(tag_name_re, str):
        tag_name_re = re_compile(tag_name_re)
    file = PurePath(file)
    for tag in get_all_tags(file=file):
        results = re_search(tag_name_re, tag.name)
        if results:
            remove_tag(tag, file=file)


def remove_tags_by_name(tag_names: list[str], file: Union[PathLike, str]) -> None:
    file = PurePath(file)
    if 1 == len(tag_names):
        remove_tag_by_name(tag_names[0], file=file)
        return
    for tag in get_all_tags(file=file):
        if tag.name in tag_names:
            remove_tag(tag, file=file)


def remove_tags_by_re(
    tag_names: list[Union[Pattern, str]], file: Union[PathLike, str]
) -> None:
    file = PurePath(file)
    if 1 == len(tag_names):
        remove_tag_by_re(tag_names[0], file=file)
        return
    for tag in get_all_tags(file=file):
        for tag_name in tag_names:
            if re_search(tag_name, tag.name):
                remove_tag(tag, file=file)


# MARK: The Loop
args = argv[1:]
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
    remove_tags_by_name(
        [
            TAG_CORRUPT.name,
            *[tag.name for tag in ORIENTATION_TAGS.keys()],
        ],
        file=path,
    )
    remove_tags_by_re(
        [
            re_compile(r"\d+x\d+"),
            re_compile(r"\d{2}:\d{2}:\d{2}"),
        ],
        file=path,
    )
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # (Try to) get the metadata or skip+tag if the video is corrupt
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    try:
        reader = read_frames(path)
        meta = reader.__next__()
    except Exception as e:
        print(f"🚫 {path.name} 👉 corrupt")
        print(e)
        add_tag(TAG_CORRUPT, file=path)
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # The order in which the tags are assigned matters when sorting by tags
    # So, I'm putting the
    #   1. Duration
    #   2. Orientation
    #   3. Resolution

    # Add the duration tag
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    duration = meta["duration"]
    duration_secs = int(duration)
    hours, remainder = divmod(duration_secs, 3600)
    minutes, seconds = divmod(remainder, 60)
    duration_tag = Tag(name=f"{hours:02}:{minutes:02}:{seconds:02}", color=BLUE)
    add_tag(duration_tag, file=path)
    print(f"〘{duration_tag.name}〛👉 {path.name}")
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Add the resolution-based tags
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    vid_width, vid_height = meta["size"]
    vid_ratio = get_aspect_ratio(vid_width, vid_height)

    for tag, test in ORIENTATION_TAGS.items():
        if test(vid_ratio):
            add_tag(tag, file=path)
            print(f"〘{tag.name}〛👉 {path.name}")
            break

    # Set the video resolution-based tags
    res_tag = Tag(name=f"{vid_width}x{vid_height}", color=GREEN)
    add_tag(res_tag, file=path)
    print(f"〘{res_tag.name}〛👉 {path.name}")
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
