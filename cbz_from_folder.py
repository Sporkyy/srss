# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# CBZ from Folder
#
# External Dependencies:
#   - https://pypi.org/project/macos-tags/
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# MARK: Imports

import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from zipfile import is_zipfile

from macos_tags import Color, Tag
from macos_tags import add as add_tag

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

    # MARK: Parity Files

    # Add in the parity files
    # par2 c -t0 -r10 -d./ -- Recovery.par2
    # set -l recovery_path "$temp_dir_recovery/Recovery.par2"
    # set -l file_list (find "$temp_dir_recovery" -type f | gshuf)
    # par2 c -B"$temp_dir_recovery" -r10 -q "$recovery_path" $file_list
    # P_recovery = os.path.join(src_dir, "Recovery.par2")
    # file_list = []
    # print(P_recovery)
    # for start, _, files in os.walk(src_dir):
    #     for file in files:
    #         file = Path(file)
    #         if file.name in [".DS_Store"]:
    #             continue
    #         file_list.append(os.path.join(start, file))
    # print(file_list)
    # print(" ".join([f'"{json.dumps(fn)}"' for fn in file_list]))
    # print(" ".join([json.dumps(fn) for fn in file_list]))
    # os.system(
    #     f"par2 c -B\"{src}\" -r10 -q \"{recovery_path}\" {' '.join(file_list)}"
    # )
    # x = [
    #     "par2",
    #     "create",
    #     f'-B"{src_dir}"',
    #     "-r10",
    #     # "-q", # Quiet
    #     "-v",  # Verbose
    #     # "Recovery.par2",
    #     f'{os.path.join(src_dir, "Recovery.par2")}',
    #     "--",
    #     # "(find . -type f | gshuf)",
    # ]
    # x.extend([f'"{fn}"' for fn in file_list])
    # print(" ".join(x))
    # subprocess.Popen(x)
    # subprocess.check_call(x)
    # os.chdir(src_dir)
    # print(subprocess.run("pwd"))
    # print(subprocess.run(["par2", "-VV"]))
    # subprocess.run(" ".join(x))
    # subprocess.run(x)
    # continue

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
