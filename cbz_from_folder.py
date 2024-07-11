# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# CBZ from Folder
#
# ## External Dependencies
#   * https://pypi.org/project/macos-tags/
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# MARK: Imports

import os
import shutil
import sys
import zipfile
from pathlib import Path
from zipfile import is_zipfile

from macos_tags import Color, Tag
from macos_tags import add as add_tag

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

    # Ensure a directory
    if not src_dir.is_dir():
        continue

    dst_cbz = src_dir.with_suffix(".cbz")

    # Ensure no collision
    if dst_cbz.exists():
        add_tag(T_collision, file=str(src_dir))

    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # MARK: Parity Files
    # Delete any existing Recovery (par2) records
    # subprocess.run(
    #     [
    #         "find",
    #         src_dir,
    #         "-type",
    #         "f",
    #         "-name",
    #         "*.par2",
    #         "-delete",
    #     ]
    # )

    # Create Recovery (par2) records
    # found_files = subprocess.run(
    #     [
    #         "find",
    #         src_dir,
    #         "-type",
    #         "f",
    #         "-not",
    #         "-name",
    #         ".DS_Store",
    #     ],
    #     capture_output=True,
    #     text=True,
    # )

    # subprocess.run(
    #     [
    #         "par2",
    #         "create",
    #         "-aRecovery",
    #         "-q",
    #         "-r10",
    #         "--",
    #         *found_files.stdout.split("\n"),
    #     ],
    #     cwd=src_dir,
    #     capture_output=True,
    #     text=True,
    # )
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    with zipfile.ZipFile(
        dst_cbz,
        mode="w",
        compression=zipfile.ZIP_STORED,
    ) as archive:
        for start, _, files in os.walk(src_dir):
            for file in files:
                file = Path(file)
                if file.name in [".DS_Store"]:
                    continue
                file_path = os.path.join(start, file)
                arcname = os.path.relpath(file_path, src_dir)
                archive.write(file_path, arcname)

    if is_zipfile(dst_cbz):
        add_tag(T_ok, file=str(dst_cbz))
        shutil.rmtree(src_dir)
    else:
        print(f"Invalid {dst_cbz}")
        add_tag(T_bad, file=str(dst_cbz))
