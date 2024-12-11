# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# CBZ: Create From Folder
#
# ## External Dependencies
#   * https://pypi.org/project/macos-tags/
#   * https://pypi.org/project/patool/
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# MARK: Imports

from glob import glob
from operator import itemgetter
from os import PathLike, chdir, environ, pathsep, remove
from os.path import relpath
from pathlib import Path
from shutil import rmtree
from subprocess import run
from sys import argv
from typing import Union

from macos_tags import Color, Tag
from macos_tags import add as add_tag_original
from macos_tags import get_all as get_all_tags_original
from macos_tags import remove as remove_tag_original
from patoolib import create_archive, test_archive
from send2trash import send2trash

# MARK: PATH Additions

# To allow `patoolib` to find the binaries from Homebrew
environ["PATH"] += pathsep + "/usr/local/bin"
environ["PATH"] += pathsep + "/opt/homebrew/bin"
environ["PATH"] += pathsep + "/opt/homebrew/sbin"

# MARK: Constants

GREEN, RED, YELLOW = itemgetter("GREEN", "RED", "YELLOW")(Color)

T_DST_CORRUPT = Tag(name="Corrupt Comic", color=RED)

T_DST_VALID = Tag(name="Valid Comic", color=GREEN)

T_SRC_DST_COLLISION = Tag(name="Collision", color=YELLOW)

T_SRC_REMOVE_FAILED = Tag(name="Failed Cleanup", color=RED)

T_SRC_ZIP_FAILED = Tag(name="Failed Creation", color=RED)

# MARK: Functions


# `macos_tags` Extensions adding `PathLike` Support
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Extend `macos_tags.add` to accept a `PathLike` object
def add_tag(tag: Tag, file: Union[PathLike, str]) -> None:
    add_tag_original(tag, file=str(file))


# Extend `macos_tags.get_all_tags` to accept a `PathLike` object
def get_all_tags(file: Union[PathLike, str]) -> list[Tag]:
    return get_all_tags_original(file=str(file))


# Extend `macos_tags.remove` to accept a `PathLike` object
def remove_tag(tag: Tag, file: Union[PathLike, str]) -> None:
    remove_tag_original(file=str(file), tag=tag)


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=


def get_descendant_file_relative_paths(dir: Union[PathLike, str]) -> list[str]:
    dir = Path(dir)
    if not dir.is_dir():
        return []
    descendants = glob(str(dir / "**"), recursive=True)
    files = [f for f in descendants if Path(f).is_file()]
    relative_paths = [relpath(fp, dir) for fp in files]
    return relative_paths


# MARK: The Loop
args = argv[1:]
for arg in args:

    src = Path(arg).resolve()

    # 📁 Ensure a directory
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if not src.is_dir():
        print(f"🛑 {src} 👉 Not a directory")
        # No tag; this shouldn't happen when run as a Shortcut
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Not using `with_suffix` below in case the `src` dir has dot(s) in the name
    dst = Path(f"{src}.cbz")
    print(f"📂 {src} ➡️ {dst}")

    # 💥 Ensure no collision
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if dst.exists():
        print(f"🛑 {dst} 👉 Collision")
        add_tag(T_SRC_DST_COLLISION, file=src)
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # 🏷️ Remove existing tags
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    for tag in get_all_tags(file=src):
        if tag in [
            T_SRC_ZIP_FAILED,
            T_SRC_REMOVE_FAILED,
            T_SRC_DST_COLLISION,
            T_DST_CORRUPT,
            T_DST_VALID,
        ]:
            remove_tag(tag, file=src)
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # 📕 Create the CBZ
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    try:
        files = get_descendant_file_relative_paths(src)
        print(files)
        chdir(src)
        create_archive(dst, files)
    except Exception as e:
        print(f"❗️ Error: {e}")
        add_tag(T_SRC_ZIP_FAILED, file=src)
        if dst.exists():
            send2trash(dst)
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # ✅ Test the CBZ
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    try:
        test_archive(str(dst))
        print(f"✅ {dst.name} 👉 Valid")
        add_tag(T_DST_VALID, dst)
    except Exception as e:
        print(f"🛑 {dst.name} 👉 {e}")
        add_tag(T_DST_CORRUPT, dst)
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # 🗑️ Remove the source directory
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    try:
        if dst.exists() and T_DST_VALID in get_all_tags(file=dst):
            send2trash(src)
    except Exception as e:
        print(f"🛑 {src.name} 👉 {e}")
        add_tag(T_SRC_REMOVE_FAILED, file=src)
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
