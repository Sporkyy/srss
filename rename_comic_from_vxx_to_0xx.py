# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Rename Comic from vXX to 0XX
#
# This script is for performing the common comic book
# renaming operation of changing the volume number to a
# Mylar-compatible three-digit issue number.
# An operation most commonly performed on manga volumes.
#
# This is done with macOS Shortcuts as a Quick Action in
# Finder.
#
# Step 1: Allow Shortcuts to Run Scripts
#   Shortcuts
#   ↳ Settings...
#   ↳ Advanced
#   ↳ ☑ Allow Running Scripts
#
# Step 2: Create a Shortcut
#   File
#   ↳ New Shorcut
#
# Step 3: Configure it as a Quick Action
#   Shortcut Details
#   ↳ Details
#   ↳ ☑ Use as Quick Action
#   ↳ ☑ Finder
#
# Step 4: Configure it to Receive Files
#   Receive [Images and 18 more]
#   ↳ Untick all but "Files"
#
# Step 5: Add a Run Shell Script Action
#   Action Library
#   ↳ Run Shell Script
#
# Step 6: Configure the Run Shell Script Action
#   Shell: [python3] (/usr/bin/python3)
#   Input: [Shortcut Input] (default)
#   Pass Input: [as arguments]
#   Run as Administrator: ◼️ (unticked)
#
# Step 7: Copy+Paste in the Python Script
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

import os
import re
import sys
from pathlib import PurePath

args = sys.argv[1:]

for arg in args:
    src = PurePath(arg)
    dst = src.with_stem(
        re.sub(r"\bv(\d{2})\b", r"0\1", src.stem)
    )
    if src != dst:
        print(f"Renaming {src} to {dst}")
        os.rename(src, dst)
    else:
        print(f"Skipping {src}")
