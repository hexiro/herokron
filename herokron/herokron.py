import sys
from argparse import ArgumentParser

import heroku3
import requests.exceptions

from .exceptions import AppError
from .utils import format_data
from .utils.database import database


class Herokron:

    def __init__(self, app: str):
        """
        :param app: The name of the Heroku app in which you want to update
        :type app: str
        """

        # if it doesn't exist refresh database
        if app not in database.apps:
            database.sync_database()
        if app in database.apps:
            self.heroku = heroku3.from_key(database.key_from_app(app))
            self.app = self.heroku.app(app)
        # after a refresh if self.heroku still isn't defined
        else:
            raise AppError("App couldn't be found in the local database.")

        # might add `proc_type` param in future
        formation = self.app.process_formation()
        if not formation:
            raise AppError("App has no process types. (can't be turned on/off)")
        elif "worker" in formation:
            self.dynos = self.app.process_formation()["worker"]
        elif "web" in formation:
            self.dynos = self.app.process_formation()["web"]
        else:
            self.dynos = formation[0]

    @property
    def online(self):
        return self.dynos.quantity == 1

    @property
    def offline(self):
        return not self.online

    def status(self):
        """
        :return: dictionary containing information about the app's status
        """
        return {"online": self.online}

    def _scale(self, turn_on: bool):
        if turn_on and self.online:
            return {"online": True, "updated": False}
        if not turn_on and self.offline:
            return {"online": False, "updated": False}
        try:
            self.dynos.scale(int(turn_on))
            return {"online": turn_on, "updated": True}
        except requests.exceptions.HTTPError:
            database.sync_database()
            raise AppError("You don't have access to this app (deleted?)")

    def on(self):
        """
        Switches the app online, if it isn't already.
        :return: dictionary containing information about the app
        """
        return self._scale(turn_on=True)

    def off(self):
        """
        Switches the app offline, if it isn't already.
        :return: dictionary containing information about the app
        """
        return self._scale(turn_on=False)


# shorthand functions

def on(app: str):
    """
    Switches the app online, if it isn't already.
    :param app: The name of the Heroku app in which you want to change
    :type app: str
    :return: dictionary containing information about the app
    """
    return Herokron(app).on()


def off(app: str):
    """
    Switches the app offline, if it isn't already.
    :param app: The name of the Heroku app in which you want to change
    :type app: str
    :return: dictionary containing information about the app
    """
    return Herokron(app).off()


def status(app: str):
    """
    :param app: The name of the Heroku app in which you want to change
    :type app: str
    :return: dictionary containing information about the app's status
    """
    return Herokron(app).status()


def main():
    """
    main function:
    used from command line herokron:main (console script)
    """
    parser = ArgumentParser()
    # we make the default False, so that if you don't give it an arg it will be `None` instead of `False`
    # if you know a better way of doing this lmk!
    parser.add_argument("-on",
                        help="Calls the `on` function to turn an app on.")
    parser.add_argument("-off",
                        help="Calls the `off` function to turn an app off.")
    parser.add_argument("-status",
                        help="Calls the `status` function view the current status of an app.")
    parser.add_argument("--add-key",
                        help="Adds the Heroku API key specified.")
    parser.add_argument("--remove-key",
                        help="Removes the Heroku API key specified.")
    parser.add_argument("--database",
                        help="Prints the formatted database.",
                        action="store_true")
    parser.add_argument("--no-print",
                        help="Stops this iteration from printing.",
                        action="store_true")

    if len(sys.argv) == 1:
        parser.print_help()
        return

    options = parser.parse_args()

    # handle database updates

    _add_key = options.add_key
    _remove_key = options.remove_key
    _no_print = options.no_print
    _database = options.database

    # duplication checking is done inside `add_key` and `remove_key`.
    if _add_key:
        database.add_key(_add_key)
    if _remove_key:
        database.remove_key(_remove_key)
    # if anything that would warrant a database update exists, and printing is allowed
    if (_add_key or _remove_key or _database) and _no_print is False:
        # ehhh i don't like the database.database syntax
        # I'll have to work on that sometime.
        print(format_data(database.database))

    # handle status changes

    app = options.on or options.off or options.status

    turn_on = bool(options.on)
    turn_off = bool(options.off)
    check_status = bool(options.status)

    if turn_on:
        result = on(app)
    elif turn_off:
        result = off(app)
    elif check_status:
        result = status(app)
    else:
        # if a `status change` is not called there is nothing else to do past this point,
        # so we just return w/o consequences.
        return

    if _no_print is False:
        print(format_data(result))
