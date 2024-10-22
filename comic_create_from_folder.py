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
from macos_tags import get_all as get_all_tags
from macos_tags import remove as remove_tag
from patoolib import create_archive, test_archive

# MARK: PATH Additions
# To allow patoolib to find the binaries from Homebrew

environ["PATH"] += pathsep + "/usr/local/bin"
environ["PATH"] += pathsep + "/opt/homebrew/bin"
environ["PATH"] += pathsep + "/opt/homebrew/sbin"

# MARK: Tags

GREEN, RED, YELLOW = itemgetter("GREEN", "RED", "YELLOW")(Color)

T_DST_CORRUPT = Tag(name="Corrupt Comic", color=RED)

T_DST_VALID = Tag(name="Valid Comic", color=GREEN)

T_SRC_DST_COLLISION = Tag(name="Collision", color=YELLOW)

T_SRC_REMOVE_FAILED = Tag(name="Failed Cleanup", color=RED)

T_SRC_ZIP_FAILED = Tag(name="Failed Creation", color=RED)

# MARK: The Loop
args = sys.argv[1:]
for arg in args:

    src = Path(arg)
    # `with_suffix` not used below because the directory may have a dot in the name
    dst = Path(f"{src.name}.cbz")

    # 🏷️ Remove existing tags
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    for tag in get_all_tags(file=str(src)):
        if tag in [
            T_SRC_ZIP_FAILED,
            T_SRC_REMOVE_FAILED,
            T_SRC_DST_COLLISION,
            T_DST_CORRUPT,
            T_DST_VALID,
        ]:
            remove_tag(tag, file=str(src))
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # 📁 Ensure a directory
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if not src.is_dir():
        print(f"🛑 {src.name} 👉 Not a directory")
        # No tag; this shouldn't happen when run as a Shortcut
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # 💥 Ensure no collision
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if dst.exists():
        print(f"🛑 {dst.name} 👉 Collision")
        add_tag(T_SRC_DST_COLLISION, file=str(src))
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # 📕 Create the CBZ
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    try:
        src_files = run(
            [
                "find",
                src,
                "-type",
                "f",
            ],
            capture_output=True,
            text=True,
        )
        chdir(src.parent)
        create_archive(
            str(dst.name),
            [relpath(fn, src.parent) for fn in src_files.stdout.splitlines()],
        )
    except Exception as e:
        print(f"❗️ {src.name} 👉 Error: {e}")
        add_tag(T_SRC_ZIP_FAILED, file=str(src))
        if dst.exists():
            remove(dst)
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # ✅ Test the CBZ
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    try:
        test_archive(str(dst))
        print(f"✅ {dst.name} 👉 Valid")
        add_tag(T_DST_VALID, file=str(dst))
    except Exception as e:
        print(f"🛑 {dst.name} 👉 {e}")
        add_tag(T_DST_CORRUPT, file=str(dst))
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # 🗑️ Remove the source directory
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    try:
        if dst.exists() and T_DST_VALID in get_all_tags(file=str(dst)):
            shutil.rmtree(src)
    except Exception as e:
        print(f"🛑 {src.name} 👉 {e}")
        add_tag(T_SRC_REMOVE_FAILED, file=str(src))
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
