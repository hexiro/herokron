## Herokron


Herokron is an app used to make updating [Heroku](https://heroku.com/) apps easy especially between accounts. I made this to be used as a cron job hence the ending *kron*, so the main used of this is from the command line, but the file can also be imported. Optionally, all on/off state changes called from the command line are logged in a discord server by a webhook.

![Forks](https://img.shields.io/github/forks/Hexiro/Herokron)
![Stars](https://img.shields.io/github/stars/Hexiro/Herokron)
![Issues](https://img.shields.io/github/issues/Hexiro/Herokron)
![License](https://img.shields.io/github/license/Hexiro/Herokron)

![Herokron Webhook Example](https://i.imgur.com/oZr8Nbr.png)


## 📦 Installation

Install the package with pip.

```console
pip3 install git+https://github.com/Hexiro/Herokron@main
```


## 💾 Setup

Use the setup script to load values. Supply all the keys you have, there is no limit.
```console
$ Herokron-Setup --add-key {key} 
$ Herokron-Setup -w {discord_webhook}
$ Herokron-Setup -c {discord_embed_color}
```
To make sure everything works properly, run:
```console
$ Herokron-Setup --print
```
Then, your output should look something like this:
```javascript 
ex.
{'HEROKU_KEY': key1}
{'HEROKU_KEY': key2}
{'HEROKU_KEY': key3}
{'COLOR': 'ff0000'}
{'WEBHOOK': 'https://discord.com/api/webhooks/channel/token'}
```

## 📈 Usage

#### Command Line
```console
herokron function [app]
```

#### Import
```Python
import Herokron
Herokron.function("app")
```

## 📝 Documentation
```python
# Changes state of Heroku app to `on`.
Herokron on [app] # command line
Herokron.on(app) # .py
>>> {"changed": bool, "online": boll, "app": str}
```
```Python
# Changes state of Heroku app to `off`.
Herokron off [app] # command line
Herokron.off(app) # .py
>>> {"changed": bool, "online": boll, "app": str}
```
```Python
# Returns the current state of the Heroku app.
Herokron is_on [app] # command line
Herokron.is_on(app) # .py
>>> {"online": bool, "app": str}
```
```Python
# Returns all the apps associated with all the Heroku API keys provided.
Herokron apps_list # command line
Herokron.apps_list() # .py
>>> [app1, app2, app3]
```


## Contributing
Pull requests are always 100% welcomed and appreciated. Some possible areas of improvement would be caching which key correlates to which app to prevent unnecessary API calls, and optimizing how the get_datafile function is used so it isn't written twice.