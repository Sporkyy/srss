# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Comic: Process
#
# External Dependencies
#   * https://pypi.org/project/macos-tags/
#   * https://pypi.org/project/patool/
#   * https://pypi.org/project/rarfile/
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# MARK: Imports

from operator import itemgetter
from os import PathLike, environ, pathsep, remove, rename
from pathlib import Path
from sys import argv
from typing import Union
from zipfile import is_zipfile

from macos_tags import Color, Tag
from macos_tags import add as add_tag_original
from macos_tags import get_all as get_all_tags_original
from macos_tags import remove as remove_tag_original
from patoolib import repack_archive, test_archive
from rarfile import is_rarfile
from send2trash import send2trash

# MARK: PATH
# To allow patoolib to find the binaries from Homebrew

environ["PATH"] += pathsep + "/usr/local/bin"
environ["PATH"] += pathsep + "/opt/homebrew/bin"
environ["PATH"] += pathsep + "/opt/homebrew/sbin"

# MARK: Constants

GREEN, RED, YELLOW = itemgetter("GREEN", "RED", "YELLOW")(Color)

T_VALID = Tag(name="Valid Comic", color=GREEN)
T_CORRUPT = Tag(name="Corrupt Comic", color=RED)
T_COLLISON = Tag(name="Collision", color=YELLOW)

# MARK: Functions


# Extend `macos_tags.add` to accept a `PathLike` object
def add_tag(tag: Tag, file: Union[PathLike, str]) -> None:
    add_tag_original(tag, file=str(file))


# Extend `macos_tags.get_all_tags` to accept a `PathLike` object
def get_all_tags(file: Union[PathLike, str]) -> list[Tag]:
    return get_all_tags_original(file=str(file))


# Extend `macos_tags.remove` to accept a `PathLike` object
def remove_tag(tag: Tag, file: Union[PathLike, str]) -> None:
    remove_tag_original(file=str(file), tag=tag)


def remove_tags(tags: list[Tag], file: Union[PathLike, str]) -> None:
    for tag in get_all_tags(file):
        if tag in tags:
            remove_tag(tag, file)


# MARK: The Loop
args = argv[1:]
for arg in args:
    src = Path(arg)

    # Skip if not a file
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if not src.is_file():
        print(f"🛑 {src.name} 👉 Not a file")
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Skip if not a comic book archive
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if not src.suffix.lower() in [".cbz", ".cbr"]:
        print(f"🛑 {src.name} 👉 Unrecognized suffix ({src.suffix})")
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Remove existing tags
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    remove_tags([T_VALID, T_CORRUPT, T_COLLISON], file=src)
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Ensure the extension is lowercase
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if src.suffix.lower() != src.suffix:
        print(f"⬇️ {src.name} 👉 Downcased suffix ({src.suffix.lower()})")
        dst = src.with_suffix(src.suffix.lower())
        rename(src, dst)
        src = dst
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Fix extension if necessary
    # This could be combined with the CBR repack, but it's not
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if ".cbr" == src.suffix and is_zipfile(src):
        dst = src.with_suffix(".cbz")
        if dst.exists():
            add_tag(T_COLLISON, file=src)
            print(f"⚠️ {src.name} 👉 Collision ({dst.name})")
            continue
        else:
            rename(src, dst)
            print(f"🔧 {src.name} 👉 Fixed extension (.cbr ➡️ .cbz)")
            src = dst
    elif ".cbz" == src.suffix and is_rarfile(src):
        dst = src.with_suffix(".cbr")
        if dst.exists():
            add_tag(T_COLLISON, file=src)
            print(f"⚠️ {src.name} 👉 Collides with {dst.name}")
            continue
        else:
            rename(src, dst)
            print(f"🔧 {src.name}  👉 Fixed extension (.cbz ➡️ .cbr)")
            src = dst
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Repack CBRs
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if ".cbr" == src.suffix and is_rarfile(src):
        dst = src.with_suffix(".cbz")
        if dst.exists():
            add_tag(T_COLLISON, file=src)
            print(f"⚠️ Collision 👉 {src.name} 💥 ({dst.name})")
            continue
        else:
            try:
                test_archive(src)
                repack_archive(src, dst)
                send2trash(src)
                src = dst
            except Exception as e:
                add_tag(T_CORRUPT, file=src)
                print(f"🛑 {src.name} 👉 Failed repack")
                print(e)
                continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Tag the comic as valid or corrupt
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    try:
        test_archive(str(src))
        add_tag(T_VALID, file=src)
        print(f"✅ {src.name} 👉 Valid")
    except Exception as e:
        add_tag(T_CORRUPT, file=src)
        print(f"🛑 {src.name} 👉 Corrupt ")
        print(e)
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
