# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Tag Mylar Series Folder
#
# ## External Dependencies
#   * https://pypi.org/project/macos-tags/
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

import os
import sys
from pathlib import Path, PurePath

from macos_tags import Color, Tag
from macos_tags import add as add_tag
from macos_tags import remove_all as remove_all_tags

# MARK: Tags
T_has_no_movie = Tag(name="Has no movie", color=Color.RED)
T_has_multiple_movies_in_root = Tag(name="Has multiple movies", color=Color.RED)
T_has_behind_the_scenes = Tag(name="Has 'Behind the Scenes'", color=Color.BLUE)
T_has_deleted_scenes = Tag(name="Has 'Deleted Scenes'", color=Color.BLUE)
T_has_interviews = Tag(name="Has 'Interviews'", color=Color.BLUE)
T_has_other = Tag(name="Has 'Other'", color=Color.BLUE)
T_has_scenes = Tag(name="has 'Scenes'", color=Color.BLUE)¸
T_has_shorts = Tag(name="has 'Shorts'", color=Color.BLUE)¸

movie_suffixes = [".avi", ".mp4v", ".mkv", ".mov", ".mp4", ".webm"]

args = sys.argv[1:]

def dir_has_movie(dir: Path) -> bool:
    for fn in os.listdir(dir):
        P_fn = Path(fn)
        if not P_fn.is_file():
            continue
        fn_suffix = P_fn.suffix.lower()
        if fn_suffix in movie_suffixes:
            return True
    return False

# MARK: The Loop
for arg in args:

    P_arg = Path(arg)

    # Skip if not a directory
    if not P_arg.is_dir():
        continue

    cnt_movies = 0
    is_found_behind_the_scenes = False
    is_found_deleted_scenes = False
    is_found_interviews = False
    is_found_other = False
    is_found_scenes = False
    is_found_shorts = False

    for fn in os.listdir(P_arg):
        P_fn = Path(fn)
        if P_fn.is_dir() and dir_has_movie(P_fn):
            cnt_movies += 1
        if P_fn.is_dir():
            if "behind the scenes" == fn.lower():
                is_found_behind_the_scenes = True

    # C_cnt_movies = Color.RED if 0 == cnt_movies else Color.GREEN
    # T_cnt_movies = Tag(name=f"Movie Count: {cnt_movies}", color=C_cnt_movies)
    # add_tag(T_cnt_movies, file=arg)

    # TODO: Target only specific tags for removal
    remove_all_tags(file=arg)
    if 0 == cnt_movies:
        add_tag(T_has_no_movie, file=arg)
    elif 1 < cnt_movies:
        add_tag(T_has_multiple_movies_in_root, file=arg)

    if is_found_behind_the_scenes:
        add_tag(T_has_behind_the_scenes, file=arg)