# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# CBZ from Folder
#
# External Dependencies:
#   - https://pypi.org/project/macos-tags/
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

import os
import shutil
import sys
import zipfile
from pathlib import Path

from macos_tags import Color, Tag
from macos_tags import add as add_tag

args = sys.argv[1:]


for arg in args:

    src = Path(arg)

    print(f"Checking is directory {src}")

    # Skip if not a directory
    if not src.is_dir():
        continue

    print(f"Continuing with directory {src}")

    cbz = src.with_suffix(".cbz")

    print(f"Checking is existing {cbz}")

    if cbz.exists():
        add_tag(
            Tag(name="Yellow", color=Color.YELLOW),
            file=str(src),
        )
        continue

    print(f"Continuing to create {cbz}")

    with zipfile.ZipFile(
        cbz, mode="w", compression=zipfile.ZIP_STORED
    ) as archive:
        for fn in os.listdir(src):
            archive.write(src / fn, arcname=fn)

    print(f"Verifying {cbz}")

    if zipfile.is_zipfile(cbz):
        add_tag(
            Tag(name="Green", color=Color.GREEN),
            file=str(cbz),
        )
        shutil.rmtree(src)
    else:
        add_tag(
            Tag(name="Red", color=Color.RED), file=str(cbz)
        )
