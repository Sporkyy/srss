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
from pathlib import Path
from sys import argv

from macos_tags import Color, Tag
from macos_tags import add as add_tag
from macos_tags import get_all as get_all_tags
from macos_tags import remove as remove_tag

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

# TODO: Find if ther is an official list of movie suffixes for Plex
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


# MARK: Tags

BLUE, RED = itemgetter("BLUE", "RED")(Color)

# These tags go on the movie folder
# e.g. `The Matrix (1999) {imdb-tt0133093}`

# Tags based on the number of movies in the folder
T_HAS_NO_MOVIE = Tag(name="Has no movies", color=RED)
T_HAS_MULTIPLE_MOVIES = Tag(name="Has multiple movies", color=RED)
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


def is_movie(path: Path) -> bool:
    return path.suffix.lower() in MOVIE_SUFFIXES


# def is_behind_the_scenes(path: Path, sub_path: Path) -> bool:
#     if not is_movie(sub_path):
#         return False
#     elif sub_path.stem.lower().endswith(
#         "-behindthescenes"
#     ) and sub_path.parent.samefile(path):
#         return True
#     elif (
#         path.parent.name.lower() == "behind the scenes"
#         and sub_path.parent.parent.samefile(path)
#     ):
#         return True
#     else:
#         return False


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


# def is_deleted_scene(path: Path, sub_path: Path) -> bool:
#     if not is_movie(sub_path):
#         return False
#     return is_movie(path) and (
#         path.stem.lower().endswith("-deletedscene")
#         or path.parent.name.lower() == "deleted scenes"
#     )


# def is_interview(path: Path, sub_path: Path) -> bool:
#     if not is_movie(sub_path):
#         return False
#     return is_movie(path) and (
#         path.stem.lower().endswith("-interview")
#         or path.parent.name.lower() == "interviews"
#     )


# def is_featurette(path: Path, sub_path: Path) -> bool:
#     if not is_movie(sub_path):
#         return False
#     return is_movie(path) and (
#         path.stem.lower().endswith("-featurette")
#         or path.parent.name.lower() == "featurettes"
#     )


# def is_other(path: Path, sub_path: Path) -> bool:
#     if not is_movie(sub_path):
#         return False
#     return is_movie(path) and (
#         path.stem.lower().endswith("-other") or path.parent.name.lower() == "other"
#     )


# def is_scene(path: Path, sub_path: Path) -> bool:
#     if not is_movie(sub_path):
#         return False
#     return is_movie(path) and (
#         path.stem.lower().endswith("-scene") or path.parent.name.lower() == "scenes"
#     )


# def is_short(path: Path, sub_path: Path) -> bool:
#     if not is_movie(sub_path):
#         return False
#     return is_movie(path) and (
#         path.stem.lower().endswith("-short") or path.parent.name.lower() == "shorts"
#     )


# def is_trailer(path: Path, sub_path: Path) -> bool:
#     if not is_movie(sub_path):
#         return False
#     return is_movie(path) and (
#         path.stem.lower().endswith("-trailer") or path.parent.name.lower() == "trailers"
#     )


# def is_image(path: Path, sub_path: Path) -> bool:
#     return path.suffix.lower() in IMAGE_SUFFIXES


# TODO: There are multiple names for the poster image; gotta collect them all!
# def is_poster(path: Path, sub_path: Path) -> bool:
#     return path.stem.lower() == "poster"


# MARK: The Loop
for arg in argv[1:]:

    path = Path(arg)

    # Ensure a directory
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if not path.is_dir():
        print(f"🛑 {path.name} 👉 Not a directory")
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # 🏷️ Remove existing tags
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    for tag in get_all_tags(file=str(path)):
        if tag in [
            *HAS_EXTRAS_TAGS,
            T_HAS_NO_MOVIE,
            T_HAS_MULTIPLE_MOVIES,
        ]:
            remove_tag(tag, file=str(path))
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # 📁 Loop through the directory and determine the appropriate tags
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # Plex doesn't care about the number of movies in a folder
    # But Radarr does and I do too (I try to avoid multiple movies in a folder)
    cnt_non_extras_movies = 0

    for str_sub in glob(str(path / "**/*"), recursive=True):
        print(f"🔎 Checking 👉 {str_sub}")
        sub_path = Path(str_sub)
        # Skip anything not a file
        if not sub_path.is_file():
            print(f"🛑 {sub_path.name} 👉 Not a file")
            continue
        # Skip files that should be ignored (copy+paste from global `.gitignore`)
        if sub_path.name in IGNORE_FILES:
            print(f"🛑 {sub_path.name} 👉 Ignored")
            continue
        for tag, [suffix, dir_name] in HAS_EXTRAS_TAGS.items():
            if is_extra(path, sub_path, suffix, dir_name):
                add_tag(tag, file=str(path))
                print(f"〘{tag.name}〛👉 {path.name}")
                continue
        if is_movie(sub_path):
            cnt_non_extras_movies += 1
        else:
            print(f"⚠️ {sub_path.name} 👉 Not a movie")

    if 0 == cnt_non_extras_movies:
        add_tag(T_HAS_NO_MOVIE, file=str(path))
    elif 1 < cnt_non_extras_movies:
        add_tag(T_HAS_MULTIPLE_MOVIES, file=str(path))
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # if is_behind_the_scenes(path, sub_path):
    #     has_behind_the_scenes = True
    # elif is_deleted_scene(path, sub_path):
    #     has_deleted_scenes = True
    # elif is_featurette(path, sub_path):
    #     has_featurettes = True
    # elif is_interview(path, sub_path):
    #     has_interviews = True
    # elif is_other(path, sub_path):
    #     has_other = True
    # elif is_scene(path, sub_path):
    #     has_scenes = True
    # elif is_short(path, sub_path):
    #     has_shorts = True
    # elif is_trailer(path, sub_path):
    #     has_trailers = True
    # elif is_movie(path, sub_path):
    #     cnt_non_extras_movies += 1

    # if is_image(sub_path):
    #     has_poster = True
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
