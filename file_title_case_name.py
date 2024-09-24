# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# File: Title Case Name
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

    # Decided against support for multiple suffixes after testing
    if src.is_file():
        dst_main = dst.stem
        print(f'File main "{dst_main}"')
    else:
        dst_main = dst.name
        print(f'Dir main "{dst_main}"')

    # Files with words delimited by dots outnumber files with multiple extensions
    if not " " in dst_main:
        print(f'No spaces "{dst_main}"')
        if re.search(r"[0-9a-z]_[0-9a-z]", dst_main, re.IGNORECASE):
            dst_main = dst_main.replace("_", " ")
        elif re.search(r"[0-9a-z]\.[0-9a-z]", dst_main, re.IGNORECASE):
            dst_main = dst_main.replace(".", " ")
        elif re.search(r"[0-9a-z]-[0-9a-z]", dst_main, re.IGNORECASE):
            dst_main = dst_main.replace("-", " ")

    # Remove multiple subsequent spaces
    dst_main = re.sub(r"\s{2,}", " ", dst_main)

    # It should probably be titlecase
    dst_main = titlecase(dst_main)

    # Ensure no whitespace at the beginning or end
    dst_main = dst_main.strip()

    # Recalculate the destination path after the changes above
    if src.is_file():
        dst = dst.with_stem(dst_main)
    else:
        dst = dst.with_name(dst_main)

    if src != dst:
        print(f'Renaming "{src.name}" to "{dst.name}"')
        os.rename(src, dst)
    else:
        print(f'Skipping "{src.name}"')
