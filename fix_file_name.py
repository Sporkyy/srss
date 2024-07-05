# https://pypi.org/project/titlecase/

import os
import re
import sys
from pathlib import PurePath

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
    src = PurePath(arg)
    dst = src

    # Ensure there is whitespace somewhere
    if 0 == str.count(src.stem, " "):
        probable_spaces = re.sub(r"[^-_\.]", "", src.stem)
        if 0 < str.count(probable_spaces):
            probable_space = most_frequent_char(
                probable_spaces
            )
            dst = src.with_stem(
                src.stem.replace(probable_space, " ")
            )

    # Remove multiple spaces
    dst = dst.with_stem(re.sub(r"\s{2,}", " ", dst.stem))

    # Should probably be titlecase
    dst = dst.with_stem(titlecase(dst.stem))

    # Ensure the extension is lowercase
    dst = dst.with_suffix(dst.suffix.lower())

    # Remove leading and trailing whitespace
    dst = str.strip(dst)

    if src != dst:
        print(f"Renaming {src} to {dst}")
        os.rename(src, dst)
    else:
        print(f"Skipping {src}")
