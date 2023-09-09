A Mastodon bot to forward anonymous questions to their recipient, *à la* Curious Cat or NGL. 

# Receiving questions from Shy Raccoon

1. Follow the Shy Raccoon account on the fediverse
2. Instruct your followers to send their questions to the Shy Racoon account, in private message, mentioning you. 
3. That's it

# Sending anonymous questions using Shy Raccon

1. Send a private message to the Shy Raccoon account that includes the full username of the person you want the question to be forwarded to
2. That's it!

# Safety features

-  ccoon is opt-in based: you need to follow the bot to start receiving anonymous messages
- If you receive an abusive or hateful question, simply answer the bot a message that contain the word "report" (this is configurable). A human will take over to ensure this person can't reach you again, as well as reporting them if necessary.

# Hosting your own Shy Raccoon

## Create a Mastodon account for the bot

Chose any instance you'd like, but ensure they are okay to host this kind of bot.

## Create a Mastodon App

With the following scopes :

- read
- write:statuses
- write:bookmarks (to bookmark reported statuses)
- push

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