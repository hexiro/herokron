from json import load, dump
from sys import exit, argv
from sys import platform
from os import environ
from inspect import isfunction
from inspect import ismethod
from datetime import datetime
from argparse import ArgumentParser
from pathlib import Path

from heroku3 import from_key
from dhooks import Embed
from dhooks import Webhook


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
    return get_datadir() / "db.json"


try:
    get_datadir().mkdir(parents=True)
except FileExistsError:
    pass
try:
    dump({"keys": [], "color": 0x4169e1, "webhook": ""}, open(get_datafile(), "x"))
except FileExistsError:
    pass


database = load(open(get_datafile()))
calls = []
returns = []


def log_message(func, title):
    hook = Webhook(environ["WEBHOOK"])
    log_embed = Embed(color=int(environ.get("COLOR", 171516), 16))
    log_embed.add_field(name="Function", value=func)
    log_embed.add_field(name="Returned", value="\n".join([f"{d}: {returns[-1][d]}" for d in returns[-1]]))
    log_embed.set_footer(text=f"{title} • {datetime.now():%I:%M %p}")
    hook.send(embed=log_embed)


class AppWithoutProcfile(Exception):
    pass


class Herokron:

    def __init__(self, app=None):
        self.keys = database["keys"]
        if app is not None:
            if app not in all_apps():
                refresh_all_apps()
            if app in all_apps():
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

    def apps_list(self):
        """

        :return: `apps_list` returns all Heroku apps associated with the API keys set in the .env.
        """
        _apps_list = [item.name for it in [app for app in [from_key(key).apps() for key in self.keys]] for item in it]
        returns.append(_apps_list)
        return _apps_list

    def is_on(self):
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
        _is_on = self.is_on()
        if _is_on["online"] :
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
        _is_on = self.is_on()
        if not _is_on["online"]:
            _off = {"changed": False, "online": False, "app": self.app.name}
            returns.append(_off)
            return _off
        self.app.process_formation()[self.proc_type].scale(0)
        _off = {"changed": True, "online": False, "app": self.app.name}
        returns.append(_off)
        return _off


def apps_list():
    """

    :return: `apps_list` returns all Heroku apps associated with the API keys set in the .env.
    """
    return Herokron().apps_list()


def on(name):
    """

    :param name: The name of the Heroku app to change. If name is not associated with any account set in the .env, the first key and first app will be used.
    :return: A dict with two keys `changed` and `online` which will be T/F.
    """
    return Herokron(name).on()


def off(name):
    """

    :param name: The name of the Heroku app to change. If name is not associated with any account set in the .env, the first key and first app will be used.
    :return: A dict with two keys `changed` and `online` which will be T/F.
    """
    return Herokron(name).off()


def is_on(name):
    """
    :param name: The name of the Heroku app to change. If name is not associated with any account set in the .env, the first key and first app will be used.
    :return: A dict with one key `online` which will be T/F.
    """
    return Herokron(name).is_on()


def refresh_all_apps(write=True):
    for key in database["keys"]:
        key = key["key"]
        refresh_apps(key, write)
    return all_apps()


def refresh_apps(key, write=True):
    search = list(filter(lambda keys: keys["key"] == key, database["keys"]))
    index = database["keys"].index(search[0])
    apps = [app.name for app in from_key(key).apps()]
    database["keys"][index]["apps"] = apps
    if write:
        dump_database()
    return apps


def all_apps():
    return [item for sublist in [key["apps"] for key in database["keys"]] for item in sublist]


def key_from_app(app):
    for num in range(len(database["keys"])):
        if app in database["keys"][num]["apps"]:
            return database["keys"][num]["key"]


def dump_database():
    dump(database, open(get_datafile(), "w"))


def main():
    parser = ArgumentParser()
    parser.add_argument("-func",
                        help="The name of the function to call.",
                        nargs="?",
                        default=None)
    parser.add_argument("-app",
                        help="The name of the Heroku app.",
                        nargs="?",
                        default=None)
    parser.add_argument("--no-log",
                        "-nl",
                        nargs="?",
                        help="Stops this iteration from logging.",
                        default=False)
    parser.add_argument("--add-key",
                        "-a",
                        help="Adds the Heroku API key specified.",
                        default=False)
    parser.add_argument("--remove-key",
                        "-r",
                        help="Removes the Heroku API key specified.",
                        default=False)
    parser.add_argument("--set-webhook",
                        "-w",
                        help="Sets the Discord Webhook URL for logging.",
                        default=False)
    parser.add_argument("--set-color",
                        "-c",
                        help="Sets the Discord Embed Color.",
                        default=False)
    parser.add_argument("--no-print",
                        "-p",
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
    _no_print = options.no_print

    if _add_key:
        if not list(filter(lambda keys: keys["key"] == _add_key, database["keys"])):
            database["keys"].append({"key": _add_key, "apps": []})
            refresh_apps(_add_key, write=False)
    if _remove_key:
        search = list(filter(lambda keys: keys["key"] == _remove_key, database["keys"]))
        if search:
            del database["keys"][database["keys"].index(search[0])]
    if _webhook:
        database["webhook"] = _webhook
    if _color:
        database["color"] = _color
    if any([_add_key, _remove_key, _webhook, _color]):
        dump_database()
        if _no_print is False:
            print(database)

    _func = options.func
    _app = options.app
    _no_log = options.no_log

    if _app and _func in ["on", "off"]:
        if _no_print is False:
            print(globals()[_func](_app))
        if database["webhook"]:
            if _no_log is not False:
                log_message(_func, _app)
    elif _app:
        print(globals()[_func](_app))
    elif _func:
        print(globals()[_func]())


if __name__ == "__main__":
    main()
