# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Plex: Tag Music Video Type
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
import sys
from operator import itemgetter
from pathlib import Path

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

# Just to keep the lambdas to 1 line
ORANGE, PURPLE, RED = itemgetter("ORANGE", "PURPLE", "RED")(Color)


def get_stem_suffix(fp: Path) -> str:
    partitoned_stem = str.rpartition(fp.stem, "-")
    if partitoned_stem[1] == "":
        return ""
    return "-" + partitoned_stem[2]


def isUnspecified(p: Path) -> bool:
    return 0 == len(get_stem_suffix(p))


def isBehindTheScenes(p: Path) -> bool:
    return "-behindthescenes" == get_stem_suffix(p)


def isConcert(p: Path) -> bool:
    return "-concert" == get_stem_suffix(p)


def isInterview(p: Path) -> bool:
    return "-interview" == get_stem_suffix(p)


def isLive(p: Path) -> bool:
    return "-live" == get_stem_suffix(p)


def isLyrics(p: Path) -> bool:
    return "-lyrics" == get_stem_suffix(p)


def isVideo(p: Path) -> bool:
    return "-video" == get_stem_suffix(p)


# MARK: Tags

# These are all exclusive with only 1 tag per file
# Python guarantees the order of the dictionary now so the order here is meaningful
TAGS = {
    Tag(name="Behind the Scenes", color=PURPLE): isBehindTheScenes,
    Tag(name="Concert", color=PURPLE): isConcert,
    Tag(name="Interview", color=PURPLE): isInterview,
    Tag(name="Live", color=PURPLE): isLive,
    Tag(name="Lyrics", color=PURPLE): isLyrics,
    Tag(name="Video", color=PURPLE): isVideo,
    Tag(name="Unspecified", color=RED): lambda p: 0 == len(get_stem_suffix(p)),
    Tag(name="Invalid", color=ORANGE): True,  # Catch all
}

# MARK: The Loop
for arg in sys.argv[1:]:

    P_arg = Path(arg)

    # Skip if not a file
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if not P_arg.is_file():
        print(f"🛑 {P_arg.name} 👉 Not a file")
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Skip if not a movie
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if not P_arg.suffix.lower() in MV_FILE_SUFFIXES:
        print(f"🛑 {P_arg.name} 👉 Unrecognized suffix ({P_arg.suffix})")
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Remove existing tags from the tags defined in this script
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    for tag in get_all_tags(file=str(P_arg)):
        if tag in TAGS.keys():
            remove_tag(tag, file=str(P_arg))
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Add the applicable tags. Each is exclusive (one-per-file)
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    for tag, check in TAGS.items():
        if check(get_stem_suffix(P_arg)) if callable(check) else check:
            add_tag(tag, file=str(P_arg))
            break  # Because only one tag per file
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
