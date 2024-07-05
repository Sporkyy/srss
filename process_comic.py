# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# https://pypi.org/project/macos-tags/
# https://pypi.org/project/rarfile/
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

import rarfile
from macos_tags import Color, Tag
from macos_tags import add as _add_tag
from macos_tags import remove as _remove_tag


def add_tag(tag, file):
    _add_tag(tag, file=str(file))


def remove_tag(tag, file):
    _remove_tag(tag, file=str(file))


def tag_bad(file):
    remove_tag(T_ok, file=src)
    add_tag(T_bad, file=src)


def tag_ok(file):
    remove_tag(T_bad, file=src)
    add_tag(T_ok, file=src)


def tag_collision(file):
    remove_tag(T_ok, file=src)
    add_tag(T_collision, file=src)


T_ok = Tag(name="Comic is ok", color=Color.GREEN)
T_bad = Tag(name="Comic is bad", color=Color.RED)
T_collision = Tag(
    name="File name collision", color=Color.YELLOW
)

args = sys.argv[1:]

for arg in args:
    src = Path(arg)

    # Ensure the extension is lowercase
    if src.suffix.lower != src.suffix:
        dst = src.with_suffix(src.suffix.lower())
        os.rename(src, dst)
        src = dst

    # Skip if not a comic book archive
    if not src.suffix in [".cbz", ".cbr"]:
        continue

    is_zip = zipfile.is_zipfile(src)
    is_rar = rarfile.is_rarfile(src)

    if not (is_zip or is_rar):
        tag_bad(src)
        continue

    # Fix the extension
    if is_zip and ".rar" == src.suffix:
        dest = src.with_suffix(".cbz")
        os.rename(src, dest)
        src = dest
    elif is_rar and ".zip" == src.suffix:
        dest = src.with_suffix(".cbr")
        os.rename(src, dest)
        src = dest

    # Extract and repack CBRs
    if is_rar:
        cbz = src.with_suffix(".cbz")
        if os.path.exists(cbz):
            tag_collision(src)
            continue
        tmp = Path(tempfile.mkdtemp())
        with rarfile.RarFile(src) as rf:
            rf.extractall(tmp)
        with zipfile.ZipFile(
            cbz, mode="w", compression=zipfile.ZIP_STORED
        ) as archive:
            for fn in os.listdir(tmp):
                archive.write(tmp / fn, arcname=fn)
        shutil.rmtree(tmp)
        is_zip = zipfile.is_zipfile(cbz)
        if is_zip:
            os.remove(src)
            src = cbz

    # Anything left should be valid
    if is_zip:
        tag_ok(src)
    else:
        tag_bad(src)
