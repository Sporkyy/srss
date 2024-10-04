# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# File: Rename Download
#
# ## External Dependencies
#   * https://pypi.org/project/titlecase/
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# MARK: Imports
import os
import re
import sys
from collections import Counter
from pathlib import Path

from titlecase import titlecase

# MARK Constants

WORDS = [
    "720p",
    "HDTV",
    "DD5.1",
    "MPEG2",
]

# MARK: Functions


def get_release_group(str: str) -> str:
    m = re.match(r"-([a-zA-Z0-9]+)$", str)
    return m.group(1) if m else ""


def spiff_it_up(str: str) -> str:
    str = str.replace(".", " ")
    str = re.sub(r"\s{2,}", " ", str)
    str = titlecase(str)
    str = str.strip()
    return str


# The variable here will actually be used in this script
args = sys.argv[1:]

# Sort the arguments in reverse order so deeper paths are processed first
args.sort(reverse=True)
# See? (told you so)

# MARK: The Loop
for arg in args:
    src = Path(arg)
    dst = src

    if src.is_file():
        dst = dst.with_stem(spiff_it_up(dst.stem))
    else:
        dst = dst.with_name(spiff_it_up(dst.name))

    if src != dst:
        print(f'Renaming "{src.name}" to "{dst.name}"')
        os.rename(src, dst)
    else:
        print(f'Skipping "{src.name}"')
