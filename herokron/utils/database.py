import json
import pathlib
import sys

import heroku3
from requests import HTTPError

from ..exceptions import DatabaseError


class Database:
    """ Utility to make main module more readable, and interactions with the database robust. """

    if sys.platform == "win32":
        database_file = pathlib.Path.home() / "AppData" / "Roaming" / "Herokron" / "db.json"
    elif sys.platform == "linux":
        database_file = pathlib.Path.home() / ".local" / "share" / "Herokron" / "db.json"
    elif sys.platform == "darwin":
        database_file = pathlib.Path.home() / "Library" / "Application Support" / "Herokron" / "db.json"
    else:
        raise OSError("Unsupported OS. Please inform maintainer(s) of what your sys.platform is, "
                      "or submit a pull request at: https://github.com/Hexiro/Herokron.")

    if not database_file.parent.exists():
        database_file.parent.mkdir()

    try:
        database = json.loads(database_file.read_text(encoding="utf8"))
    except (FileNotFoundError, json.JSONDecodeError):
        database = {"keys": []}
        database_file.write_text(data=json.dumps(database), encoding="utf8")

    def __getitem__(self, item):
        return self.database[item]

    def __setitem__(self, key, value):
        self.database[key] = value

    @property
    def keys(self):
        return [key for item in self.database["keys"] for key in item.keys()]

    @property
    def apps(self):
        # 1. Gets all `values` which is a list of all apps (ex. [["app_1", "app_2"], ["app_3", "app_4"]])
        # 2. Flattens the list (ex. ["app_1", "app_2", "app_3", "app_4"])
        # this could prob be made better but I can't think of how right now.
        return [e for sublist in (v for e in self.database["keys"] for v in e.values()) for e in sublist]

    def dump(self):
        return self.database_file.write_text(json.dumps(self.database), encoding="utf8")

    def index_key(self, key):
        for i, k in enumerate(self.keys):
            if key == k:
                return i

    def key_from_app(self, app):
        for item in self.database["keys"]:
            apps = list(item.values())[0]
            if app in apps:
                return list(item.keys())[0]

    def add_key(self, key):
        if key not in self.keys:
            try:
                self.database["keys"].append({key: [app.name for app in heroku3.from_key(key).apps()]})
                self.dump()
            except HTTPError:
                raise DatabaseError("Invalid Heroku API Key. "
                                    "View your API Key(s) at: https://dashboard.heroku.com/account.")

    def remove_key(self, key):
        if key in self.keys:
            del self.database["keys"][self.index_key(key)]
            self.dump()

    def sync_key(self, key):
        try:
            apps = [app.name for app in heroku3.from_key(key).apps()]
            self.database["keys"][self.index_key(key)][key] = apps
            self.dump()
            return apps
        except HTTPError:
            raise DatabaseError(
                "Invalid Heroku API Key. View your API Key(s) at: https://dashboard.heroku.com/account.")

    def sync_database(self):
        for key in self.keys:
            self.sync_key(key)


database = Database()
