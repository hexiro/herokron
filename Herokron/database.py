import pathlib
import json
import re
from sys import platform

from heroku3 import from_key

from .exceptions import InvalidEmbedSettings

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

database_file.parents[0].mkdir(parents=True, exist_ok=True)
if not database_file.is_file():
    with database_file.open(mode="w") as file:
        # color is `Heroku Lavender` found at https://brand.heroku.com
        json.dump({"keys": [], "color": 0x7673C0, "webhook": ""}, file)


# we do these checks one time and hope that no one deletes the files :shrug:


class DatabaseUtility:
    """ Utility to make main module more readable, and interactions with the database more robust. """

    def __init__(self):
        self.database = json.loads(database_file.read_text(encoding="utf8"))

    def __getitem__(self, item):
        return self.database[item]

    def __setitem__(self, key, value):
        self.database[key] = value

    def __str__(self):
        # kind of a hacky solution to make printing database easy :shrug:
        return str(self.database)
    
    @property
    def keys(self):
        return [item["key"] for item in self.database["keys"]]

    @property
    def apps(self):
        return [item for sublist in [key["apps"] for key in self.database["keys"]] for item in sublist]

    @property
    def color(self):
        # ooooooooooooooh returns cleaaaaaaaaaaaaaan data
        return int(self.database["color"])

    @property
    def webhook(self):
        return self.database["webhook"]

    def dump(self):
        return database_file.write_text(json.dumps(self.database), encoding="utf8")

    def key_exists(self, key):
        return key in self.keys

    def match_key(self, key):
        for index, data in enumerate(self.database["keys"]):
            if data["key"] == key:
                return index, data

    def get_key(self, app):
        for item in self.database["keys"]:
            if app in item["apps"]:
                return item["key"]

    def get_apps(self, key):
        search = self.match_key(key)
        if search:
            return search[1]["apps"]

    def add_key(self, key):
        if not key in self.keys:
            self.database["keys"].append({"key": key, "apps": [app.name for app in from_key(key).apps()]})
            self.dump()
        return self.database

    def remove_key(self, key):
        search = self.match_key(key)
        if search:
            del self.database["keys"][search[0]]
            self.dump()
            return self.database

    def set_webhook(self, url):
        # p.s. this regex is blatantly ripped from https://github.com/kyb3r/dhooks
        # discord webhook api wrapper ^
        search = re.match("^(?:https?://)?((canary|ptb)\\.)?discord(?:app)?\\.com/api/webhooks/(?P<id>[0-9]+)/("
                          "?P<token>[A-Za-z0-9\\.\\-\\_]+)/?$", url)
        if not search:
            raise InvalidEmbedSettings("Error trying to update embed: Invalid Webhook.")
        url = "https://discord.com/api/webhooks/{id}/{token}".format(**search.groupdict())
        self.database["webhook"] = url
        self.dump()
        return self.database

    def set_color(self, color: str):
        # change #FFFFFF to FFFFFF
        if isinstance(color, str) and color.startswith("#"):
            color = color[1:]
        # convert from base 16 to base 10
        if not isinstance(color, int):
            color = int(color, 16)
        if 0 <= color <= 16777215:
            # 16777215 should be max value; 16777215 is FFFFFF in base 10
            self.database["color"] = color
            self.dump()
        else:
            raise InvalidEmbedSettings("Error trying to update embed: Invalid Color.")
        return self.database

    def sync_key(self, key):
        search = self.match_key(key)
        if search:
            index, data = search
            apps = [app.name for app in from_key(key).apps()]
            self.database["keys"][index]["apps"] = apps
            self.dump()
            return apps

    def sync_database(self):
        for key in self.keys:
            self.sync_key(key)
        return self.database
