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

from operator import itemgetter
from pathlib import Path
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
    ".vob",
    ".webm",
]


# MARK: Tags

# Just to keep the lambdas to 1 line
(
    ORANGE,
    PURPLE,
    RED,
) = itemgetter(
    "ORANGE",
    "PURPLE",
    "RED",
)(Color)

# These are all exclusive with only 1 tag per file
# Python guarantees the order of the dictionary now so the order here is meaningful
MV_TAGS = {
    Tag(name="Behind the Scenes", color=PURPLE): "-behindthescenes",
    Tag(name="Concert", color=PURPLE): "-concert",
    Tag(name="Interview", color=PURPLE): "-interview",
    Tag(name="Live", color=PURPLE): "-live",
    Tag(name="Lyrics", color=PURPLE): "-lyrics",
    Tag(name="Video", color=PURPLE): "-video",
}

# MARK: Functions


def get_stem_suffix(fp: Path) -> str:
    partitoned_stem = str.rpartition(fp.stem, "-")
    if partitoned_stem[1] == "":
        return ""
    return "-" + partitoned_stem[2]


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
    for tag in get_all_tags(file=str(path)):
        if tag in MV_TAGS.keys():
            remove_tag(tag, file=str(path))
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Add the applicable tags. Each is exclusive (one-per-file)
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    for tag, tag_stem_suffix in MV_TAGS.items():
        if get_stem_suffix(path) == tag_stem_suffix:
            add_tag(tag, file=str(path))
            break  # Because only one tag per file
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
