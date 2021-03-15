from sys import argv
from argparse import ArgumentParser

from dhooks import Webhook, Embed
from heroku3 import from_key
from requests import HTTPError

from .database import DatabaseUtility
from .exceptions import AppWithoutProcfile, InvalidAPIKey, InvalidEmbedSettings, AppNotFound


database = DatabaseUtility()


class Herokron:

    def __init__(self, app=None):
        if app is not None:
            # if it doesn't exist refresh database
            if app not in database.apps:
                database.sync_database()
            if app in database.apps:
                self.heroku = from_key(database.get_key(app))
                self.app = self.heroku.app(app)

        if not hasattr(self, "heroku"):
            raise AppNotFound("App couldn't be found in the local database.")

        if not self.app.process_formation():
            raise AppWithoutProcfile("App hasn't explicitly stated weather it's a worker or a web app.")

        # In heroku, nodejs will often show up as both web and worker.
        # it's kind of bad to assume it will be worker so I might change that in the future.
        self.proc_type = "worker" if "worker" in self.app.process_formation() else "web"
        self.dynos = self.app.process_formation()[self.proc_type]

    @property
    def online(self):
        return bool(self.dynos.quantity)

    @property
    def offline(self):
        return not self.online

    def state(self):
        """
        :return: The dict with one key `online` which will be T/F.
        """
        return {
            "online": self.online,
            "name": self.app.name
        }

    def on(self):
        """
        :return: A dict with two keys `changed` and `online` which will be T/F.
        """
        completion_dict = {"online": True, "app": self.app.name}
        if self.online:
            return {"changed": False, **completion_dict}

        self.dynos.scale(1)
        return {"changed": True, **completion_dict}

    def off(self):
        """
        :return: A dict with two keys `changed` and `online` which will be T/F.
        """
        completion_dict = {"online": False, "app": self.app.name}
        if self.offline:
            return {"changed": False, **completion_dict}

        self.dynos.scale(0)
        return {"changed": True, **completion_dict}


def on(name: str):
    """
    :param name: The name of the Heroku app to change. If this name is not associated with any accounts specified in the local database, the first API key and first app will be used.
    :return: A dict with two keys `changed` and `online` which will be T/F.
    """
    return Herokron(name).on()


def off(name: str):
    """
    :param name: The name of the Heroku app to change. If this name is not associated with any accounts specified in the local database, the first API key and first app will be used.
    :return: A dict with two keys `changed` and `online` which will be T/F.
    """
    return Herokron(name).off()


def state(name: str):
    """
    :param name: The name of the Heroku app to change. If this name is not associated with any accounts specified in
    the local database, the first API key and first app will be used.
    :return: A dict with one key `online` which
    will be T/F.
    """
    return Herokron(name).state()


def main():
    parser = ArgumentParser()
    parser.add_argument("-on",
                        help="Calls the `on` function to turn an app on.")
    parser.add_argument("-off",
                        help="Calls the `off` function to turn an app off.")
    parser.add_argument("-state",
                        help="Calls the `state` function view the current state of an app.")
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

    # handle updates

    _add_key = options.add_key
    _remove_key = options.remove_key
    _webhook = options.set_webhook
    _color = options.set_color
    _no_log = options.no_log
    _no_print = options.no_print

    if _add_key:
        try:
            if not database.key_exists(_add_key):
                database.add_key(_add_key)
        except HTTPError:
            raise InvalidAPIKey("Invalid Heroku API Key. View your API Key(s) at: https://dashboard.heroku.com/account.")
    if _remove_key:
        if database.key_exists(_remove_key):
            database.remove_key(_remove_key)
    if _webhook:
        database.set_webhook(_webhook)
    if _color:
        database.set_color(_color)
    if any({_add_key, _remove_key, _webhook, _color}) and _no_print is False:
        print(database)

    # handle state changes

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
    elif _state is not False:
        func = "state"
        app = _state

    if any({_on, _off, _state}):
        # this wont be referenced before assesment
        # we only make it this far if the func and app is set
        # even though technically we don't have an else to ensure it's set.
        if app is None:
            parser.print_help()
            return
        _log = globals()[func](app)

        if _no_print is False:
            print(_log)
        # if function is a state change, logging is allowed, and a discord webhook is set:
        if func in {"on", "off"} and _no_log is False and database.webhook:
            try:
                if func == "on":
                    previous = "🔴" if _log["changed"] else "🟢"   # off, on
                else:
                    previous = "🟢" if _log["changed"] else "🔴"   # on, off
                current = "🟢" if _log["online"] else "🔴"
                log_embed = Embed(
                    title=_log["app"],
                    description=f"**STATE:⠀{previous} → {current}**\n"
                                "\n"
                                "View affected app:\n"
                                f"[heroku.com](https://dashboard.heroku.com/apps/{_log['app']})",
                    color=database.color
                )
                log_embed.set_timestamp(now=True)
                Webhook(database.webhook).send(embed=log_embed)
            except ValueError:
                raise InvalidEmbedSettings("Discord logging attempted with invalid webhook set in local database."
                                           "If your webhook is valid, please open an issue at "
                                           "https://github.com/Hexiro/Herokron.")
    elif _apps_list is not False:
        apps = list(database.apps)
        if _no_print is False:
            print(apps)


if __name__ == "__main__":
    main()
