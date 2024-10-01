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

# MARK: Imports
import os
import sys
from pathlib import Path

from macos_tags import Color, Tag
from macos_tags import add as add_tag
from macos_tags import remove_all as remove_all_tags

MOVIE_COUNT_TAGS = {
    Tag(name="No movie", color=Color.RED): lambda cnt: 0 == cnt,
    Tag(name="Multiple movies", color=Color.RED): lambda cnt: 1 < cnt,
}


EXTRAS_TAGS = {
    "behind the scenes": lambda p: (
        "behind the scenes" == p.name.lower()
        if p.is_dir()
        else p.stem.lower().endswith("-behindthescenes")
    ),
    "deleted scenes": lambda p: (
        "deleted scenes" == p.name.lower()
        if p.is_dir()
        else p.stem.lower().endswith("-deleted")
    ),
    "featurettes": lambda p: (
        "featurettes" == p.name.lower()
        if p.is_dir()
        else p.stem.lower().endswith("-featurette")
    ),
    "interviews": lambda p: (
        "interviews" == p.name.lower()
        if p.is_dir()
        else p.stem.lower().endswith("-interview")
    ),
    "other": lambda p: (
        "other" == p.name.lower() if p.is_dir() else p.stem.lower().endswith("-other")
    ),
    "scenes": lambda p: (
        "scenes" == p.name.lower() if p.is_dir() else p.stem.lower().endswith("-scene")
    ),
    "shorts": lambda p: (
        "shorts" == p.name.lower() if p.is_dir() else p.stem.lower().endswith("-short")
    ),
    "trailers": lambda p: (
        "trailers" == p.name.lower()
        if p.is_dir()
        else p.stem.lower().endswith("-trailer")
    ),
}


# MARK: Functions
def is_movie(file: Path) -> bool:
    if not file.is_file():
        return False
    fn_suffix = file.suffix.lower()
    movie_suffixes = [".avi", ".m4v", ".mkv", ".mov", ".mp4", ".mpg", ".mpeg", ".webm"]
    return fn_suffix in movie_suffixes


args = sys.argv[1:]

# MARK: The Loop
for arg in args:

    P_arg = Path(arg)

    # Skip if not a directory
    if not P_arg.is_dir():
        continue

    for fn in os.listdir(P_arg):
        P_fn = Path(fn)
        cnt_movies = 0
        for tag, fn_check in EXTRAS_TAGS.items():
            if fn_check(P_fn):
                add_tag(tag, file=arg)
            elif is_movie(P_fn):
                cnt_movies += 1
        for tag, fn_check in MOVIE_COUNT_TAGS.items():
            if fn_check(P_fn):
                add_tag(tag, file=arg)
                break
