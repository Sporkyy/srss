# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# CBZ from Folder
#
# ## External Dependencies
#   * https://pypi.org/project/macos-tags/
#   * https://pypi.org/patool/
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# MARK: Imports

import shutil
import sys
from os import chdir, remove
from os.path import relpath
from pathlib import Path
from subprocess import run
from zipfile import is_zipfile

from macos_tags import Color, Tag
from macos_tags import add as add_tag
from patoolib import create_archive

# import subprocess
# from pprint import pprint


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

    src_dir = Path(arg)
    dst_cbz = src_dir.with_suffix(".cbz")

    # Ensure a directory
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if not src_dir.is_dir():
        print(f"🛑 Not a directory {src_dir.name}")
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Ensure no collision
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if dst_cbz.exists():
        print(f"🛑 Existing {dst_cbz.name}")
        add_tag(T_collision, file=str(src_dir))
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    try:
        src_files = run(
            [
                "find",
                src_dir,
                "-type",
                "f",
            ],
            capture_output=True,
            text=True,
        )
        chdir(src_dir.parent)
        create_archive(
            str(dst_cbz.name),
            [relpath(fn, src_dir.parent) for fn in src_files.stdout.splitlines()],
        )
        if is_zipfile(dst_cbz):
            print(f"✅ CBZ OK {dst_cbz.name}")
            add_tag(T_ok, file=str(dst_cbz))
            shutil.rmtree(src_dir)
        else:
            print(f"🛑 CBZ Invalid {dst_cbz.name}")
            add_tag(T_bad, file=str(dst_cbz))
    except Exception as e:
        print(f"❗️ Error: {e}")
        add_tag(T_bad, file=str(dst_cbz))
        if dst_cbz.exists():
            remove(dst_cbz)
