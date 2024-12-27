# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# CBZ: Create From Folder
#
# ## External Dependencies
#   * https://pypi.org/project/macos-tags/
#   * https://pypi.org/project/patool/
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# MARK: Imports

from glob import glob as glob_original
from operator import itemgetter
from os import PathLike, chdir, environ, pathsep
from os.path import relpath
from pathlib import Path
from sys import argv
from typing import Sequence, Union

from macos_tags import Color, Tag
from macos_tags import add as add_tag_original
from macos_tags import get_all as get_all_tags_original
from macos_tags import remove as remove_tag_original
from patoolib import create_archive as create_archive_original
from patoolib import test_archive as test_archive_original
from send2trash import send2trash

# MARK: Path

# Add Homebrew locations to the path for `patoolib`
environ["PATH"] += pathsep + "/usr/local/bin"
environ["PATH"] += pathsep + "/opt/homebrew/bin"
environ["PATH"] += pathsep + "/opt/homebrew/sbin"

# MARK: Constants

GREEN, RED, YELLOW = itemgetter("GREEN", "RED", "YELLOW")(Color)

TAG_CORRUPT = Tag(name="Corrupt Comic", color=RED)

TAG_VALID = Tag(name="Valid Comic", color=GREEN)

TAG_COLLISION = Tag(name="Collision", color=YELLOW)

TAG_CLEANUP_FAILED = Tag(name="Failed Cleanup", color=RED)

TAG_FAILED_ARCHIVE_CREATION = Tag(name="Failed Creation", color=RED)

# MARK: Functions

# Built-In Related Functions


# Useful when using `patoolib.create_archive`
def get_descendant_file_relative_paths(dir: Union[Path, str]) -> list[str]:
    dir = Path(dir).resolve()
    if not dir.is_dir():
        return []
    descendants = dir.rglob("*")
    files = [f for f in descendants if f.is_file()]
    relative_paths = [relpath(fp, dir) for fp in files]
    return relative_paths


# Extend `glob.glob` to accept `PathLike` objects
def glob(pathname: Union[PathLike, str], *args, **kwargs) -> list[str]:
    return glob_original(str(pathname), *args, **kwargs)


# Tag Related Functions


# Extend `macos_tags.add` to accept `PathLike` objects
def add_tag(tag: Tag, file: Union[PathLike, str], *args, **kwargs) -> None:
    add_tag_original(tag, file=str(file), *args, **kwargs)


# Extend `macos_tags.get_all_tags` to accept `PathLike` objects
def get_all_tags(file: Union[PathLike, str], *args, **kwargs) -> list[Tag]:
    return get_all_tags_original(file=str(file), *args, **kwargs)


# Extend `macos_tags.remove` to accept `PathLike` objects
def remove_tag(tag: Tag, file: Union[PathLike, str], *args, **kwargs) -> None:
    remove_tag_original(file=str(file), tag=tag, *args, **kwargs)


# Convenience function for `macos_tags.remove` on multiple tags
def remove_tags(tags: list[Tag], file: Union[PathLike, str]) -> None:
    for tag in get_all_tags(file):
        if tag in tags:
            remove_tag(tag, file)


def has_tag(tag: Tag, file: Union[PathLike, str]) -> bool:
    return tag in get_all_tags(file)


# Patool Related Functions


# Extend `patoolib.create_archive` to accept `PathLike` objects
def create_archive(
    archive: Union[PathLike, str],
    filenames: Sequence[Union[PathLike, str]],
    *args,
    **kwargs,
) -> None:
    create_archive_original(
        archive=str(archive),
        filenames=[str(filename) for filename in filenames],
        *args,
        **kwargs,
    )


# Extend `patoolib.test_archive` to accept `PathLike` objects
def test_archive(archive: Union[PathLike, str], *args, **kwargs) -> None:
    test_archive_original(archive=str(archive), *args, **kwargs)


# MARK: The Loop
args = argv[1:]
for arg in args:

    src = Path(arg).resolve()

    # 🚨 Ensure it exists
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if not src.exists():
        print(f"🛑 {src} 👉 Does not exist")
        # No tag; this shouldn't happen when run as a Shortcut
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # 📁 Ensure it's a directory
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if not src.is_dir():
        print(f"🛑 {src} 👉 Not a directory")
        # No tag; this shouldn't happen when run as a Shortcut
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # 🛩️ Determine the destination
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # Not using `with_suffix` below in case the `src` dir has dot(s) in the name
    dst = Path(f"{src}.cbz")
    print(f"📂 {src} ➡️ {dst}")
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # 💥 Ensure no collision at the desination
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if dst.exists():
        print(f"🛑 {dst} 👉 Collision")
        add_tag(TAG_COLLISION, file=src)
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # 🏷️ Remove existing tags
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    remove_tags(
        [
            TAG_FAILED_ARCHIVE_CREATION,
            TAG_CLEANUP_FAILED,
            TAG_COLLISION,
            TAG_CORRUPT,
            TAG_VALID,
        ],
        file=src,
    )
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # 📕 Create the CBZ
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    try:
        files = get_descendant_file_relative_paths(src)
        print(files)
        chdir(src)  # !! Don't forget to change to the source directory
        create_archive(dst, files)
    except Exception as e:
        print(f"❗️ Error: {e}")
        add_tag(TAG_FAILED_ARCHIVE_CREATION, file=src)
        if dst.exists():
            send2trash(dst)
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # ✅ Test the CBZ
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    try:
        test_archive(dst)
        print(f"✅ {dst.name} 👉 Valid")
        add_tag(TAG_VALID, dst)
    except Exception as e:
        print(f"🛑 {dst.name} 👉 {e}")
        add_tag(TAG_CORRUPT, dst)
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # 🗑️ Remove the source directory
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    try:
        if dst.exists() and has_tag(TAG_VALID, dst):
            send2trash(src)
    except Exception as e:
        print(f"🛑 {src.name} 👉 {e}")
        add_tag(TAG_CLEANUP_FAILED, file=src)
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
