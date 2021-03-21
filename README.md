## Herokron

Herokron is a python package used to make switching [Heroku](https://heroku.com/) apps on/off easy, especially between accounts. The primary use case is from the command line in the form of a cron job (hence the ending *kron*), but Herokron does work in a python file. Optionally, all on/off status changes called from the command line are logged in a discord server by a webhook.

![Forks](https://img.shields.io/github/forks/Hexiro/Herokron)
![Stars](https://img.shields.io/github/stars/Hexiro/Herokron)
![Issues](https://img.shields.io/github/issues/Hexiro/Herokron)
![License](https://img.shields.io/github/license/Hexiro/Herokron)

![Herokron Webhook Example](https://i.imgur.com/42O2mbP.png)


## 📦 Installation

Install the package with pip.

```
pip3 install git+https://github.com/Hexiro/Herokron
```


## 💾 Setup

Load API keys, and setup logging
```console
$ Herokron --add-key {key} 
$ Herokron --set-webhook {discord_webhook}
$ Herokron --set-color {discord_embed_color}
```
View the database to make sure everything is working.
```console
$ Herokron -database
```

##  Usage

### 🖥️ Command Line

```console
$ Herokron --help
```
app commands (classified by leading -)
```console
  -on ON                		Calls the `on` function to turn an app on.
  -off OFF              		Calls the `off` function to turn an app off.
  -status STATUS        		Calls the `status` function view the current status of an app.
```
database commands (classified by leading --)
```
  --database [DATABASE]  		Prints the formatted database.
  --add-key ADD_KEY     		Adds the Heroku API key specified.
  --remove-key REMOVE_KEY		Removes the Heroku API key specified.            
  --set-webhook SET_WEBHOOK		Sets the Discord Webhook URL for logging.                    
  --set-color SET_COLOR			Sets the Discord Embed Color.
  --no-log [NO_LOG]     		Stops this iteration from logging.
  --no-print [NO_PRINT]			Stops this iteration from printing.
```

### Python

app commands
```py
import herokron
herokron.on("herokron-example")
herokron.off("herokron-example")
herokron.status("herokron-example")
```

while they function correctly, it's not exactly practical because the database is still loaded from the database file so that has to be set before hand.

# ⌛ Cron
The following example will start a Heroku app everyday at 8 am.

### crontab
```
0 8 * * * herokron -on [app]
```

If this isn't working, cron is most likely just having issues finding Herokron. If this happens, you will need to specify the Herokron path. 

### command line
```
$ which herokron
/home/pi/.local/bin/herokron
```
### crontab
```
0 8 * * * /home/pi/.local/bin/herokron -on [app]
```


# Contributing
Pull requests are always 100% welcomed and appreciated. Right now, I have no way of Testing Mac OS and other Linux distributions. All modern operating systems should work. Operation system is only used to find the local database file.