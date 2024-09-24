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
from os import chdir, environ, pathsep, remove
from os.path import relpath
from pathlib import Path
from subprocess import run
from zipfile import is_zipfile

from macos_tags import Color, Tag
from macos_tags import add as add_tag
from patoolib import create_archive, test_archive

# MARK: PATH
# To allow patoolib to find the binaries from Homebrew

environ["PATH"] += pathsep + "/usr/local/bin"
environ["PATH"] += pathsep + "/opt/homebrew/bin"
environ["PATH"] += pathsep + "/opt/homebrew/sbin"


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
        add_tag(T_collision, file=str(src_dir))
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
        add_tag(T_bad, file=str(dst_cbz))
        if dst_cbz.exists():
            remove(dst_cbz)
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Test the CBZ
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    try:
        test_archive(str(dst_cbz))
        print(f"✅ CBZ OK {dst_cbz.name}")
        add_tag(T_ok, file=str(dst_cbz))
        shutil.rmtree(src_dir)
    except Exception as e:
        print(f"🛑 CBZ Invalid {dst_cbz.name}")
        print(f"❗️ Error: {e}")
        add_tag(T_bad, file=str(dst_cbz))
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
