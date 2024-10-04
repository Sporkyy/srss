# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Comic: Process
#
# External Dependencies
#   * https://pypi.org/project/macos-tags/
#   * https://pypi.org/project/patool/
#   * https://pypi.org/project/rarfile/
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# MARK: Imports

import sys
from operator import itemgetter
from os import environ, pathsep, remove, rename
from pathlib import Path
from zipfile import is_zipfile

from macos_tags import Color, Tag
from macos_tags import add as add_tag
from macos_tags import remove as remove_tag
from patoolib import repack_archive, test_archive
from rarfile import is_rarfile

from comic_create_from_folder import RED

# MARK: PATH
# To allow patoolib to find the binaries from Homebrew

environ["PATH"] += pathsep + "/usr/local/bin"
environ["PATH"] += pathsep + "/opt/homebrew/bin"
environ["PATH"] += pathsep + "/opt/homebrew/sbin"

# MARK: Constants

GREEN, RED, YELLOW = itemgetter("GREEN", "RED", "YELLOW")(Color)

# MARK: Tags
T_VALID = Tag(name="Comic is valid", color=Color.GREEN)
T_CORRUPT = Tag(name="Comic is corrupt", color=Color.RED)
T_COLLISON = Tag(name="File name collision", color=Color.YELLOW)


# MARK: Functions


def tag_corrupt(file: Path):
    remove_tag(T_VALID, file=str(file))
    add_tag(T_CORRUPT, file=str(file))


def tag_valid(file: Path):
    remove_tag(T_CORRUPT, file=str(file))
    add_tag(T_VALID, file=str(file))


# MARK: The Loop
for arg in sys.argv[1:]:
    src = Path(arg)
    tmp_dir = None

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

    # Ensure the extension is lowercase
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if src.suffix.lower() != src.suffix:
        print(f"⬇️ {src.name} 👉 Downcased suffix ({src.suffix.lower()})")
        dst = src.with_suffix(src.suffix.lower())
        rename(src, dst)
        src = dst
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Fix extension if necessary
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    remove_tag(T_COLLISON, file=str(src))
    if ".cbr" == src.suffix and is_zipfile(src):
        src_cbr = src
        dst_cbz = src.with_suffix(".cbz")
        if dst_cbz.exists():
            add_tag(T_COLLISON, file=str(src_cbr))
            print(f"⚠️ {src_cbr.name} 👉 Collision ({dst_cbz.name})")
            continue
        else:
            rename(src_cbr, dst_cbz)
            print(f"🔧 {src_cbr.name} Fixed extension (.cbr ➡️ .cbz)")
            src = dst_cbz
    elif ".cbz" == src.suffix and is_rarfile(src):
        src_cbz = src
        dst_cbr = src_cbz.with_suffix(".cbr")
        if dst_cbr.exists():
            add_tag(T_COLLISON, file=str(src_cbz))
            print(f"⚠️ {src_cbz.name} 👉 Collision ({dst_cbr.name})")
            continue
        else:
            rename(src_cbz, dst_cbr)
            print(f"🔧 {src_cbz.name} 👉 Fixed extension (.cbz ➡️ .cbr)")
            src = dst_cbr
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Repack CBRs
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    remove_tag(T_COLLISON, file=str(src))
    if ".cbr" == src.suffix and is_rarfile(src):
        src_cbr = src
        dst_cbz = src_cbr.with_suffix(".cbz")
        if dst_cbz.exists():
            add_tag(T_COLLISON, file=str(src_cbr))
            print(f"⚠️ {src_cbr.name} 👉 Collision ({dst_cbz.name})")
            continue
        else:
            try:
                test_archive(str(src_cbr))
                repack_archive(str(src_cbr), str(dst_cbz))
                # Presuming that `repack_archive` has some kind of test built-in
                remove(src_cbr)
                src = dst_cbz
            except Exception as e:
                tag_corrupt(src)
                print(f"🛑 Failed repack 👉 {src.name}")
                print(f"❗️ Error 👉 {e}")
                continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Tag the comic as ok
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    try:
        test_archive(str(src))
        tag_valid(src)
        print(f"✅ {src.name} 👉 Valid")
    except Exception as e:
        tag_corrupt(src)
        print(f"🛑 {src.name} 👉 Corrupt ")
        print(e)
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
