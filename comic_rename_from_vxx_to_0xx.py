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

# MARK: Constants

RE_VOL_NUM = re.compile(r"\bv(\d{2,})\b")
RE_NO_VOL = re.compile(r"\b(\d{2,})\b")


# MARK: The Loop
args = sys.argv[1:]

for arg in args:
    src = Path(arg)

    # Skip if not a file
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if not src.is_file():
        print(f"🛑 Not a file 👉 {src.name}")
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Skip if not a comic
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if src.suffix.lower() not in [".cbz", ".cbr"]:
        print(f"🛑 Not a comic 👉 {src.name}")
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    dst = src

    g = re.search(RE_VOL_NUM, src.stem)
    if g:
        # dst = dst.with_stem(re.sub(RE_VOL_NUM, r"0\1", dst))
    else:
        g = re.search(RE_NO_VOL, src.stem):
        # dst = dst.with_stem(re.sub(RE_NO_VOL, r"0\1", dst.stem))

    # dst = dst.with_stem(re.sub(RE_VOL_NUM, r"0\1", dst.stem))

    if src != dst:
        print(f"⬇️ 👉 {src.name}")
        print(f"⬆️ 👉 {dst.name}")
        os.rename(src, dst)
    else:
        print(f"⏩ Skipping 👉 {src}")
