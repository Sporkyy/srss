# https://pypi.org/project/titlecase/

# MARK: Imports
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Collection

from titlecase import titlecase

args = sys.argv[1:]

# MARK: The Loop
for arg in args:
    src = Path(arg)
    dst = src

    if src.is_file():
        dst_suffixes = dst.suffixes
        dst_suffixes_len = len(str.join("", dst_suffixes))
        dst_main = dst.name[:-dst_suffixes_len]
    else:
        dst_main = dst.name

    # Ensure no existing whitespace before adding some
    if 0 == str.count(dst_main, " "):
        cans = re.sub(r"[^-_\.]", "", dst_main)
        print(f'Space Candidates "{cans}"')
        if 0 < len(cans):
            best = Counter(cans).most_common(1)[0][0]
            dst_main = dst_main.replace(best, " ")

    # Remove multiple spaces
    dst_main = re.sub(r"\s{2,}", " ", dst_main)

    # Should probably be titlecase
    dst_main = titlecase(dst_main)

    # Ensure no whitespace at the beginning or end
    dst_main = dst_main.strip()

    if src.is_file():
        dst = dst.with_stem(dst_main)
        # Ensure the extension is lowercase
        dst = dst.with_suffix("".join(dst_suffixes))
    else:
        dst = dst.with_name(dst_main)

    if src != dst:
        print(f"Renaming {src} to {dst}")
        os.rename(src, dst)
    else:
        print(f"Skipping {src}")
