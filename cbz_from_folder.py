# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# CBZ from Folder
#
# External Dependencies:
#   - https://pypi.org/project/macos-tags/
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

import os
import shutil
import sys
from pathlib import Path
from zipfile import is_zipfile

from macos_tags import Color, Tag
from macos_tags import add as _add_tag
from patoolib import create_archive


def add_tag(tag, file):
    _add_tag(tag, file=str(file))


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
        add_tag(T_collision, file=src)
        continue

    print(f"Continuing to create {cbz}")

    # with zipfile.ZipFile(
    #     cbz,
    #     mode="w",
    #     compression=zipfile.ZIP_STORED,
    # ) as archive:
    #     for fn in os.listdir(src):
    #         archive.write(src / fn, arcname=fn)

    create_archive(str(cbz), [str(src)])

    print(f"Verifying {cbz}")
    if is_zipfile(cbz):
        add_tag(T_ok, file=cbz)
        shutil.rmtree(src)
    else:
        add_tag(T_bad, file=cbz)
