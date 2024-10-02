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

args = sys.argv[1:]

# Sort the arguments in reverse order so deeper paths are processed first
args.sort(reverse=True)

# MARK: The Loop
for arg in args:
    src = Path(arg)
    dst = src

    if src.is_file():
        dst = dst.with_stem(dst.stem.replace(".", " "))
        dst = dst.with_stem(re.sub(r"\s{2,}", " ", dst.stem))
        dst = dst.with_stem(titlecase(dst.stem))
        dst = dst.with_stem(dst.stem.strip())
    else:
        dst = dst.with_name(dst.name.replace(".", " "))
        dst = dst.with_name(re.sub(r"\s{2,}", " ", dst.name))
        dst = dst.with_name(titlecase(dst.name))
        dst = dst.with_name(dst.name.strip())

    if src != dst:
        print(f'Renaming "{src.name}" to "{dst.name}"')
        os.rename(src, dst)
    else:
        print(f'Skipping "{src.name}"')
