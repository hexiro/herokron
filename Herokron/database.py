import pathlib
import json
from sys import platform


# one time setup

home = pathlib.Path.home()

if platform == "win32":
    database_file = home / "AppData" / "Roaming" / "Herokron" / "db.json"
elif platform == "linux":
    database_file = home / ".local" / "share" / "Herokron" / "db.json"
elif platform == "darwin":
    database_file = home / "Library" / "Application Support" / "Herokron" / "db.json"
else:
    raise OSError("Unsupported OS. View Lines 24-30 and submit a pull request to add OS,"
                  "or inform maintainer(s) of what your sys.platform is.")

database_file.parents[0].mkdir(exist_ok=True)
if not database_file.is_file():
    with database_file.open(mode="w") as file:
        json.dump({"keys": [], "color": 0x171516, "webhook": ""}, file)


def load_database():
    return json.loads(database_file.read_text(encoding="utf8"))


def dump_database(database):
    return database_file.write_text(json.dumps(database), encoding="utf8")
