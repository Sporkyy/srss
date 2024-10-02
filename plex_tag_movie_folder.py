# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Plex: Tag Movie Folder
#
# ## Extras Directories
#   * `behind the scenes`
#   * `deleted scenes`
#   * `featurettes`
#   * `interviews`
#   * `other`
#   * `scenes`
#   * `shorts`
#   * `trailers`
#
# ## External Dependencies
#   * https://pypi.org/project/macos-tags/
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

import sys
from operator import is_, itemgetter

# MARK: Imports
from os import listdir, name
from pathlib import Path

from macos_tags import Color, Tag
from macos_tags import add as add_tag
from macos_tags import remove_all as remove_all_tags

# MARK: Constants

BLUE, RED = itemgetter("BLUE", "RED")(Color)

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

MOVIE_COUNT_TAGS = {
    Tag(name="No movie", color=RED): lambda cnt: 0 == cnt,
    Tag(name="Multiple movies", color=RED): lambda cnt: 1 < cnt,
}


EXTRAS_TAGS = {
    Tag(name="Behind the Scenes", color=BLUE): lambda p: is_behind_the_scenes(p),
    Tag(name="Deleted Scenes", color=BLUE): lambda p: is_deleted_scene(p),
    Tag(name="Featurettes", color=BLUE): lambda p: is_featurette(p),
    Tag(name="Interviews", color=BLUE): lambda p: is_interview(p),
    Tag(name="Other", color=BLUE): lambda p: is_other(p),
    Tag(name="Scenes", color=BLUE): lambda p: is_scene(p),
    Tag(name="Shorts", color=BLUE): lambda p: is_short(p),
    Tag(name="Trailers", color=BLUE): lambda p: is_trailer(p),
}


# MARK: Functions
def is_movie(fn: Path) -> bool:
    if not fn.is_file():
        return False
    return fn.suffix.lower() in MOVIE_SUFFIXES


def is_extra(fn: Path) -> bool:
    if not fn.is_dir():
        return False
    return fn.name.lower() in EXTRAS_TAGS


def is_behind_the_scenes(p: Path) -> bool:
    return (
        p.stem.lower().endswith("-behindthescenes")
        or p.parent.name.lower() == "behind the scenes"
    )


def is_deleted_scene(p: Path) -> bool:
    return (
        p.stem.lower().endswith("-deletedscene")
        or p.parent.name.lower() == "deleted scenes"
    )


def is_interview(p: Path) -> bool:
    return (
        p.stem.lower().endswith("-interview") or p.parent.name.lower() == "interviews"
    )


def is_featurette(p: Path) -> bool:
    return (
        p.stem.lower().endswith("-featurette") or p.parent.name.lower() == "featurettes"
    )


def is_other(p: Path) -> bool:
    return p.stem.lower().endswith("-other") or p.parent.name.lower() == "other"


def is_scene(p: Path) -> bool:
    return p.stem.lower().endswith("-scene") or p.parent.name.lower() == "scenes"


def is_short(p: Path) -> bool:
    return p.stem.lower().endswith("-short") or p.parent.name.lower() == "shorts"


def is_trailer(p: Path) -> bool:
    return p.stem.lower().endswith("-trailer") or p.parent.name.lower() == "trailers"


# MARK: The Loop
for fn in sys.argv[1:]:

    P_fn = Path(fn)

    # Skip if not a directory
    if not P_fn.is_dir():
        continue

    for fn in listdir(P_fn):
        P_fn = Path(fn)
        cnt_movies = 0
        for tag, fn_check in EXTRAS_TAGS.items():
            if fn_check(P_fn):
                add_tag(tag, file=fn)
            elif is_movie(P_fn):
                cnt_movies += 1
        for tag, fn_check in MOVIE_COUNT_TAGS.items():
            if fn_check(P_fn):
                add_tag(tag, file=fn)
                break
