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
T_HAS_NO_MOVIES = Tag(name="Has no movies", color=RED)
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


def has_movie_suffix(path: Path) -> bool:
    return path.suffix.lower() in MOVIE_SUFFIXES


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

    P_movie = Path(arg)

    # Ensure a directory
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if not P_movie.is_dir():
        print(f"🛑 {P_movie.name} 👉 Not a directory")
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # 🏷️ Remove existing tags
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    for tag in get_all_tags(file=str(P_movie)):
        if tag in [
            *HAS_EXTRAS_TAGS.keys(),
            T_HAS_NO_MOVIES,
            T_HAS_MULTIPLE_MOVIES,
        ]:
            remove_tag(tag, file=str(P_movie))
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # 📁 Loop through the directory and determine the appropriate tags
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # Plex doesn't care about the number of movies in a folder
    # But Radarr does and I do too (I try to avoid multiple movies in a folder)
    cnt_movies = 0
    cnt_extras = 0

    for sub in glob(str(P_movie / "**/*"), recursive=True):
        print(f"🔎 Checking 👉 {sub}")
        P_sub = Path(sub)
        # Skip anything not a file
        if not P_sub.is_file():
            print(f"🛑 {P_sub.name} 👉 Not a file")
            continue
        # Skip files that should be ignored (copy+paste from global `.gitignore`)
        if P_sub.name in IGNORE_FILES:
            print(f"🛑 {P_sub.name} 👉 Ignored")
            continue
        # Skip if it's not a movie
        if not has_movie_suffix(P_sub):
            continue
        else:
            cnt_movies += 1
        for tag, [stem_suffix, parent_dir_name] in HAS_EXTRAS_TAGS.items():
            if is_extra(P_movie, P_sub, stem_suffix, parent_dir_name):
                cnt_extras += 1
                add_tag(tag, file=str(P_movie))
                print(f"〘{tag.name}〛👉 {P_movie.name}")
                continue

    cnt_movies_not_extras = cnt_movies - cnt_extras

    if 0 == cnt_movies_not_extras:
        add_tag(T_HAS_NO_MOVIES, file=str(P_movie))
    elif 1 < cnt_movies_not_extras:
        add_tag(T_HAS_MULTIPLE_MOVIES, file=str(P_movie))
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
