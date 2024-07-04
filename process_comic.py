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
from macos_tags import add as add_tag
from macos_tags import remove as remove_tag

args = sys.argv[1:]

tag_is_ok = Tag(name="Green", color=Color.GREEN)
tag_is_bad = Tag(name="Red", color=Color.RED)
tag_is_collision = Tag(name="Yellow", color=Color.YELLOW)

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

    def mark_bad():
        remove_tag(tag_is_ok, file=str(src))
        add_tag(tag_is_bad, file=str(src))

    def mark_ok():
        remove_tag(tag_is_bad, file=str(src))
        add_tag(tag_is_ok, file=str(src))

    def mark_collision():
        remove_tag(tag_is_ok, file=str(src))
        add_tag(tag_is_collision, file=str(src))

    if not (is_zip or is_rar):
        mark_bad()
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
            mark_collision()
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
        mark_ok()
    else:
        mark_bad()
