# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Plex: Tag Music Video Type
#
# The goal of this script is to find music videos without one of the Plex-defined
# suffixes. It tags everything appropriately and then anything without a tag needs
# manual intervention.
#
# ## Video Types
#   * `-behindthescenes` (behind the scenes)
#   * `-concert` (concert performance)
#   * `-interview` (artist interview)
#   * `-live` (live music video)
#   * `-lyrics` (lyrics music video
#   * `-video` (regular music video)
#
# ## External Dependencies
#   * https://pypi.org/project/macos-tags/
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# MARK: Imports

from ast import Str
from operator import itemgetter
from os import PathLike
from pathlib import Path, PurePath
from sys import argv

from macos_tags import Color, Tag
from macos_tags import add as add_tag
from macos_tags import get_all as get_all_tags
from macos_tags import remove as remove_tag

# Probably a list of these out there somewhere
MV_FILE_SUFFIXES = [
    ".avi",
    ".divx",
    ".flv",
    ".m4v",
    ".mkv",
    ".mov",
    ".mp4",
    ".mpg",
    ".mpeg",
    ".ts",
    ".vob",
    ".webm",
]


# MARK: Tags

# Just to keep the lambdas to 1 line
(
    RED,
    ORANGE,
    YELLOW,
    GREEN,
    BLUE,
    PURPLE,
) = itemgetter(
    "RED",
    "ORANGE",
    "YELLOW",
    "GREEN",
    "BLUE",
    "PURPLE",
)(Color)

# These are all exclusive with only 1 tag per file
# Python guarantees the order of the dictionary now so the order here is meaningful
MV_TAGS = {
    Tag(name="Behind the Scenes", color=RED): "-behindthescenes",
    Tag(name="Concert", color=ORANGE): "-concert",
    Tag(name="Interview", color=YELLOW): "-interview",
    Tag(name="Live", color=GREEN): "-live",
    Tag(name="Lyrics", color=BLUE): "-lyrics",
    Tag(name="Video", color=PURPLE): "-video",
}

# MARK: Functions


def get_stem_suffix(file: PathLike) -> str:
    file = PurePath(file)
    partitoned_stem = str.rpartition(file.stem, "-")
    if partitoned_stem[1] == "":
        return ""
    return "-" + partitoned_stem[2]


def remove_tag_by_name(tag_name: str, file: PathLike) -> None:
    file = PurePath(file)
    for tag in get_all_tags(file=str(file)):
        if tag.name == tag_name:
            remove_tag(tag, file=str(file))
            break


def remove_tags_by_name(tag_names: list[str], file: PathLike) -> None:
    file = PurePath(file)
    if 1 == len(tag_names):
        remove_tag_by_name(tag_names[0], file=file)
        return
    for tag in get_all_tags(file=str(file)):
        if tag.name in tag_names:
            remove_tag(tag, file=str(file))


# MARK: The Loop
args = argv[1:]
for arg in args:

    path = Path(arg)

    # Skip if not a file
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if not path.is_file():
        print(f"🛑 {path.name} 👉 Not a file")
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Skip if not a movie
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if not path.suffix.lower() in MV_FILE_SUFFIXES:
        print(f"🛑 {path.name} 👉 Unrecognized suffix ({path.suffix})")
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Remove existing tags from the tags defined in this script
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    remove_tags_by_name([mv_tag.name for mv_tag in MV_TAGS.keys()], file=path)
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Add the applicable tags. Each is exclusive (one-per-file)
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    for tag, tag_stem_suffix in MV_TAGS.items():
        if get_stem_suffix(path) == tag_stem_suffix:
            add_tag(tag, file=str(path))
            break  # Because only one tag per file
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
