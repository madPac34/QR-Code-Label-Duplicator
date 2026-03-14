"""Example runtime configuration for labelclone.

Copy this file to config.py and adapt values for your hardware.
"""

from pathlib import Path

# Optional fixed scanner event device, e.g. "/dev/input/event3".
# Leave as None to auto-detect from /dev/input/by-id/*event-kbd.
SCANNER_DEVICE = None

# Keyboard layout used by the scanner ("de" or "us").
KEYBOARD_LAYOUT = "de"

# Label printer raw device path.
PRINTER_DEVICE = "/dev/usb/lp0"

# Absolute or relative path to the ZPL template.
TEMPLATE_PATH = Path("/opt/labelclone/templates/label_template.zpl")

# Prevent immediate duplicate re-printing in this many seconds.
DUPLICATE_SUPPRESSION_SECONDS = 0.5
