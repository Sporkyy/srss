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

# MARK: Constants

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

# MARK: Tags

# These are all exclusive with only 1 tag per file
# Python guarantees the order of the dictionary now so the order here is meaningful
TAGS = {
    Tag(name="Unspecified", color=RED): lambda s: 0 == len(s),
    Tag(name="Behind the Scenes", color=PURPLE): lambda s: "-behindthescenes" == s,
    Tag(name="Concert", color=PURPLE): lambda s: "-concert" == s,
    Tag(name="Interview", color=PURPLE): lambda s: "-interview" == s,
    Tag(name="Live", color=PURPLE): lambda s: "-live" == s,
    Tag(name="Lyrics", color=PURPLE): lambda s: "-lyrics" == s,
    Tag(name="Video", color=PURPLE): lambda s: "-video" == s,
    Tag(name="Invalid", color=ORANGE): True,  # Catch all
}


def get_stem_suffix(fp: Path) -> str:
    partitoned_stem = str.rpartition(fp.stem, "-")
    if partitoned_stem[1] == "":
        return ""
    return "-" + partitoned_stem[2]


args = sys.argv[1:]

# MARK: The Loop
for arg in args:

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
