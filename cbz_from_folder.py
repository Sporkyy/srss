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
from zipfile import is_zipfile

from macos_tags import Color, Tag
from macos_tags import add as add_tag

# from patoolib import create_archive, test_archive

# MARK: Tags
T_ok = Tag(
    name="Comic is ok",
    color=Color.GREEN,
)
T_bad = Tag(
    name="Comic is bad",
    color=Color.RED,
)
T_collision = Tag(
    name="File name collision",
    color=Color.YELLOW,
)

args = sys.argv[1:]

# MARK: The Loop
for arg in args:

    src = Path(arg)

    print("Esuring a directory {src}")

    # Skip if not a directory
    if not src.is_dir():
        continue

    cbz = src.with_suffix(".cbz")

    print("Ensuring no existing {cbz}")

    if cbz.exists():
        add_tag(T_collision, file=str(src))
        continue

    with zipfile.ZipFile(
        cbz,
        mode="w",
        compression=zipfile.ZIP_STORED,
    ) as archive:
        for fn in os.listdir(src):
            archive.write(src / fn, arcname=fn)

    print("Verifying {cbz}")
    if is_zipfile(cbz):
        add_tag(T_ok, file=str(cbz))
        shutil.rmtree(src)
    else:
        add_tag(T_bad, file=str(cbz))
