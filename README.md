## Herokron


Herokron is an app used to make updating [Heroku](https://heroku.com/) apps easy especially between accounts. I made this to be used as a cron job hence the ending *kron*, so the main used of this is from the command line, but the file can also be imported. All on/off state changes called from the command line are logged in a discord server by a bot.

![Forks](https://img.shields.io/github/forks/Hexiro/Herokron)
![Stars](https://img.shields.io/github/stars/Hexiro/Herokron)
![Issues](https://img.shields.io/github/issues/Hexiro/Herokron)
![License](https://img.shields.io/github/license/Hexiro/Herokron)

## 📦 Installation

Clone the [GitHub](https://github.com/Hexiro/Herokron) repository.


    $ git clone https://github.com/Hexiro/Herokron/
    $ cd Herokron
    $ pip3 install -r requirements.txt


## 💾 Setup

Use the setup script to load values. Supply all the keys you have, there is no limit.
```
$ Herokron-Setup --add-key {key} 
$ Herokron-Setup -w {discord_webhook}
$ Herokron-Setup -c {discord_embed_color}
```
To make sure everything works properly, run:
```
$ Herokron-Setup --print
```
Then, your output should look something like this
```
ex.
{'HEROKU_KEY': key1}
{'HEROKU_KEY': key2}
{'HEROKU_KEY': key3}
{'COLOR': 'ff0000'}
{'WEBHOOK': 'https://discord.com/api/webhooks/channel/token'}
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