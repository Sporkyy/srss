# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# CBZ from Folder
#
# ## External Dependencies
#   * https://pypi.org/project/macos-tags/
#   * https://pypi.org/patool/
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# MARK: Imports

import os
import shutil
import subprocess
import sys
from pathlib import Path
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
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Ensure no collision
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if dst_cbz.exists():
        add_tag(T_collision, file=str(src_dir))
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # MARK: Add Parity Files
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # Delete any existing Recovery (par2) records
    subprocess.run(
        [
            "find",
            src_dir,
            "-type",
            "f",
            "-name",
            "*.par2",
            "-delete",
        ]
    )

    # Find files to protect
    find_output = subprocess.run(
        [
            "find",
            src_dir,
            "-type",
            "f",
        ],
        capture_output=True,
        text=True,
    )

    # Create Recovery (par2) records
    part2_output = subprocess.run(
        [
            "par2",
            "create",
            "-aRecovery",
            "-q",
            "-r10",
            "--",
            *find_output.stdout.split("\n"),
        ],
        cwd=src_dir,
    )
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    try:
        os.chdir(src_dir.parent)
        create_archive(str(dst_cbz.name), [str(src_dir.name)])
        if is_zipfile(dst_cbz):
            print(f"✅ CBZ OK {dst_cbz}")
            add_tag(T_ok, file=str(dst_cbz))
            shutil.rmtree(src_dir)
        else:
            print(f"🛑 CBZ Invalid {dst_cbz}")
            add_tag(T_bad, file=str(dst_cbz))
    except Exception as e:
        print(f"❗️ Error: {e}")
        add_tag(T_bad, file=str(dst_cbz))
        if dst_cbz.exists():
            os.remove(dst_cbz)
