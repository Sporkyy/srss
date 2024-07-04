# https://pypi.org/project/titlecase/

import os
import sys
from pathlib import PurePath

from titlecase import titlecase

args = sys.argv[1:]

for arg in args:
    src = PurePath(arg)
    dst = src.with_stem(titlecase(src.stem))
    if src != dst:
        print(f"Renaming {src} to {dst}")
        os.rename(src, dst)
    else:
        print(f"Skipping {src}")
