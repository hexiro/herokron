from sys import platform
from pathlib import Path


def get_datadir() -> Path:

    """
    Returns a parent directory path
    where persistent application data can be stored.

    # linux: ~/.local/share
    # macOS: ~/Library/Application Support
    # windows: C:/Users/<USER>/AppData/Roaming
    """

    home = Path.home()

    if platform == "win32":
        return home / "AppData/Roaming/Herokron"
    elif platform == "linux":
        return home / ".local/share/Herokron"
    elif platform == "darwin":
        return home / "Library/Application Support/Herokron"


def get_datafile() -> Path:
    return get_datadir() / ".env"


try:
    get_datadir().mkdir(parents=True)
except FileExistsError:
    pass
try:
    open(get_datafile(), "x").close()
except FileExistsError:
    pass