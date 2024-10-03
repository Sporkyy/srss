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
from macos_tags import remove as remove_tag

# MARK: Constants

# https://github.com/github/gitignore/blob/main/Global/macOS.gitignore
IGNORE_FILES = [
    ".DS_Store",
    ".AppleDouble",
    ".LSOverride",
]

# TODO: Find if ther is an official list of image suffixes for Plex
IMAGE_SUFFIXES = [".jpg", ".jpeg", ".png", ".tiff", ".webp"]

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

EXTRAS_SUFFIXES = [
    "-behindthescenes",
    "-deleted",
    "-featurette",
    "-interview",
    "-other",
    "-scene",
    "-short",
    "-trailer",
]

EXTRAS_DIRECTORIES = [
    "behind the scenes",
    "deleted scenes",
    "featurettes",
    "interviews",
    "other",
    "scenes",
    "shorts",
    "trailers",
]

BLUE, RED = itemgetter("BLUE", "RED")(Color)

# MARK: Tags

# These tags go on the movie folder
# e.g. `The Matrix (1999) {imdb-tt0133093}`

# Tags based on the number of movies in the folder
T_HAS_NO_MOVIE = Tag(name="Has no movies", color=RED)
T_HAS_MULTIPLE_MOVIES = Tag(name="Has multiple movies", color=RED)
# Tags based on the presence of Plex extras
T_HAS_BEHIND_THE_SCENES = Tag(name="Has behind the scenes", color=BLUE)
T_HAS_DELETED_SCENES = Tag(name="Has deleted scenes", color=BLUE)
T_HAS_FEATURETTES = Tag(name="Has featurettes", color=BLUE)
T_HAS_INTERVIEWS = Tag(name="Has interviews", color=BLUE)
T_HAS_OTHER = Tag(name="Has other", color=BLUE)
T_HAS_SCENES = Tag(name="Has scenes", color=BLUE)
T_HAS_SHORTS = Tag(name="Has shorts", color=BLUE)
T_HAS_TRAILERS = Tag(name="Has trailers", color=BLUE)


# MARK: Functions


def is_movie(path: Path) -> bool:
    return path.suffix.lower() in MOVIE_SUFFIXES


def is_behind_the_scenes(path: Path) -> bool:
    return is_movie(path) and (
        path.stem.lower().endswith("-behindthescenes")
        or path.parent.name.lower() == "behind the scenes"
    )


def is_deleted_scene(path: Path) -> bool:
    return is_movie(path) and (
        path.stem.lower().endswith("-deletedscene")
        or path.parent.name.lower() == "deleted scenes"
    )


def is_interview(path: Path) -> bool:
    return is_movie(path) and (
        path.stem.lower().endswith("-interview")
        or path.parent.name.lower() == "interviews"
    )


def is_featurette(path: Path) -> bool:
    return is_movie(path) and (
        path.stem.lower().endswith("-featurette")
        or path.parent.name.lower() == "featurettes"
    )


def is_other(path: Path) -> bool:
    return is_movie(path) and (
        path.stem.lower().endswith("-other") or path.parent.name.lower() == "other"
    )


def is_scene(path: Path) -> bool:
    return is_movie(path) and (
        path.stem.lower().endswith("-scene") or path.parent.name.lower() == "scenes"
    )


def is_short(path: Path) -> bool:
    return is_movie(path) and (
        path.stem.lower().endswith("-short") or path.parent.name.lower() == "shorts"
    )


def is_trailer(path: Path) -> bool:
    return is_movie(path) and (
        path.stem.lower().endswith("-trailer") or path.parent.name.lower() == "trailers"
    )


def is_image(path: Path) -> bool:
    return path.suffix.lower() in IMAGE_SUFFIXES


# TODO: There are multiple names for the poster image; gotta collect them all!
def is_poster(path: Path) -> bool:
    return path.stem.lower() == "poster"


# MARK: The Loop
for str_movie_dir in argv[1:]:

    print(f"Checking {str_movie_dir}")

    path_movie_dir = Path(str_movie_dir)

    # Skip if not a directory
    if not path_movie_dir.is_dir():
        continue

    # Flags for the tags for this movie folder if a Plex extra is found
    has_behind_the_scenes = False
    has_deleted_scenes = False
    has_featurettes = False
    has_interviews = False
    has_other = False
    has_scenes = False
    has_shorts = False
    has_trailers = False

    # Plex doesn't care about the number of movies in a folder
    # But Radarr does and I do too (I try to avoid multiple movies in a folder)
    cnt_non_extras_movies = 0

    # For images
    has_poster = False

    for str_sub in glob(str(path_movie_dir / "**/*"), recursive=True):
        print(f"↳ Checking {str_sub}")
        sub_path = Path(str_sub)
        if sub_path.name in IGNORE_FILES:
            continue
        if is_movie(sub_path):
            if is_behind_the_scenes(sub_path):
                has_behind_the_scenes = True
            elif is_deleted_scene(sub_path):
                has_deleted_scenes = True
            elif is_featurette(sub_path):
                has_featurettes = True
            elif is_interview(sub_path):
                has_interviews = True
            elif is_other(sub_path):
                has_other = True
            elif is_scene(sub_path):
                has_scenes = True
            elif is_short(sub_path):
                has_shorts = True
            elif is_trailer(sub_path):
                has_trailers = True
            else:
                cnt_non_extras_movies += 1
        if is_image(sub_path):
            has_poster = True

    if has_behind_the_scenes:
        add_tag(T_HAS_BEHIND_THE_SCENES, file=str(path_movie_dir))
    else:
        remove_tag(T_HAS_BEHIND_THE_SCENES, file=str(path_movie_dir))

    if has_deleted_scenes:
        add_tag(T_HAS_DELETED_SCENES, file=str(path_movie_dir))
    else:
        remove_tag(T_HAS_DELETED_SCENES, file=str(path_movie_dir))

    if has_featurettes:
        add_tag(T_HAS_FEATURETTES, file=str(path_movie_dir))
    else:
        remove_tag(T_HAS_FEATURETTES, file=str(path_movie_dir))

    if has_interviews:
        add_tag(T_HAS_INTERVIEWS, file=str(path_movie_dir))
    else:
        remove_tag(T_HAS_INTERVIEWS, file=str(path_movie_dir))

    if has_other:
        add_tag(T_HAS_OTHER, file=str(path_movie_dir))
    else:
        remove_tag(T_HAS_OTHER, file=str(path_movie_dir))

    if has_scenes:
        add_tag(T_HAS_SCENES, file=str(path_movie_dir))
    else:
        remove_tag(T_HAS_SCENES, file=str(path_movie_dir))

    if has_shorts:
        add_tag(T_HAS_SHORTS, file=str(path_movie_dir))
    else:
        remove_tag(T_HAS_SHORTS, file=str(path_movie_dir))

    if has_trailers:
        add_tag(T_HAS_TRAILERS, file=str(path_movie_dir))
    else:
        remove_tag(T_HAS_TRAILERS, file=str(path_movie_dir))

    if 0 == cnt_non_extras_movies:
        add_tag(T_HAS_NO_MOVIE, file=str(path_movie_dir))
    else:
        remove_tag(T_HAS_NO_MOVIE, file=str(path_movie_dir))

    if 1 < cnt_non_extras_movies:
        add_tag(T_HAS_MULTIPLE_MOVIES, file=str(path_movie_dir))
    else:
        remove_tag(T_HAS_MULTIPLE_MOVIES, file=str(path_movie_dir))
