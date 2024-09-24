# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Comic: Rename from vXX to 0XX
#
# This script is for performing the common comic book renaming operation of changing the
# volume number to a Mylar-compatible three-digit issue number. An operation most
# commonly performed on manga volumes.
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# MARK: Imports

import os
import re
import sys
from pathlib import Path

args = sys.argv[1:]

# MARK: The Loop

for arg in args:
    src = Path(arg)

    if not src.is_file():
        print(f"Not a file {src}")
        continue

    if src.suffix.lower() not in [".cbz", ".cbr"]:
        print(f"Not a comic {src}")
        continue

    dst = src

    dst = dst.with_stem(re.sub(r"\bv(\d{2})\b", r"0\1", dst.stem))

    if src != dst:
        print(f"Renaming {src} to {dst}")
        os.rename(src, dst)
    else:
        print(f"Skipping {src}")
