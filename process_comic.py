# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Process Comic
#
# External Dependencies
#   * https://pypi.org/project/macos-tags/
#   * https://pypi.org/project/rarfile/
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# MARK: Imports

import os
import shutil
import sys
import tempfile
from pathlib import Path, PurePath
from zipfile import ZIP_STORED, ZipFile, is_zipfile

from macos_tags import Color, Tag
from macos_tags import add as add_tag
from macos_tags import remove as remove_tag
from rarfile import RarFile, is_rarfile

# MARK: Functions


def add_path(path: str):
    os.environ["PATH"] += os.pathsep + path


def tag_bad(file: os.PathLike):
    remove_tag(T_ok, file=str(file))
    add_tag(T_bad, file=str(file))


def tag_ok(file: os.PathLike):
    remove_tag(T_bad, file=str(file))
    add_tag(T_ok, file=str(file))


def tag_collision(file: os.PathLike):
    remove_tag(T_ok, file=str(file))
    add_tag(T_collision, file=str(file))


# MARK: PATH

add_path("/usr/local/bin")
add_path("/opt/homebrew/bin")
add_path("/opt/homebrew/sbin")

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

    is_cbz = is_zipfile(src)
    is_cbr = is_rarfile(src)

    if not is_cbz and not is_cbr:
        print(f"Invalid archive {src.stem}")
        tag_bad(src)
        continue

    # Fix the extension
    if ".rar" == src.suffix and is_cbz:
        src_cbr = src
        print(f"Fixing {src_cbr.name} extension")
        dst_cbz = src.with_suffix(".cbz")
        os.rename(src_cbr, dst_cbz)
        src = dst_cbz
    elif ".zip" == src.suffix and is_cbr:
        src_cbz = src
        print(f"Fixing {src_cbz.name} extension")
        dst_cbr = src_cbz.with_suffix(".cbr")
        os.rename(src_cbz, dst_cbr)
        src = dst_cbr

    # Repack CBRs
    if ".cbr" == src.suffix:
        src_cbr = src
        dst_cbz = src_cbr.with_suffix(".cbz")
        if os.path.exists(dst_cbz):
            tag_collision(src_cbr)
            continue
        tmp = tempfile.mkdtemp(prefix="cbz_from_cbr_")
        PP_tmp = PurePath(tmp)
        with RarFile(src_cbr, "r") as archive:
            archive.extractall(tmp)
        with ZipFile(dst_cbz, "w", ZIP_STORED) as archive:
            for start, _, files in os.walk(tmp):
                for file in files:
                    file_path = os.path.join(start, file)
                    arcname = os.path.relpath(file_path, src_cbr)
                    archive.write(file_path, arcname)
        shutil.rmtree(tmp)
        is_cbz = is_zipfile(dst_cbz)
        if is_cbz:
            os.remove(src_cbr)
            src = dst_cbz
        else:
            tag_bad(dst_cbz)
            continue

    # Tag the comic as ok
    if is_cbz:
        tag_ok(src)
    else:
        tag_bad(src)
