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

from glob import glob
from operator import itemgetter
from os import PathLike
from pathlib import Path, PurePath
from sys import argv
from typing import Union

from macos_tags import Color, Tag
from macos_tags import add as add_tag_original
from macos_tags import get_all as get_all_tags_original
from macos_tags import remove as remove_tag_original

# MARK: Constants

# https://github.com/github/gitignore/blob/main/Global/macOS.gitignore
IGNORE_FILES = [
    ".AppleDouble",
    ".DS_Store",
    ".LSOverride",
    ".plexmatch",
]

# TODO: Find if ther is an official list of image suffixes for Plex
# IMAGE_SUFFIXES = [".jpg", ".jpeg", ".png", ".tiff", ".webp"]

# TODO: Find if there is an official list of movie suffixes for Plex
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
    ".ts",
    ".vob",
    ".webm",
]


# MARK: Tags

BLUE, RED = itemgetter("BLUE", "RED")(Color)

# These tags go on the movie folder
# e.g. `The Matrix (1999) {imdb-tt0133093}`

# Tags based on the number of movies in the folder
TAG_HAS_NO_MOVIES = Tag(name="Has no movies", color=RED)
TAG_HAS_MULTIPLE_MOVIES = Tag(name="Has multiple movies", color=RED)
# Tags based on the presence of Plex extras
HAS_EXTRAS_TAGS = {
    Tag(name="Has behind the scenes", color=BLUE): [
        "-behindthescenes",
        "behind the scenes",
    ],
    Tag(name="Has deleted scenes", color=BLUE): [
        "-deleted",
        "deleted scenes",
    ],
    Tag(name="Has featurettes", color=BLUE): [
        "-featurette",
        "featurettes",
    ],
    Tag(name="Has interviews", color=BLUE): [
        "-interview",
        "interviews",
    ],
    Tag(name="Has other", color=BLUE): [
        "-other",
        "other",
    ],
    Tag(name="Has scenes", color=BLUE): [
        "-scene",
        "scenes",
    ],
    Tag(name="Has shorts", color=BLUE): [
        "-short",
        "shorts",
    ],
    Tag(name="Has trailers", color=BLUE): [
        "-trailer",
        "trailers",
    ],
}


# MARK: Functions


# `macos_tags` Extensions adding `PathLike` Support
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Extend `macos_tags.add` to accept a `PathLike` object
def add_tag(tag: Tag, file: Union[PathLike, str]) -> None:
    add_tag_original(tag, file=str(file))


# Extend `macos_tags.get_all_tags` to accept a `PathLike` object
def get_all_tags(file: Union[PathLike, str]) -> list[Tag]:
    return get_all_tags_original(file=str(file))


# Extend `macos_tags.remove` to accept a `PathLike` object
def remove_tag(tag: Tag, file: Union[PathLike, str]) -> None:
    remove_tag_original(file=str(file), tag=tag)


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# def has_movie_suffix(path: Path) -> bool:
#     return path.suffix.lower() in MOVIE_SUFFIXES


def remove_tag_by_name(tag_name: str, file: PathLike) -> None:
    file = PurePath(file)
    for tag in get_all_tags(file=file):
        if tag.name == tag_name:
            remove_tag(tag, file=file)
            break


def remove_tags_by_name(tag_names: list[str], file: PathLike) -> None:
    file = PurePath(file)
    if 1 == len(tag_names):
        remove_tag_by_name(tag_names[0], file=file)
        return
    for tag in get_all_tags(file=file):
        if tag.name in tag_names:
            remove_tag(tag, file=file)


# TODO: Figure out if this is even true
# i.e. Can an extra with a suffix be in any subdirectory of the movie folder?
# i.e. Can an extra in an extras subdirectory be at any depth?
def is_extra(path: Path, sub_path: Path, suffix: str, parent_dir_name: str) -> bool:
    if sub_path.stem.lower().endswith(suffix) and sub_path.parent.samefile(path):
        return True
    elif (
        path.parent.name.lower() == parent_dir_name
        and sub_path.parent.parent.samefile(path)
    ):
        return True
    else:
        return False


# TODO: There are multiple names for the poster image; gotta collect them all!
# def is_poster(path: Path, sub_path: Path) -> bool:
#     return path.stem.lower() == "poster"


# MARK: The Loop
args = argv[1:]
for arg in args:

    P_movie_dir = Path(arg)

    # Ensure a directory
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if not P_movie_dir.is_dir():
        print(f"🛑 {P_movie_dir.name} 👉 Not a directory")
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # print(glob(str(P_movie_dir / "**/*"), recursive=True))
    # exit()

    # 🏷️ Remove existing tags
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    for tag in get_all_tags(file=P_movie_dir):
        if tag in [
            *HAS_EXTRAS_TAGS.keys(),
            TAG_HAS_NO_MOVIES,
            TAG_HAS_MULTIPLE_MOVIES,
        ]:
            remove_tag(tag, file=P_movie_dir)
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # 📁 Loop through the directory and determine the appropriate tags
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # Plex doesn't care about the number of movies in a folder
    # But Radarr does, so don't do it
    cnt_movies = 0
    cnt_extras = 0

    for sub_path in glob(str(P_movie_dir / "**/*"), recursive=True):
        print(f"🔎 Checking 👉 {sub_path}")
        P_sub = Path(sub_path)
        # Skip anything not a file
        if not P_sub.is_file():
            print(f"🛑 {P_sub.name} 👉 Not a file")
            continue
        # Skip files that should be ignored (copy+paste from global `.gitignore`)
        if P_sub.name in IGNORE_FILES:
            print(f"🛑 {P_sub.name} 👉 Ignored")
            continue
        # Skip if it's not a movie
        if not P_sub.suffix.lower() in MOVIE_SUFFIXES:
            continue
        else:
            cnt_movies += 1
        for tag, [stem_suffix, parent_dir_name] in HAS_EXTRAS_TAGS.items():
            if is_extra(P_movie_dir, P_sub, stem_suffix, parent_dir_name):
                cnt_extras += 1
                add_tag(tag, file=P_movie_dir)
                print(f"〘{tag.name}〛👉 {P_movie_dir.name}")
                continue

    cnt_movies_not_extras = cnt_movies - cnt_extras

    if 0 == cnt_movies_not_extras:
        add_tag(TAG_HAS_NO_MOVIES, file=P_movie_dir)
    elif 1 < cnt_movies_not_extras:
        add_tag(TAG_HAS_MULTIPLE_MOVIES, file=P_movie_dir)
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
