# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# YTDL: Rename
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# MARK: Imports

import os
import sys
from pathlib import Path
from re import match as re_match
from re import sub as re_sub

# MARK: Functions


def new_stem(old_name):
    m = re_match(r"^(.*)\s+\((.*?)\)\s+\((.*?)\)$", old_name)
    if m is None:
        print("❌ No match found")
        return old_name

    print(m.groups())
    (base_name, av_info, channel_name) = m.groups()

    base_name = base_name.replace("[", "(")
    base_name = base_name.replace("]", ")")
    av_info = av_info.replace("_", "][")
    av_info = f"[{av_info}]"
    channel_name = re_sub(r"\s", "", channel_name)

    return f"{base_name} {av_info}-{channel_name}"


# MARK: The Loop

args = sys.argv[1:]
for arg in args:
    src = Path(arg)

    if not src.is_file():
        print(f"❌ {src.name} 👉 not a file")
        continue

    dst = src.with_stem(new_stem(src.stem))

    if src != dst:
        print(f"⬇️ {src.name}")
        print(f"⬆️ {dst.name}")
        os.rename(src, dst)
    else:
        print(f"♻️ {src.name}")
