from logging import NOTSET
from sys import exit
from os import environ
from inspect import isfunction
from inspect import ismethod
from datetime import datetime
from argparse import ArgumentParser

from dotenv import load_dotenv
from heroku3 import from_key
from dhooks import Embed
from dhooks import Webhook

from herokrondir import get_datafile


load_dotenv(get_datafile())
calls = []
returns = []


def log_message(func, title):
    hook = Webhook(environ["WEBHOOK"])
    log_embed = Embed(color=int(environ["COLOR"], 16))
    log_embed.add_field(name="Function", value=func)
    log_embed.add_field(name="Returned", value="\n".join([f"{d}: {returns[-1][d]}" for d in returns[-1]]))
    log_embed.set_footer(text=f"{title} • {datetime.now():%I:%M %p}")
    hook.send(embed=log_embed)


class Herokron:

    def __init__(self, name=None):
        self.keys = [environ[key] for key in [key for key in environ.keys() if key.startswith("HEROKU_KEY")]]
        if name is not None:
            for key in self.keys:
                if name in [app.name for app in from_key(key).apps()]:
                    self.heroku = from_key(key)
                    self.app = self.heroku.app(name)
                    break
        if not hasattr(self, "heroku"):
            self.heroku = from_key(self.keys[0])
            self.app = self.heroku.app(self.heroku.apps()[0].name)
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
        _is_on = {"online": bool(self.app.process_formation()[self.proc_type].quantity)}
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


def main():
    parser = ArgumentParser()
    parser.add_argument("func",
                        help="The name of the function to call.")
    parser.add_argument("app",
                        help="The name of the Heroku app.",
                        nargs="?",
                        default=None)
    options = parser.parse_args()
    print(options)
    _func = options.func
    _app = options.app
    if _func not in globals():
        parser.print_help()
        exit(1)
    if bool(_app) and _func in ["on", "off"]:
        print(globals()[_func](_app))
        if environ.get("WEBHOOK", None) is not None:
            log_message(_func, _app)
    elif bool(_app):
        print(globals()[_func](_app))
    else:
        print(globals()[_func]())


if __name__ == "__main__":
    main()
