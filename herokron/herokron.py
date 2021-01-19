from json import load, dump
from sys import argv
from sys import platform
from os.path import expanduser
from os.path import abspath
from os.path import exists
from os import mkdir
from inspect import isfunction
from inspect import ismethod
from datetime import datetime
from argparse import ArgumentParser

from heroku3 import from_key
from dhooks import Embed
from dhooks import Webhook
from requests import HTTPError

from .exceptions import AppWithoutProcfile, InvalidWebhook
from .exceptions import InvalidAPIKey

home = expanduser('~')

if platform == "win32":
    database_directory = abspath(f"{home}/AppData/Roaming/Herokron")
elif platform == "linux":
    database_directory = abspath(f"{home}/.local/share/Herokron")
elif platform == "darwin":
    database_directory = abspath(f"{home}Library/Application Support/Herokron")
else:
    raise OSError("Unsupported OS. View Lines 24-30 and submit a pull request to add OS.")

database_file = abspath(f"{database_directory}/db.json")

if not exists(database_directory):
    mkdir(database_directory)

if not exists(database_file):
    dump({"keys": [], "color": 0x171516, "webhook": ""}, open(database_file, "x"))

database = load(open(database_file, "r"))
calls = []
returns = []


def log_embed(action, app):
    color = database["color"]
    if not isinstance(color, int):
        color = int(color, 16)
    log_embed = Embed(color=color)
    log_embed.add_field(name="Response", value="\n".join([f"{d}: {returns[-1][d]}" for d in returns[-1] if d != "app"]))
    log_embed.add_field(name="Action", value=action)
    log_embed.set_footer(text=f"{app}  |  {datetime.now():%b %d %I:%M %p}")
    return log_embed


class Herokron:

    def __init__(self, app=None):
        self.keys = [item["key"] for item in database["keys"]]
        if app is not None:
            if app not in apps_list():
                refresh_apps_list()
            if app in apps_list():
                self.heroku = from_key(key_from_app(app))
                self.app = self.heroku.app(app)
        if not hasattr(self, "heroku"):
            self.heroku = from_key(self.keys[0])
            self.app = self.heroku.app(self.heroku.apps()[0].name)
        if not self.app.process_formation():
            raise AppWithoutProcfile("App hasn't explicitly stated weather it's a worker or a web app.")
        self.proc_type = "worker" if "worker" in self.app.process_formation() else "web"

    def __getattribute__(self, name):
        returned = object.__getattribute__(self, name)
        if isfunction(returned) or ismethod(returned):
            calls.append(returned.__name__)
        return returned

    def state(self):
        """

        :return: The dict with one key `online` which will be T/F.
        """
        _is_on = {"online": bool(self.app.process_formation()[self.proc_type].quantity), "app": self.app.name}
        returns.append(_is_on)
        return _is_on

    def on(self):
        """

        :return: A dict with two keys `changed` and `online` which will be T/F.
        """
        _state = self.state()
        if _state["online"]:
            _on = {"changed": False, "online": True, "app": self.app.name}
            returns.append(_on)
            return _on
        self.app.process_formation()[self.proc_type].scale(1)
        _on = {"changed": True, "online": True, "app": self.app.name}
        returns.append(_on)
        return _on

    def off(self):
        """

        :return: A dict with two keys `changed` and `online` which will be T/F.
        """
        _state = self.state()
        if not _state["online"]:
            _off = {"changed": False, "online": False, "app": self.app.name}
            returns.append(_off)
            return _off
        self.app.process_formation()[self.proc_type].scale(0)
        _off = {"changed": True, "online": False, "app": self.app.name}
        returns.append(_off)
        return _off


def on(name):
    """

    :param name: The name of the Heroku app to change. If this name is not associated with any accounts specified in the local database, the first API key and first app will be used.
    :return: A dict with two keys `changed` and `online` which will be T/F.
    """
    return Herokron(name).on()


def off(name):
    """

    :param name: The name of the Heroku app to change. If this name is not associated with any accounts specified in the local database, the first API key and first app will be used.
    :return: A dict with two keys `changed` and `online` which will be T/F.
    """
    return Herokron(name).off()


def state(name):
    """
    :param name: The name of the Heroku app to change. If this name is not associated with any accounts specified in the local database, the first API key and first app will be used.
    :return: A dict with one key `online` which will be T/F.
    """
    return Herokron(name).state()


def apps_list():
    """

    :return: A list of all Heroku apps associated with the API keys set in the local database.
    """
    return [item for sublist in [key["apps"] for key in database["keys"]] for item in sublist]


def refresh_apps_list(write=True):
    """

    :return: A list of Heroku apps associated with the API keys set in the local database.
    """
    for key in database["keys"]:
        key = key["key"]
        refresh_apps(key, write)
    return apps_list()


def refresh_apps(key, write=True):
    """
    :param key: Heroku API Key
    :return: A list of all apps associated with `key`
    """
    search = list(filter(lambda keys: keys["key"] == key, database["keys"]))
    index = database["keys"].index(search[0])
    apps = [app.name for app in from_key(key).apps()]
    database["keys"][index]["apps"] = apps
    if write:
        dump_database()
    return apps


def key_from_app(name):
    """

    :param name: The name of the Heroku app to change. If this name is not associated with any accounts specified in the local database, the first API key and first app will be used.
    :return: A string containing the API key of the app. Should only be directly called by Herokron class to prevent tracebacks.
    """
    for num in range(len(database["keys"])):
        if name in database["keys"][num]["apps"]:
            return database["keys"][num]["key"]


def dump_database():
    dump(database, open(database_file, "w"))


def main():
    parser = ArgumentParser()
    parser.add_argument("-on",
                        help="Calls the `on` function to turn an app on.",
                        nargs="?",
                        default=False)
    parser.add_argument("-off",
                        help="Calls the `off` function to turn an app on.",
                        nargs="?",
                        default=False)
    parser.add_argument("-state",
                        help="Calls the `state` function view the current state of an app.",
                        nargs="?",
                        default=False)
    parser.add_argument("-apps-list",
                        help="Calls the `apps_list` function to view all connected apps.",
                        nargs="?",
                        default=False)
    parser.add_argument("--no-log",
                        nargs="?",
                        help="Stops this iteration from logging.",
                        default=False)
    parser.add_argument("--add-key",
                        "-add",
                        help="Adds the Heroku API key specified.",
                        default=False)
    parser.add_argument("--remove-key",
                        "-remove",
                        help="Removes the Heroku API key specified.",
                        default=False)
    parser.add_argument("--set-webhook",
                        "-webhook",
                        help="Sets the Discord Webhook URL for logging.",
                        default=False)
    parser.add_argument("--set-color",
                        "-color",
                        help="Sets the Discord Embed Color.",
                        default=False)
    parser.add_argument("--no-print",
                        help="Doesn't print stored values.",
                        nargs="?",
                        default=False)
    if len(argv) == 1:
        parser.print_help()
        return

    options = parser.parse_args()

    _add_key = options.add_key
    _remove_key = options.remove_key
    _webhook = options.set_webhook
    _color = options.set_color
    _no_log = options.no_log
    _no_print = options.no_print

    if _add_key:
        try:
            if not list(filter(lambda keys: keys["key"] == _add_key, database["keys"])):
                database["keys"].append({"key": _add_key, "apps": []})
                refresh_apps(_add_key, write=False)
        except HTTPError:
            raise InvalidAPIKey("Invalid Heroku API Key. View your API Key at: https://dashboard.heroku.com/account.")
    if _remove_key:
        search = list(filter(lambda keys: keys["key"] == _remove_key, database["keys"]))
        if search:
            del database["keys"][database["keys"].index(search[0])]
    if _webhook:
        database["webhook"] = _webhook
    if _color:
        database["color"] = int(_color, 16)
    if any([_add_key, _remove_key, _webhook, _color]):
        dump_database()
        if _no_print is False:
            print(database)

    _on = options.on
    _off = options.off
    _apps_list = options.apps_list
    _state = options.state

    if _on is not False:
        func = "on"
        app = _on
    elif _off is not False:
        func = "off"
        app = _off
    elif _apps_list is not False:
        func = "refresh_apps_list"
        app = None
    elif _state is not False:
        func = "state"
        app = _state
    else:
        return

    if func != "refresh_apps_list" and app is None:
        parser.print_help()
        return

    if app:
        _log = globals()[func](app)
    else:
        _log = globals()[func]()
    if _no_print is False:
        print(_log)
    if _no_log is False and func in ["on", "off"]:
        try:
            Webhook(database["webhook"]).send(
                embed=log_embed(
                    func,
                    app
                )
            )
            print(log_embed(func, app).to_dict())
        except ValueError:
            raise InvalidWebhook("Discord logging attempted with invalid webhook set in local database.")


if __name__ == "__main__":
    main()
