# https://pypi.org/project/titlecase/

import os
import re
import sys
from pathlib import Path

from titlecase import titlecase


def cnt_chars(str):
    cnts = {}
    for char in list(str):
        if char not in cnts:
            cnts[char] = 0
        cnts[char] += 1
    return cnts


def most_frequent_char(str):
    cnts = cnt_chars(str)
    return max(cnts, key=cnts.get)


args = sys.argv[1:]

for arg in args:
    src = Path(arg)
    dst = src

    # Ensure there is whitespace somewhere
    if 0 == str.count(src.stem, " "):
        space_cans = re.sub(r"[^-_\.]", "", src.stem)
        print(space_cans)
        if 0 < len(space_cans):
            best_can = most_frequent_char(space_cans)
            dst = src.with_stem(
                str.strip(src.stem.replace(best_can, " "))
            )

    # Remove multiple spaces
    dst = dst.with_stem(re.sub(r"\s{2,}", " ", dst.stem))

    # Should probably be titlecase
    dst = dst.with_stem(titlecase(dst.stem))

    # Ensure the extension is lowercase
    dst = dst.with_suffix(dst.suffix.lower())

    if src != dst:
        print(f"Renaming {src} to {dst}")
        os.rename(src, dst)
    else:
        print(f"Skipping {src}")
