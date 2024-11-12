# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# File: Rename Download
#
# ## External Dependencies
#   * https://pypi.org/project/titlecase/
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# MARK: Imports

from os import rename
from pathlib import Path
from re import search as re_search
from sys import argv

from titlecase import titlecase

# MARK: Constants

GOES_IN_SQUARE_BRACKETS = [
    r"\b\d{3,4}p\b",
    r"\bMP4(?:-\w+)?\b",
    r"\bDDC\b",
    r"\bx264\b",
    r"\bx265\b",
    r"\bXviD\b",
    r"\bHEVC\b",
    r"\bHDTV\b",
    r"\bWEB\b",
    r"\bWEBRip\b",
    r"\bWEB-?DL\b",
    r"\bXXX\b",
]

# MARK: Functions


# def six_to_eight_digit_date(m):
#     # Year, month, day
#     if 12 < m.group(3):
#         year = m.group(1)
#         month = m.group(2)
#         day = m.group(3)
#     # Month, day, year
#     elif 12 < m.group(2):
#         month = m.group(1)
#         day = m.group(2)
#         year = m.group(3)
#     # elif 12 < m.group(1):
#     #     year = m.group(3)
#     #     month = m.group(2)
#     #     day = m.group(1)
#     # The matched date, with the year expanded
#     return f"{year}-{month}-{day})"


# def get_release_group(str: str) -> str:
#     m = re_search(r"-([a-zA-Z0-9]+)$", str)
#     return m.group(1) if m else ""


def date_match_formatter(m):
    if m is None:
        return ""
    # yymmdd = 80-09-11
    year, month, day = m.groups()
    # mmddyy = 09-11-80
    if 32 <= day and month <= 12:
        year, month, day = month, day, year
    if 2 == len(year):
        year = f"20{year}"
    return f" {year}-{month}-{day} "


def spiff_it_up(str: str) -> str:
    str = str.replace(".", " ")
    # Resolution
    str = re_sub(r"\b(\d{3,4})p\b", r" \[\1p\] ", str)
    # 6 and 8 digit dates (YYMMDD  and YYYYMMDD)
    str = re_sub(r"\b(\d{2}\d{2}?)\D(\d{2})\D(\d{2})\b", date_match_formatter, str)
    str = titlecase(str)
    # Normalize each whitespace instance to a single space
    str = re_sub(r"\s", " ", str)
    str = str.strip()
    return str


# MARK: The Loop
# The variable here will actually be used in this script
args = argv[1:]
# Sort the arguments in reverse order so deeper paths are processed first
args.sort(reverse=True)
# See? (told you so)
for arg in args:
    src = Path(arg)
    dst = src

    if src.is_file():
        dst = dst.with_stem(spiff_it_up(dst.stem))
    else:
        dst = dst.with_name(spiff_it_up(dst.name))

    if src != dst:
        print(f"⬇️ {src.name}")
        print(f"⬆️ {dst.name}")
        rename(src, dst)
    else:
        print(f"♻️ {src.name}")
