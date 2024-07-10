# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# https://pypi.org/project/macos-tags/
# Rarfile
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# MARK: Imports

import os
import shutil
import sys
import tempfile
import zipfile
from operator import is_
from pathlib import Path, PurePath
from zipfile import ZipFile

import rarfile
from macos_tags import Color, Tag
from macos_tags import add as add_tag
from macos_tags import remove as remove_tag
from rarfile import RarFile

# MARK: Homebrew PATH
os.environ["PATH"] += os.pathsep + "/usr/local/bin"
os.environ["PATH"] += os.pathsep + "/opt/homebrew/bin"
os.environ["PATH"] += os.pathsep + "/opt/homebrew/sbin"


# MARK: Functions
def tag_bad(file: os.PathLike):
    remove_tag(T_ok, file=str(src))
    add_tag(T_bad, file=str(src))


def tag_ok(file: os.PathLike):
    remove_tag(T_bad, file=str(src))
    add_tag(T_ok, file=str(src))


def tag_collision(file: os.PathLike):
    remove_tag(T_ok, file=str(src))
    add_tag(T_collision, file=str(src))


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

    # Ensure the extension is lowercase
    if src.suffix.lower() != src.suffix:
        print(f"Downcasing {src.suffix}")
        dst = src.with_suffix(src.suffix.lower())
        os.rename(src, dst)
        src = dst

    # Skip if not a comic book archive
    if not src.suffix in [".cbz", ".cbr"]:
        print(f"Not a comic {src.stem}")
        continue

    is_zipfile = zipfile.is_zipfile(src)
    is_rarfile = rarfile.is_rarfile(src)

    if not is_zipfile and not is_rarfile:
        print(f"Invalid archive {src.stem}")
        tag_bad(src)
        continue

    # Fix the extension
    if ".rar" == src.suffix and is_zipfile:
        print(f"Fixing {src.suffix} extension {src.stem}")
        dest = src.with_suffix(".cbz")
        os.rename(src, dest)
        src = dest
    elif ".zip" == src.suffix and is_rarfile:
        print(f"Fixing {src.suffix} extension {src.stem}")
        dest = src.with_suffix(".cbr")
        os.rename(src, dest)
        src = dest

    # Repack CBRs
    if ".cbr" == src.suffix:
        cbz = src.with_suffix(".cbz")
        if os.path.exists(cbz):
            tag_collision(src)
            continue
        tmp = tempfile.mkdtemp(prefix="cbz_from_cbr_")
        PP_tmp = PurePath(tmp)
        with RarFile(src, "r") as archive:
            archive.extractall(tmp)
        with ZipFile(
            cbz, "w", zipfile.ZIP_STORED
        ) as archive:
            for root, _, files in os.walk(src):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(
                        file_path, src
                    )
                    archive.write(file_path, arcname)
        shutil.rmtree(tmp)
        is_zipfile = zipfile.is_zipfile(cbz)
        if is_zipfile:
            os.remove(src)
            src = cbz
        else:
            tag_bad(cbz)
            continue

    # Tag the comic as ok
    if is_zipfile:
        tag_ok(src)
    else:
        tag_bad(src)
