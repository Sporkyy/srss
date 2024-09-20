# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Tag Plex Music Video
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
from macos_tags import remove as remove_tag
from macos_tags import remove_all as remove_all_tags

# MARK: Tags
T_no_video_type = Tag(name="No Video Type", color=Color.RED)


# MARK: Functions
def is_movie(file: Path) -> bool:
    if not file.is_file():
        return False
    fn_suffix = file.suffix.lower()
    movie_suffixes = [".avi", ".m4v", ".mkv", ".mov", ".mp4", ".mpg", ".mpeg", ".webm"]
    return fn_suffix in movie_suffixes


def has_video_type(file: Path) -> bool:
    if not file.is_file():
        return False
    fn_stem = file.stem.lower()
    video_types = [
        "-behindthescenes",
        "-concert",
        "-interview",
        "-live",
        "-lyrics",
        "-video",
    ]
    for video_type in video_types:
        if fn_stem.endswith(video_type):
            return True
    return False


args = sys.argv[1:]

# MARK: The Loop
for arg in args:

    P_arg = Path(arg)

    # Skip if not a movie
    if not is_movie(P_arg):
        continue

    if not has_video_type(P_arg):
        add_tag(T_no_video_type, file=arg)
    else:
        remove_tag(T_no_video_type, file=arg)
