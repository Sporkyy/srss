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
from macos_tags import get_all as get_all_tags
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
T_VALID = Tag(name="Comic is valid", color=GREEN)
T_CORRUPT = Tag(name="Comic is corrupt", color=RED)
T_COLLISON = Tag(name="File name collision", color=YELLOW)


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

    # Remove existing tags
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    for tag in get_all_tags(file=str(src)):
        if tag in [T_VALID, T_CORRUPT, T_COLLISON]:
            remove_tag(tag, file=str(src))
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
            add_tag(T_COLLISON, file=str(src))
            print(f"⚠️ {src.name} 👉 Collision ({dst.name})")
            continue
        else:
            rename(src, dst)
            print(f"🔧 {src.name} 👉 Fixed extension (.cbr ➡️ .cbz)")
            src = dst
    elif ".cbz" == src.suffix and is_rarfile(src):
        dst = src.with_suffix(".cbr")
        if dst.exists():
            add_tag(T_COLLISON, file=str(src))
            print(f"⚠️ {src.name} 👉 Collides with {dst.name}")
            continue
        else:
            rename(src, dst)
            print(f"🔧 {src.name} 👉 Fixed extension (.cbz ➡️ .cbr)")
            src = dst
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Repack CBRs
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if ".cbr" == src.suffix and is_rarfile(src):
        dst = src.with_suffix(".cbz")
        if dst.exists():
            add_tag(T_COLLISON, file=str(src))
            print(f"⚠️ Collision 👉 {src.name} 💥 ({dst.name})")
            continue
        else:
            try:
                test_archive(str(src))
                repack_archive(str(src), str(dst))
                # Presuming that `repack_archive` has some kind of test built-in
                remove(src)
                src = dst
            except Exception as e:
                add_tag(T_CORRUPT, file=str(src))
                print(f"🛑 {src.name} 👉 Failed repack")
                print(e)
                continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Tag the comic as valid or corrupt
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    try:
        test_archive(str(src))
        add_tag(T_VALID, file=str(src))
        print(f"✅ {src.name} 👉 Valid")
    except Exception as e:
        add_tag(T_CORRUPT, file=str(src))
        print(f"🛑 {src.name} 👉 Corrupt ")
        print(e)
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
