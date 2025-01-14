# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Video: Rename with Resolution
#
# ## External Dependencies
#   * https://pypi.org/project/imageio_ffmpeg/
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# MARK: Imports

from os import environ, pathsep
from pathlib import Path
from re import IGNORECASE as re_IGNORECASE
from re import compile as re_compile
from re import search as re_search
from re import sub as re_sub
from sys import argv

from imageio_ffmpeg import read_frames

# MARK: PATH Additions
# To allow `imageio_ffmpeg` to find the binaries from Homebrew

environ["PATH"] += pathsep + "/usr/local/bin"
environ["PATH"] += pathsep + "/opt/homebrew/bin"
environ["PATH"] += pathsep + "/opt/homebrew/sbin"

# MARK: Constants

MOVIE_SUFFIXES = [
    ".asf",
    ".avi",
    ".divx",
    ".flv",
    ".m4v",
    ".mkv",
    ".mov",
    ".mp4",
    ".mpg",
    ".mpeg",
    ".ogv",
    ".ogm",
    ".rm",
    ".rmvb",
    ".ts",
    ".vob",
    ".webm",
    ".wmv",
]

# MARK: The Loop
args = argv[1:]
for arg in args:

    src = Path(arg).resolve()

    # ♻️ Skip if the path is not a file
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if not src.is_file():
        print(f"🛑 {src.name} 👉 not a file")
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # ♻️ Skip if the path does not have a recognized suffix
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if not src.suffix.lower() in MOVIE_SUFFIXES:
        print(f"🛑 {src.suffix} 👉 not a movie suffix")
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Normalize dimensions (<w>x<h>) in the file name to resolution (<h>p)
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    pattern_dimensions = re_compile(r"\b(\d{3,4})\s?[xX]\s?(\d{3,4})\b")
    matches = re_search(pattern_dimensions, src.stem)
    if matches:
        print(f"📏 {src.name} (name) 👉 {matches.group(1)}")
        fn_height = matches.group(2)
        dst = src.with_stem(re_sub(pattern_dimensions, f"{fn_height}p", src.stem))
        print(f"♻️ Renaming {src} 👉 {dst}")
        src.rename(dst)
        src = dst
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Get the resolution from the file name
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    pattern_resolution = re_compile(r"\b(\d{3,4}[pP])\b")
    fn_resolution = None
    matches = re_search(pattern_resolution, src.stem)
    if matches:
        fn_resolution = matches.group(1)
        print(f"📏 {src.name} (name) 👉 {fn_resolution}")
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # If the "p" is capitalized, make it lowercase
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if fn_resolution:
        if "P" in fn_resolution:
            fn_resolution = fn_resolution.lower()
            dst = src.with_stem(re_sub(pattern_resolution, fn_resolution, src.stem))
            print(f"♻️ Lowering case {src} 👉 {dst}")
            dst = src.rename(dst)
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # (Try to) get the metadata or skip+tag if the video is corrupt
    # And if the video is corrupt, rename it to indicate that
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    try:
        reader = read_frames(src)
        meta = reader.__next__()
    except Exception as e:
        print(f"🚫 {src.name} 👉 corrupt")
        src.rename(src.with_stem(f"_CORRUPT_ {src.stem}"))
        print(e)
        continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Get the video resolution
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    vid_width, vid_height = meta["size"]
    print(f"📏 {src.name} (meta) 👉 {vid_width}x{vid_height}")
    vid_resolution = f"{vid_height}p"
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Skip if the resolution is already in the file name or replace it if it's wrong
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if fn_resolution:
        if fn_resolution == vid_resolution:
            print(f"🚫 {src.name} 👉 already has correct resolution")
            continue
        else:
            dst = src.with_stem(re_sub(pattern_resolution, vid_resolution, src.stem))
            print(f"♻️ {src} 👉 {dst}")
            src.rename(dst)
            continue
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    # Add the resolution to the file name if it is missing
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    if not fn_resolution:
        dst = src.with_stem(f"{src.stem} [{vid_resolution}]")
        print(f"♻️ {src} 👉 {dst}")
        src.rename(dst)
    # =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
