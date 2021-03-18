#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from argparse import ArgumentParser

import dhooks
import heroku3

from .database import DatabaseUtility
from .exceptions import AppError, DatabaseError


database = DatabaseUtility()


class Herokron:

    def __init__(self, app):
        """
        :param app: The name of the Heroku app in which you want to change
        :type app: str
        """

        # if it doesn't exist refresh database
        if app not in database.apps:
            database.sync_database()
        if app in database.apps:
            self.heroku = heroku3.from_key(database.get_key(app))
            self.app = self.heroku.app(app)

        # after a refresh if self.heroku still isn't defined
        else:
            raise AppError("App couldn't be found in the local database.")

        if not self.app.process_formation():
            raise AppError("App has not process types.")

        # In heroku, nodejs will often show up as both web and worker
        # it's kind of bad to assume it will be worker, so I might change that in the future.
        self.proc_type = "worker" if "worker" in self.app.process_formation() else "web"
        self.dynos = self.app.process_formation()[self.proc_type]

    @property
    def online(self):
        return bool(self.dynos.quantity)

    @property
    def offline(self):
        return not self.online

    def status(self):
        """
        :return: dictionary containing information about the app's status
        """
        return {
            "online": self.online,
            "app": self.app.name
        }

    def on(self):
        """
        Switches the app online, if it isn't already.
        :return: dictionary containing information about the app
        """
        completion_dict = {"online": True, "app": self.app.name}
        if self.online:
            return {"updated": False, **completion_dict}

        self.dynos.scale(1)
        return {"updated": True, **completion_dict}

    def off(self):
        """
        Switches the app offline, if it isn't already.
        :return: dictionary containing information about the app
        """
        completion_dict = {"online": False, "app": self.app.name}
        if self.offline:
            return {"updated": False, **completion_dict}

        self.dynos.scale(0)
        return {"updated": True, **completion_dict}


# shorthand functions

def on(app):
    """
    Switches the app online, if it isn't already.
    :param app: The name of the Heroku app in which you want to change
    :type app: str
    :return: dictionary containing information about the app
    """
    return Herokron(app).on()


def off(app):
    """
    Switches the app offline, if it isn't already.
    :param app: The name of the Heroku app in which you want to change
    :type app: str
    :return: dictionary containing information about the app
    """
    return Herokron(app).off()


def status(app):
    """
    :param app: The name of the Heroku app in which you want to change
    :type app: str
    :return: dictionary containing information about the app's status
    """
    return Herokron(app).status()


def main():
    """
    main function:
    0. used if __name__ == __main__
    1. used from command line herokron:main (console script)
    """
    parser = ArgumentParser()
    # we make the default False, so that if you don't give it an arg it will be `None` instead of `False`
    # if you know a better way of doing this lmk!
    parser.add_argument("-on",
                        help="Calls the `on` function to turn an app on.")
    parser.add_argument("-off",
                        help="Calls the `off` function to turn an app off.")
    parser.add_argument("-state",
                        help="Calls the `state` function view the current state of an app.")
    parser.add_argument("-apps",
                        help="Returns a list of all connected apps.",
                        nargs="?",
                        default=False)
    parser.add_argument("-keys",
                        help="Returns a list of all connected keys.",
                        nargs="?",
                        default=False)
    parser.add_argument("-database",
                        help="Returns a the raw database json.",
                        nargs="?",
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
    parser.add_argument("--no-log",
                        nargs="?",
                        help="Stops this iteration from logging.",
                        default=False)
    parser.add_argument("--no-print",
                        help="Stops this iteration from printing.",
                        nargs="?",
                        default=False)

    if len(sys.argv) == 1:
        parser.print_help()
        return

    options = parser.parse_args()

    # handle database updates

    _add_key = options.add_key
    _remove_key = options.remove_key
    _webhook = options.set_webhook
    _color = options.set_color
    _no_log = options.no_log
    _no_print = options.no_print

    # duplication checking is done inside `add_key` and `remove_key`.
    if _add_key:
        database.add_key(_add_key)
    if _remove_key:
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
    _state = options.state
    _database = options.database
    _apps = options.apps
    _keys = options.keys

    if _on:
        log = globals()["on"](_on)
    elif _off:
        log = globals()["off"](_off)
    elif _state:
        log = globals()["state"](_state)
    elif _database is not False:
        log = database
    elif _apps is not False:
        log = database.apps
    elif _keys is not False:
        log = database.keys
    else:
        # if a `state change` is not called there is nothing else to do past this point,
        # so we just return w/o consequences.
        return

    if _no_print is False:
        print(log)

    # if function is a state change, logging is allowed, and a discord webhook is set:
    if (isinstance(log, dict) and "updated" in log) and _no_log is False and database.webhook:
        # beyond this point we know log is a state change dict
        try:
            match_dict = {True: "🟢", False: "🔴"}  # TRUE: Large Green Circle, FALSE: Large Red Circle
            if log["online"]:
                previous = match_dict[not log["updated"]]
            else:
                previous = match_dict[log["updated"]]
            current = match_dict[log["online"]]
            log_embed = dhooks.Embed(
                title=log["app"],
                # `hair spaces` (small space unicode) in description to split the emojis apart in a nice manner.
                description=f"**STATE:⠀{previous}      →      {current}**\n"
                            "\n"
                            "View affected app:\n"
                            f"[heroku.com](https://dashboard.heroku.com/apps/{log['app']})",
                color=database.color
            )
            log_embed.set_timestamp(now=True)
            dhooks.Webhook(database.webhook).send(embed=log_embed)
        except ValueError:
            raise DatabaseError("Discord logging attempted with invalid webhook set in local database."
                                "If your webhook is valid, please open an issue at "
                                "https://github.com/Hexiro/Herokron.")


if __name__ == "__main__":
    main()
