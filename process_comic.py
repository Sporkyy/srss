# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Process Comic
#
# External Dependencies
#   * https://pypi.org/project/macos-tags/
#   * https://pypi.org/project/rarfile/
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# MARK: Imports

import sys
from os import PathLike, environ, pathsep, remove, rename
from pathlib import Path
from zipfile import is_zipfile

from macos_tags import Color, Tag
from macos_tags import add as add_tag
from macos_tags import remove as remove_tag
from patoolib import repack_archive, test_archive
from rarfile import is_rarfile

# MARK: PATH
# To allow patoolib to find the binaries from Homebrew

environ["PATH"] += pathsep + "/usr/local/bin"
environ["PATH"] += pathsep + "/opt/homebrew/bin"
environ["PATH"] += pathsep + "/opt/homebrew/sbin"

# MARK: Functions


def tag_bad(file: PathLike):
    remove_tag(T_ok, file=str(file))
    add_tag(T_bad, file=str(file))


def tag_ok(file: PathLike):
    remove_tag(T_bad, file=str(file))
    add_tag(T_ok, file=str(file))


def tag_collision(file: PathLike):
    remove_tag(T_ok, file=str(file))
    add_tag(T_collision, file=str(file))


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
    tmp_dir = None

    # Skip if not a comic book archive
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if not src.suffix.lower() in [".cbz", ".cbr"]:
        print(f"🙅‍♂️ Not a comic {src.name}")
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Ensure the extension is lowercase
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if src.suffix.lower() != src.suffix:
        print(f"⬇️ Downcasing suffix {src.name}")
        dst = src.with_suffix(src.suffix.lower())
        rename(src, dst)
        src = dst
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Fix the extension
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if ".rar" == src.suffix and is_zipfile(src):
        src_cbr = src
        print(f"♻️ Changing {src_cbr.name} extension to .cbz")
        dst_cbz = src.with_suffix(".cbz")
        rename(src_cbr, dst_cbz)
        src = dst_cbz
    elif ".zip" == src.suffix and is_rarfile(src):
        src_cbz = src
        print(f"♻️ Changing {src_cbz.name} extension to .cbr")
        dst_cbr = src_cbz.with_suffix(".cbr")
        rename(src_cbz, dst_cbr)
        src = dst_cbr
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Repack CBRs
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if ".cbr" == src.suffix:
        try:
            src_cbr = src
            test_archive(str(src_cbr))
            dst_cbz = src_cbr.with_suffix(".cbz")
            repack_archive(str(src_cbr), str(dst_cbz))
            # I presume that `repack_archive` has some kind of test built-in
            remove(src_cbr)
            src = dst_cbz
        except Exception as e:
            tag_bad(src)
            print(f"🛑 Failed repack {src.name}")
            print(f"❗️ Error {e}")
            continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Tag the comic as ok
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    try:
        test_archive(str(src))
        tag_ok(src)
        print(f"✅ Comic OK {src.name}")
    except Exception as e:
        tag_bad(src)
        print(f"🛑 Comic bad {src.name}")
        print(e)
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
