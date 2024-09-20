# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Tag Mylar Series Folder
#
# ## Extras Directories
#   * `behind the scenes`
#   * `deleted scenes`
#   * `featurettes`
#   * `interviews`
#   * `other`
#   * `scenes`
#   * `shorts`
#   * `trailers
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

# MARK: Tags
T_has_no_movie = Tag(name="Has no movie", color=Color.RED)
T_has_multiple_movies = Tag(name="Has multiple movies", color=Color.RED)
T_has_behind_the_scenes = Tag(name="Has 'Behind the Scenes'", color=Color.BLUE)
T_has_deleted_scenes = Tag(name="Has 'Deleted Scenes'", color=Color.BLUE)
T_has_featurettes = Tag(name="Has 'Featurettes'", color=Color.BLUE)
T_has_interviews = Tag(name="Has 'Interviews'", color=Color.BLUE)
T_has_other = Tag(name="Has 'Other'", color=Color.BLUE)
T_has_scenes = Tag(name="has 'Scenes'", color=Color.BLUE)
T_has_shorts = Tag(name="has 'Shorts'", color=Color.BLUE)
T_has_trailers = Tag(name="has 'Trailers'", color=Color.BLUE)


# MARK: Functions
def is_movie(file: Path) -> bool:
    if not file.is_file():
        return False
    fn_suffix = file.suffix.lower()
    movie_suffixes = [".avi", ".m4v", ".mkv", ".mov", ".mp4", ".mpg", ".mpeg", ".webm"]
    return fn_suffix in movie_suffixes


def dir_has_movie(dir: Path) -> bool:
    if not dir.is_dir():
        return False
    for fn in os.listdir(dir):
        P_fn = Path(fn)
        if is_movie(P_fn):
            return True
    return False


args = sys.argv[1:]

# MARK: The Loop
for arg in args:

    P_arg = Path(arg)

    # Skip if not a directory
    if not P_arg.is_dir():
        continue

    cnt_movies = 0
    is_found_behind_the_scenes = False
    is_found_deleted_scenes = False
    is_found_featurettes = False
    is_found_interviews = False
    is_found_other = False
    is_found_scenes = False
    is_found_shorts = False
    is_found_trailers = False

    for fn in os.listdir(P_arg):
        P_fn = Path(fn)
        if is_movie(P_fn):
            cnt_movies += 1
        elif dir_has_movie(P_fn):
            if "behind the scenes" == P_fn.stem.lower():
                is_found_behind_the_scenes = True
            elif "deleted scenes" == P_fn.stem.lower():
                is_found_deleted_scenes = True
            elif "featurettes" == P_fn.stem.lower():
                is_found_featurettes = True
            elif "interviews" == P_fn.stem.lower():
                is_found_interviews = True
            elif "other" == P_fn.stem.lower():
                is_found_other = True
            elif "scenes" == P_fn.stem.lower():
                is_found_scenes = True
            elif "shorts" == P_fn.stem.lower():
                is_found_shorts = True
            elif "trailers" == P_fn.stem.lower():
                is_found_trailers = True

    remove_all_tags(file=arg)

    if 0 == cnt_movies:
        add_tag(T_has_no_movie, file=arg)
    elif 1 < cnt_movies:
        add_tag(T_has_multiple_movies, file=arg)

    if is_found_behind_the_scenes:
        add_tag(T_has_behind_the_scenes, file=arg)
    if is_found_deleted_scenes:
        add_tag(T_has_deleted_scenes, file=arg)
    if is_found_featurettes:
        add_tag(T_has_featurettes, file=arg)
    if is_found_interviews:
        add_tag(T_has_interviews, file=arg)
    if is_found_other:
        add_tag(T_has_other, file=arg)
    if is_found_scenes:
        add_tag(T_has_scenes, file=arg)
    if is_found_shorts:
        add_tag(T_has_shorts, file=arg)
    if is_found_trailers:
        add_tag(T_has_trailers, file=arg)
