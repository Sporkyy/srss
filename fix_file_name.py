# https://pypi.org/project/titlecase/

import os
import re
import sys
from collections import Counter
from pathlib import PurePath

from titlecase import titlecase


def most_frequent_char(str: str) -> str:
    cnts = Counter(str)
    return max(cnts, key=cnts.get)


args = sys.argv[1:]

# MARK: The Loop
for arg in args:
    src = PurePath(arg)
    dst_stem = src.stem
    dst_suffix = src.suffix

    # Ensure no existing whitespace before adding some
    if 0 == str.count(dst_stem, " "):
        space_cans = re.sub(r"[^-_\.]", "", dst_stem)
        print('Space Candidates "{space_cans}"')
        if 0 < len(space_cans):
            best_can = most_frequent_char(space_cans)
            dst_stem = dst_stem.replace(best_can, " ")

    # Remove multiple spaces
    dst_stem = re.sub(r"\s{2,}", " ", dst_stem)

    # Should probably be titlecase
    dst_stem = titlecase(dst_stem)

    # Ensure no whitespace at the beginning or end
    dst_stem = dst_stem.strip()

    # Ensure the extension is lowercase
    dst_suffix = dst_suffix.lower()

    dst = src.with_name("{dst_stem}{dst_suffix}")

    if src != dst:
        print("Renaming {src} to {dst}")
        os.rename(src, dst)
    else:
        print("Skipping {src}")
