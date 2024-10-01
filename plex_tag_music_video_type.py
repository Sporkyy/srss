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
from pathlib import Path

from macos_tags import Color, Tag
from macos_tags import add as add_tag
from macos_tags import get_all as get_all_tags
from macos_tags import remove as remove_tag

# MARK: Constants

# Probably a list of these out there somewhere
MV_FILE_SUFFIXES = [
    ".avi",
    ".flv",
    ".m4v",
    ".mkv",
    ".mov",
    ".mp4",
    ".mpg",
    ".mpeg",
    ".webm",
]

# Just to keep the lambdas to 1 line
ORANGE = Color.ORANGE
RED = Color.RED
PURPLE = Color.PURPLE

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


# MARK: Functions
def is_movie(fp: Path) -> bool:
    if not fp.is_file():
        return False
    return fp.suffix.lower() in MV_FILE_SUFFIXES


def get_stem_suffix(fp: Path) -> str:
    partitoned_stem = str.rpartition(fp.stem, "-")
    if partitoned_stem[1] == "":
        return ""
    return "-" + partitoned_stem[2]


args = sys.argv[1:]

# MARK: The Loop
for arg in args:

    P_arg = Path(arg)

    # Skip if not a movie
    if not is_movie(P_arg):
        continue

    # Remove existing tags (TAGS defined in this script)
    for tag in get_all_tags(file=P_arg.as_posix()):
        if tag in TAGS.keys():
            remove_tag(tag, file=P_arg.as_posix())

    # Add tags based on the tests in TAGS (These are on-per-file)
    for tag, check in TAGS.items():
        if check(get_stem_suffix(P_arg)) if callable(check) else check:
            add_tag(tag, file=P_arg.as_posix())
            break  # Only one tag per file
