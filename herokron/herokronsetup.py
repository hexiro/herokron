from dotenv import dotenv_values
from pprint import pprint
from argparse import ArgumentParser


def main():
    values = [[key, dotenv_values()[key]] for key in dotenv_values()]
    parser = ArgumentParser()
    parser.add_argument("--heroku-num", type=str, default=False)
    parser.add_argument("--heroku-key", type=str, default=False)
    parser.add_argument("--discord-webhook", type=str, default=False)
    parser.add_argument("--discord-color", type=str, default=False)
    options = parser.parse_args()
    _heroku_key = options.heroku_key
    _heroku_num = options.heroku_num
    _discord_webhook = options.discord_webhook
    _discord_color = options.discord_color
    keys = [sublist[0] for sublist in values]
    if bool(_heroku_key) != bool(_heroku_num):
        parser.print_help()
    if bool(_heroku_num) and not _heroku_num.isdigit():
        parser.print_help()
    if bool(_heroku_key):
        print('Bruh')
        if f"HEROKU_KEY{_heroku_num}" in keys:
            values[keys.index(f"HEROKU_KEY{_heroku_num}")][1] = _heroku_key
        else:
            values.append([f"HEROKU_KEY{_heroku_num}", _heroku_key])
    if bool(_discord_webhook):
        if "DISCORD_WEBHOOK" in keys:
            values[keys.index("DISCORD_WEBHOOK")][1] = _discord_webhook
        else:
            values.append(["DISCORD_WEBHOOK", _discord_webhook])
    if bool(_discord_color):
        if "DISCORD_COLOR" in keys:
            values[keys.index("DISCORD_COLOR")][1] = _discord_color
        else:
            values.append(["DISCORD_COLOR", _discord_color])
    pprint(values)
    with open(".env", "w") as file:
        for key, value in values:
            file.write(f"{key}={value}\n")


if __name__ == "__main__":
    main()
