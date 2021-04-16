"""
Module init file

Emil Rekola <emil.rekola@hotmail.com>
"""

from pathlib import Path
from importlib import metadata

VERSION = None

# Read version on startup
_version_file = Path(__file__).parent.parent / "VERSION"

# If package was not installed -> read file
if _version_file.exists():
    VERSION = _version_file.open("r").readline().strip()

# Package was installed -> read version from installation metadata
else:
    VERSION = metadata.version("Cryptalert")
