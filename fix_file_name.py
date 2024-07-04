# https://pypi.org/project/titlecase/

import os
import re
import sys
from pathlib import PurePath

from titlecase import titlecase

args = sys.argv[1:]

for arg in args:
    src = PurePath(arg)
    fixed_stem = re.sub(
        r"\b\W+\b", " ", titlecase(src.stem)
    )
    fixed_suffix = str.lower(src.suffix)
    dst = src.with_stem(fixed_stem).with_suffix(
        fixed_suffix
    )
    if src != dst:
        print(f"Renaming {src} to {dst}")
        os.rename(src, dst)
    else:
        print(f"Skipping {src}")
