## Herokron


Herokron is an app used to make updating [Heroku](https://heroku.com/) apps easy especially between accounts. I made this to be used as a cron job hence the ending *kron*, so the main used of this is from the command line, but the file can also be imported. All on/off state changes called from the command line are logged in a discord server by a bot.

## Badges
![Issues](https://img.shields.io/github/issues/Hexiro/Herokron)
![Forks](https://img.shields.io/github/forks/Hexiro/Herokron)
![Stars](https://img.shields.io/github/stars/Hexiro/Herokron)
![License](https://img.shields.io/github/license/Hexiro/Herokron)

## 📦 Installation & Setup

Clone the [GitHub](https://github.com/Hexiro/Herokron) repository.


    $ git clone https://github.com/Hexiro/Herokron/
    $ cd Herokron
    $ pip3 install -r requirements.txt


Herokron uses a .env file to load Heroku/Discord API keys. Feel free to hard code these values into your code to remove a dependency. It's laid out this way so you easily know what values you have to edit in a separate file.

    # heroku keys (more can be added)
    HEROKU_KEY1=aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa
    HEROKU_KEY2=bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb
    HEROKU_KEY3=cccccccc-cccc-cccc-cccc-cccccccccccc
    DISCORD_BOT_TOKEN=AaAaAAA1AAAaAAA1AAAaAaA1.A1aA1A.A...

    # discord.py
    DISCORD_GUILD=Server 1 
    DISCORD_CHANNEL=general
    DISCORD_COLOR = 3d3d3d

Make sure all Heroku API keys work by listing all apps
```python
 python3 Herokron.py apps_list
```

## 📈 Usage

#### Command Line

Herokron doesn't use optparse, instead it calls functions with args provided with sys.argv.

```python
python3 Herokron.py on/off/is_on/ "name"
```
#### Import
```Python
import Herokron
Herokron.on("name")
Herokron.off("name")
Herokron.is_on("name")
```

## 🤖 Discord Embed Preview
![Discord Embed Preview](https://thigh.pics/6c02BAc.png)


## Contributing
Pull requests are always 100% welcomed and appreciated. Some possible areas of improvement are the discord logging section and the command line could be made into optparse.