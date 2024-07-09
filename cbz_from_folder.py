# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# CBZ from Folder
#
# External Dependencies:
#   - https://pypi.org/project/macos-tags/
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# MARK: Imports
import os
import shutil
import subprocess
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

    # Ensure a directory
    if not src.is_dir():
        continue

    cbz = src.with_suffix(".cbz")

    # Ensure no collision
    if cbz.exists():
        add_tag(T_collision, file=str(src))
        continue

    # Add in the parity files
    # par2 c -t0 -r10 -d./ -- Recovery.par2
    # set -l recovery_path "$temp_dir_recovery/Recovery.par2"
    # set -l file_list (find "$temp_dir_recovery" -type f | gshuf)
    # par2 c -B"$temp_dir_recovery" -r10 -q "$recovery_path" $file_list
    # recovery_path = src / "Recovery.par2"
    # file_list = []
    # for root, _, files in os.walk(src):
    #     for file in files:
    #         file_list.append(os.path.join(root, file))
    # print(" ".join([f'"{fn}"' for fn in file_list]))
    # os.system(
    #     f"par2 c -B\"{src}\" -r10 -q \"{recovery_path}\" {' '.join(file_list)}"
    # )
    # x = [
    #     "par2",
    #     "c",
    #     f'-B"{src}"',
    #     "-r10",
    #     "-q",
    #     f'"{recovery_path}"',
    # ].extend([f'"{fn}"' for fn in file_list])
    # print(x)
    # # subprocess.Popen(x)
    # continue

    with zipfile.ZipFile(
        cbz,
        mode="w",
        compression=zipfile.ZIP_STORED,
    ) as archive:
        for root, _, files in os.walk(src):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, src)
                archive.write(file_path, arcname)

    if is_zipfile(cbz):
        add_tag(T_ok, file=str(cbz))
        shutil.rmtree(src)
    else:
        print(f"Invalid {cbz}")
        add_tag(T_bad, file=str(cbz))
