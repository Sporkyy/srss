# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Comic: Create From Images
#
# Notes:
#   * patool cannot list the contents of an archive in a way that can be captured and
#     put into a variable. That is by design because it would be difficult.
#
# External Dependencies
#   * https://pypi.org/project/macos-tags/
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# MARK: Imports

from operator import itemgetter
from os import PathLike, chdir, environ, pathsep
from os.path import relpath
from pathlib import Path, PurePath
from sys import argv
from typing import Sequence, Union

from macos_tags import Color, Tag
from macos_tags import add as add_tag_original
from patoolib import create_archive, test_archive
from send2trash import send2trash

# MARK: PATH Additions

# Allow `patoolib` to find the binaries from Homebrew
environ["PATH"] += pathsep + "/usr/local/bin"
environ["PATH"] += pathsep + "/opt/homebrew/bin"
environ["PATH"] += pathsep + "/opt/homebrew/sbin"

# MARK: Constants

GREEN, RED, YELLOW = itemgetter("GREEN", "RED", "YELLOW")(Color)
# To share the tags between scripts, copy+paste becase each script must be standalone
T_VALID = Tag(name="Valid Comic", color=GREEN)
T_CORRUPT = Tag(name="Corrupt Comic", color=RED)
T_COLLISION = Tag(name="Collision", color=YELLOW)

# MARK: Functions


# Extend `macos_tags.add` to accept a `PathLike` object
def add_tag(tag: Tag, file: Union[str, PathLike]) -> None:
    add_tag_original(tag, file=str(file))


# So this doens't handle the same path with different cases
# macOS is case-insensitive but case-preserving by default
# e.g.
#   print(Path("/Applications/").samefile(Path("/Applications/"))) # True
#   print(Path("/Applications/").samefile(Path("/applications/"))) # Also True!
# (FYI: `os.path.realpath` does not get the correct case)
# (FYI: `chdir` and `getcwd` do not get the correct case either)
# (Conclusion: Iterating+checking all keys with `samefile` woud work, but not worth it)
# So that is a bit of a problem, but not one I solve here
# Because this is intended to be used in a Shortcut
# And thus the paths should come directly from macoS/Finder
# (Except during testing)
def group_files_by_parent(
    files: Sequence[Union[PathLike, str]]
) -> dict[Union[PathLike, str], list[Union[PathLike, str]]]:
    groups = {}
    for file in files:
        fp = Path(file).resolve()
        if not fp.is_file():
            continue
        pp = fp.parent
        if pp not in groups:
            groups[pp] = []
        groups[pp].append(fp)
    return groups


# Group the files by their parent directory
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
args = argv[1:]
grouped = group_files_by_parent(args)
# print(grouped)
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# Create an archive for each group
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
for parent, files in grouped.items():
    ppp = PurePath(parent)
    # `with_suffix` not used below because the directory may have a dot in the name
    dst = Path(ppp.joinpath(f"{ppp.name}.cbz"))

    if dst.is_file():
        print(f"🛑 COLLISION! {dst.name} 👉 Already exists")
        add_tag(T_COLLISION, file=dst)
        continue

    print(f"📦 Creating: {dst}")
    print(f"📁 Source: {files}")

    chdir(ppp)  # Change to the parent directory here, for using `relpath` below
    create_archive(
        dst,
        [relpath(fn, ppp) for fn in files],
    )
    print(f"📦 Created: {dst}")

    try:
        test_archive(dst)
        print(f"✅ Verified: {dst}")
        add_tag(T_VALID, file=dst)
        print(f"🗑️ Deleting: {files}")
        send2trash(files)
    except Exception as e:
        print(f"❗️ Error: {e}")
        add_tag(T_CORRUPT, file=dst)
        print(f"🗑️ Deleting: {dst}")
        send2trash(dst)
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
