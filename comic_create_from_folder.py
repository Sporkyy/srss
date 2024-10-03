# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Comic: Create From Folder
#
# ## External Dependencies
#   * https://pypi.org/project/macos-tags/
#   * https://pypi.org/project/patool/
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# MARK: Imports

import shutil
import sys
from operator import itemgetter
from os import chdir, environ, pathsep, remove
from os.path import relpath
from pathlib import Path
from subprocess import run

from macos_tags import Color, Tag
from macos_tags import add as add_tag
from patoolib import create_archive, test_archive

from image_tag_resolution import YELLOW

# MARK: PATH
# To allow patoolib to find the binaries from Homebrew

environ["PATH"] += pathsep + "/usr/local/bin"
environ["PATH"] += pathsep + "/opt/homebrew/bin"
environ["PATH"] += pathsep + "/opt/homebrew/sbin"

# MARK: Constants

GREEN, RED, YELLOW = itemgetter("GREEN", "RED", "YELLOW")(Color)

# MARK: Tags
T_OK = Tag(name="Comic is ok", color=GREEN)

T_BAD = Tag(name="Comic is bad", color=RED)

T_COLLISION = Tag(name="File name collision", color=YELLOW)

args = sys.argv[1:]

# MARK: The Loop
for arg in args:

    src_dir = Path(arg)
    dst_cbz = Path(f"{src_dir.name}.cbz")

    # Ensure a directory
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if not src_dir.is_dir():
        print(f"🛑 Not a directory {src_dir.name}")
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Ensure no collision
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if dst_cbz.exists():
        print(f"🛑 Existing {dst_cbz.name}")
        add_tag(T_COLLISION, file=str(src_dir))
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Create the CBZ
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    try:
        src_files = run(
            [
                "find",
                src_dir,
                "-type",
                "f",
            ],
            capture_output=True,
            text=True,
        )
        chdir(src_dir.parent)
        create_archive(
            str(dst_cbz.name),
            [relpath(fn, src_dir.parent) for fn in src_files.stdout.splitlines()],
        )
    except Exception as e:
        print(f"❗️ Error: {e}")
        add_tag(T_BAD, file=str(dst_cbz))
        if dst_cbz.exists():
            remove(dst_cbz)
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Test the CBZ
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    try:
        test_archive(str(dst_cbz))
        print(f"✅ CBZ OK {dst_cbz.name}")
        add_tag(T_OK, file=str(dst_cbz))
        shutil.rmtree(src_dir)
    except Exception as e:
        print(f"🛑 CBZ Invalid {dst_cbz.name}")
        print(f"❗️ Error: {e}")
        add_tag(T_BAD, file=str(dst_cbz))
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
