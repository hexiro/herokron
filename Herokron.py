from sys import argv
from os import environ
from inspect import isfunction
from inspect import ismethod
from datetime import datetime

from dotenv import load_dotenv
from heroku3 import from_key
from discord.ext import commands
from discord.ext import tasks
from discord.utils import get
from discord import Embed


load_dotenv()
calls = []
returns = []


class DiscordLogger(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix="!",
            help_command=None)

    async def on_ready(self):
        self.log_message.start()

    @tasks.loop(count=1)
    async def log_message(self):
        channel = get(self.get_all_channels(), guild__name=environ["DISCORD_GUILD"], name=environ["DISCORD_CHANNEL"])
        log_embed = Embed(color=int(environ["DISCORD_COLOR"], 16))
        log_embed.add_field(name="Function", value=self.func)
        log_embed.add_field(name="Returned", value="\n".join([f"{d}: {returns[-1][d]}" for d in returns[-1]]))
        log_embed.set_footer(text=f"test-heroku-app • {datetime.now():%I:%M %p}")
        await channel.send(embed=log_embed)

    @log_message.after_loop
    async def after_log(self):
        try:
            await self.close()
        except RuntimeError:
            pass

    def startup(self, func, param):
        self.func = func
        self.title = param
        self.run(environ["DISCORD_TOKEN"])


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
            _on = {"changed": False, "online": True}
            returns.append(_on)
            return _on
        self.app.process_formation()[self.proc_type].scale(1)
        _on = {"changed": True, "online": True}
        returns.append(_on)
        return _on

    def off(self):
        """

        :return: A dict with two keys `changed` and `online` which will be T/F.
        """
        _is_on = self.is_on()
        if not _is_on["online"]:
            _off = {"changed": False, "online": False}
            returns.append(_off)
            return _off
        self.app.process_formation()[self.proc_type].scale(0)
        _off = {"changed": True, "online": False}
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


if __name__ == '__main__':
    func = argv[1]
    if len(argv) == 2:
        print(globals()[func]())
    else:
        param = argv[2]
        print(globals()[func](param))
        if func in ["on", "off"]:
            DiscordLogger().startup(func, param)
print('*splooges*')
