## Herokron


Herokron is a python package used to make updating [Heroku](https://heroku.com/) apps easy especially between accounts. I made this to be used as a cron job hence the ending *kron*, so the main used of this is from the command line, but the file can also be imported. Optionally, all on/off state changes called from the command line are logged in a discord server by a webhook.

![Forks](https://img.shields.io/github/forks/Hexiro/Herokron)
![Stars](https://img.shields.io/github/stars/Hexiro/Herokron)
![Issues](https://img.shields.io/github/issues/Hexiro/Herokron)
![License](https://img.shields.io/github/license/Hexiro/Herokron)

![Herokron Webhook Example](https://i.imgur.com/o8Tmdxh.png)


## 📦 Installation

Install the package with pip.

```
pip3 install git+https://github.com/Hexiro/Herokron
```


## 💾 Setup

Supply all the keys you have, there is no limit.
```console
$ Herokron --add-key {key} 
$ Herokron --set-webhook {discord_webhook}
$ Herokron --set-color {discord_embed_color}
```
View all loaded apps to make sure everything is working.
```console
$ Herokron -apps-list
>>> ["app_one", "app_two", "..."]
```

## 📝 Usage
```python
# Changes state of Heroku app to `on`.
Herokron -on [app] # command line
Herokron.on(app) # .py
>>> {"changed": bool, "online": bool, "app": str}
```
```Python
# Changes state of Heroku app to `off`.
Herokron -off [app] # command line
Herokron.off(app) # .py
>>> {"changed": bool, "online": bool, "app": str}
```
```Python
# Returns the current state of the Heroku app.
Herokron -state [app] # command line
Herokron.state(app) # .py
>>> {"online": bool, "app": ""}
```
```Python
# Returns all the apps associated with all the Heroku API keys provided.
Herokron -apps-list # command line
Herokron.apps_list() # .py
>>> ["app_one", "app_two", "..."]
```

# ⌛ Cron
If you find that this app isn't working with cron you will need to specify the Herokron path. In the following example the cron job specified will run everyday at 8 am.

### console
```
$ which herokron
/home/pi/.local/bin/herokron
```
### crontab
```
0 8 * * * python3 /home/pi/.local/bin/herokron -on [app]
```


# Contributing
Pull requests are always 100% welcomed and appreciated. Right now I have no way of Testing Mac OS, and other linux distributions. All modern operating systems should work, as operating system is only needed to find database file location. 