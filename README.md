A Mastodon bot to forward anonymous messages to their recipient, *à la* Curious Cat or NGL. 

# Receiving messages from Shy Raccoon

1. Follow the Shy Raccoon account on the fediverse
2. Instruct your followers to send their messages to the Shy Racoon account, in private message, mentioning you. 
3. That's it

# Sending anonymous messages using Shy Raccon

1. Send a private message to the Shy Raccoon account that includes the full username of the person you want the question to be forwarded to
2. That's it!

# Safety features

- Shy Raccoon is opt-in based: you need to follow the bot to start receiving anonymous messages
- Messages are rate-limited and a given user won't be able to send more than a couple dozen messages a day by default
- If you receive an abusive or hateful question, simply answer the bot a message that contain the hashtag "#report" (this is configurable). A human will take over to ensure this person can't reach you again, as well as reporting them if necessary.

# Hosting your own Shy Raccoon

## Create a Mastodon account for the bot

Chose any instance you'd like, but ensure they are okay to host this kind of bot.

## Create a Mastodon App

With the following scopes :

- read
- write:statuses
- write:bookmarks (to bookmark reported statuses)
- push

Grab the access token for later.

## Get the code

```bash
cd ~
git clone https://github.com/agateblue/shy-raccoon.git
cd shy-raccoon

# create a python virtualenv
python3 -m venv venv

# install the project and its dependencies
venv/bin/pip install '.'
```

## Configuration file

Configuration is done through environment variables. In a production environment, we use an `.env` file to store them.

```bash
cp env.sample .env

# Add necessary values
nano .env
```

## Systemd unit

To ensure the bot is started automatically with the system and restarted in case of a crash, we recommand using systemd. 

```bash
sudo cp shy-raccoon.service /etc/systemd/system/

# Tweak the unit as needed, especially the path to your shy-raccoon install
sudo nano /etc/systemd/system/shy-raccoon.service

# Reload the configuration
sudo systemctl daemon-reload
sudo systemctl enable shy-raccoon.service
sudo systemctl start shy-raccoon.service
```

## Upgrading

If you want to run an updated version of the code:

```bash
cd ~/shy-raccoon
# pull changes from the repo
git pull
# reinstall the project and its dependencies
venv/bin/pip install '.'
# restart the service
sudo systemctl restart shy-raccoon.service
```

# Contribute to the project

Initial setup :

```bash
# git clone then
cd shy-raccoon

# create a python virtualenv
python3 -m venv venv

# install the project in dev mode
venv/bin/pip install -e '.[dev]'
```

Running the project:

```bash
export ACCESS_TOKEN=yourtoken SERVER_URL='https://mastodon.cafe'
# launch Shy Raccoon
venv/bin/shy-raccoon stream
```