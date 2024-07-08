# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# https://pypi.org/project/macos-tags/
# https://pypi.org/project/patool/
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# MARK: Imports

import os

# import shutil
import sys
from pathlib import Path

# import tempfile
from zipfile import is_zipfile

import patoolib
from macos_tags import Color, Tag
from macos_tags import add as _add_tag
from macos_tags import remove as _remove_tag
from patoolib import test_archive as _test_archive
from rarfile import is_rarfile

# MARK: Homebrew PATH
os.environ["PATH"] = (
    r"/usr/local/bin" + os.pathsep + os.environ["PATH"]
)
os.environ["PATH"] = (
    r"/opt/homebrew/bin" + os.pathsep + os.environ["PATH"]
)
os.environ["PATH"] += os.pathsep + r"/opt/homebrew/sbin"


# MARK: Import Overrides
def test_archive(file):
    if not isinstance(file, str):
        file = str(file)
    return _test_archive(file)


def add_tag(tag, file):
    if not isinstance(file, str):
        file = str(file)
    return _add_tag(tag, file=file)


def remove_tag(tag, file):
    if not isinstance(file, str):
        file = str(file)
    return _remove_tag(tag, file=file)


# MARK: Functions
def tag_bad(file):
    remove_tag(T_ok, file=src)
    add_tag(T_bad, file=src)


def tag_ok(file):
    remove_tag(T_bad, file=src)
    add_tag(T_ok, file=src)


def tag_collision(file):
    remove_tag(T_ok, file=src)
    add_tag(T_collision, file=src)


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

    try:
        test_archive(src)
    except Exception as e:
        tag_bad(src)
        continue

    # Fix the extension
    if ".rar" == src.suffix and is_zipfile(src):
        dest = src.with_suffix(".cbz")
        os.rename(src, dest)
        src = dest
    elif ".zip" == src.suffix and is_rarfile(src):
        dest = src.with_suffix(".cbr")
        os.rename(src, dest)
        src = dest

    # Repack CBRs
    if ".cbr" == src.suffix:
        cbz = src.with_suffix(".cbz")
        if os.path.exists(cbz):
            tag_collision(src)
            continue
        patoolib.repack_archive(src, cbz)
        if is_zipfile(cbz):
            os.remove(src)
            src = cbz
        else:
            tag_bad(cbz)
            continue

    # Tag the comic as ok
    tag_ok(src)
