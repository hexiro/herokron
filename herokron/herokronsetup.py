from sys import platform
from sys import argv
from dotenv import dotenv_values
from argparse import ArgumentParser
from pathlib import Path


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
    return get_datadir() / ".env"


try:
    get_datadir().mkdir(parents=True)
except FileExistsError:
    pass
try:
    open(get_datafile(), "x").close()
except FileExistsError:
    pass


def main():
    parser = ArgumentParser()
    parser.add_argument("--add-key",
                        "-ak",
                        help="Adds the Heroku API key specified.",
                        default=False)
    parser.add_argument("--remove-key",
                        "-rk",
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
    parser.add_argument("--print",
                        "-p",
                        help="Prints stored values.",
                        nargs="?",
                        default=False) 
    if len(argv) == 1:
        parser.print_help()
        return
    
    options = parser.parse_args()
    env_keys = dotenv_values(get_datafile())
    values = [[key, env_keys[key]] for key in env_keys]
    keys = [sublist[0] for sublist in values]

    _add_key = options.add_key
    _remove_key = options.remove_key
    _webhook = options.set_webhook
    _color = options.set_color
    _print = options.print

    if bool(_add_key):
        values.append([f"HEROKU_KEY_{_add_key.replace('-', '_')}".upper(), _add_key])
    if bool(_remove_key):
        if f"HEROKU_KEY_{_remove_key.replace('-', '_')}".upper() in keys:
            del values[keys.index(f"HEROKU_KEY_{_remove_key.replace('-', '_')}".upper())]
    if bool(_webhook):
        if "WEBHOOK" in keys:
            values[keys.index("WEBHOOK")][1] = _webhook
        else:
            values.append(["WEBHOOK", _webhook])
    if bool(_color):
        if "COLOR" in keys:
            values[keys.index("COLOR")][1] = _color
        else:
            values.append(["COLOR", _color])
    with open(get_datafile(), "w") as file:
        for key, value in values:
            file.write(f"{key}={value}\n")
    if _print is None:
        for key, value in values:
            if key.startswith("HEROKU_KEY"):
                print({"HEROKU_KEY": value})
            else:
                print({key: value})

if __name__ == "__main__":
    main()
