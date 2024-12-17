# Use image optimize to compress images to 85% quality

from subprocess import run
from sys import argv

# MARK: Functions


def get_key(key: str):
    result = run(
        ["defaults", "read", "net.pornel.ImageOptim", key],
        capture_output=True,
        text=True,
    )
    print(result)
    return "false" if "does not exist" in result.stderr else result.stdout.strip()


def set_key(key: str, value: str):
    result = run(
        [
            "defaults",
            "write",
            "net.pornel.ImageOptim",
            key,
            "-bool" if value.lower() in ["true", "false", "yes", "no"] else "",
            value,
        ],
        capture_output=True,
        text=True,
    )
    print(result)
    return result.stdout.strip()


# Store the original values
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
LossyEnabledOriginal = get_key("LossyEnabled")
JpegOptimMaxQualityOriginal = get_key("JpegOptimMaxQuality")
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# Set the new values
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
set_key("LossyEnabled", "true")
set_key("JpegOptimMaxQuality", "85")
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# MARK: The Loop
args = argv[1:]
for arg in args:
    result = run(
        ["open", "-a", "ImageOptim", arg],
        # capture_output=True,
        # text=True,
    )
    print(result)

# Restore the ogirinal values
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
set_key("LossyEnabled", LossyEnabledOriginal)
set_key("JpegOptimMaxQuality", JpegOptimMaxQualityOriginal)
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
