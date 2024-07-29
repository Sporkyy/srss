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
from macos_tags import remove as remove_tag

# MARK: Tags
T_has_no_movie = Tag(name="Has no movie", color=Color.RED)
T_has_multiple_movies_in_root = Tag(name="Has multiple movies", color=Color.RED)
T_has_behind_the_scenes = Tag(name="Has 'Behind the Scenes'", color=Color.BLUE)
T_has_deleted_scenes = Tag(name="Has 'Deleted Scenes'", color=Color.BLUE)
T_has_interviews = Tag(name="Has 'Interviews'", color=Color.BLUE)
T_has_other = Tag(name="Has 'Other'", color=Color.BLUE)
T_has_scenes = Tag(name="has 'Scenes'", color=Color.BLUE)¸
T_has_shorts = Tag(name="has 'Scenes'", color=Color.BLUE)¸

args = sys.argv[1:]

movie_suffixes = [".avi", ".mp4v", ".mkv", ".mov", ".mp4", ".webm"]

# MARK: The Loop
for arg in args:

    arg = Path(arg)

    # Skip if not a directory
    if not arg.is_dir():
        continue

    cnt_movies = 0
    is_found_behind_the_scenes = False
    is_found_deleted_scenes = False
    is_found_interviews = False
    is_found_other = False
    is_found_scenes = False

    for fn in os.listdir(arg):
        PP_fn = PurePath(fn)
        fn_suffix = PP_fn.suffix.lower()
        if fn_suffix in movie_suffixes:
            cnt_movies += 1

#     if not did_find_sj:
#         add_tag(T_no_sj, file=str(arg))
#     else:
#         remove_tag(T_no_sj, file=str(arg))

#     if not did_find_comic:
#         add_tag(T_no_comic, file=str(arg))
#     else:
#         remove_tag(T_no_comic, file=str(arg))