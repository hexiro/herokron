import json
import pathlib
import re
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
        # color is `Heroku Lavender` found at https://brand.heroku.com
        database = {"keys": [], "color": 0x7673C0, "webhook": {}}
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

    @property
    def color(self):
        # ooooooooooooooh returns cleaaaaaaaaaaaaaan data
        return int(self.database["color"])

    @property
    def webhook(self):
        if {"id", "token"} <= self.database["webhook"].keys():
            # this clever line with horrible readability just checks if both `id` and `token` are present in the db.
            return "https://discord.com/api/webhooks/{id}/{token}".format(**self.database["webhook"])

    def dump(self):
        return self.database_file.write_text(json.dumps(self.database), encoding="utf8")

    def index_key(self, key):
        keys = self.keys
        for index in range(len(keys)):
            if key == keys[index]:
                return index

    def get_key(self, app):
        for item in self.database["keys"]:
            apps = list(item.values())[0]
            if app in apps:
                return list(item.keys())[0]

    def get_apps(self, key):
        if key in self.keys:
            return self.database["keys"][key]

    def add_key(self, key):
        if key not in self.keys:
            try:
                self.database["keys"].append({key: [app.name for app in heroku3.from_key(key).apps()]})
                self.dump()
            except HTTPError:
                raise DatabaseError(
                    "Invalid Heroku API Key. View your API Key(s) at: https://dashboard.heroku.com/account.")
        return self.database

    def remove_key(self, key):
        if key in self.keys:
            del self.database["keys"][self.index_key(key)]
            self.dump()
            return self.database

    def set_webhook(self, url):
        # p.s. this regex is blatantly ripped from https://github.com/kyb3r/dhooks
        # discord webhook api wrapper ^
        search = re.match("^(?:https?://)?((canary|ptb)\\.)?discord(?:app)?\\.com/api/webhooks/(?P<id>[0-9]+)/("
                          "?P<token>[A-Za-z0-9\\.\\-\\_]+)/?$", url)
        if not search:
            raise DatabaseError("Webhook passed doesn't match webhook format.")
        self.database["webhook"] = search.groupdict()
        self.dump()
        return self.database

    def set_color(self, color: str):
        # change #FFFFFF to FFFFFF
        if color.startswith("#"):
            color = color[1:]
        # convert from base 16 to base 10
        if len(color) == 6:
            color = int(color, 16)
        # change type to base 10 int
        else:
            color = int(color)
        if 0 <= color <= 16777215:
            # 16777215 should be max value; 16777215 is FFFFFF in base 10
            self.database["color"] = color
            self.dump()
        else:
            raise DatabaseError("Color passed isn't in base 16 or hexadecimal.")
        return self.database

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
        return self.database


database = Database()
