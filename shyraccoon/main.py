import json
import logging

import requests

from . import settings


def get_data(server_url, path, access_token):
    headers = {
        "authorization": f"Bearer {access_token}",
    }
    url = f"{server_url}{path}"
    logging.info("Requesting %s…", url)
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    logging.debug("Received %s", data)
    return data


def start_stream(server_url, streaming_url, access_token):
    s = requests.Session()
    url = f"{server_url}{streaming_url}"

    headers = {
        "connection": "keep-alive",
        "content-type": "application/json",
        "transfer-encoding": "chunked",
        "authorization": f"Bearer {access_token}",
    }

    req = requests.Request("GET", url, headers=headers).prepare()

    logging.info("Starting stream on %s%s", server_url, streaming_url)
    resp = s.send(req, stream=True)
    resp.raise_for_status()
    event_type = None

    for line in resp.iter_lines():
        logging.debug("Received line: %s", line)
        line = line.decode("UTF-8")

        key = "event: "
        if key in line:
            line = line.replace(key, "")
            event_type = line

        key = "data: "
        if key in line:
            line = line.replace(key, "")
            data = dict()
            data["event"] = event_type
            data["data"] = json.loads(line)
            yield data


SKIP = {"action": "skip"}


def skip(message=None):
    data = {"action": "skip"}
    if message:
        data["message"] = message

    return data


def handle_message(
    payload,
    bot_data,
    server_url,
    access_token,
):
    if payload["visibility"] != "direct":
        return skip()

    mentions = payload.get("mentions", []) or []
    mentioned = False
    account_data = payload.get("account", {})
    if account_data.get("id") == bot_data["id"]:
        return skip()

    if len(mentions) != 1:
        return skip()

    for mention in mentions:
        if mention["id"] == bot_data["id"]:
            mentioned = True

    if not mentioned:
        return skip()

    content = payload["content"]
    words = content.split(" ")
    mentioned_username = None
    raw_username = None
    for word in words:
        if is_username(word):
            raw_username = word
            mentioned_username = clean_username(word)
    if not mentioned_username:
        return skip(settings.ERROR_INVALID_ACCOUNT.format(""))
    try:
        recipient = get_data(
            server_url,
            f"/api/v1/accounts/lookup?acct={mentioned_username}",
            access_token=access_token,
        )
    except requests.RequestException:
        return skip(settings.ERROR_INVALID_ACCOUNT.format(mentioned_username))

    # check if the other mentioned account is following shy raccoon
    relationship = get_data(
        server_url,
        f'/api/v1/accounts/relationships?id[]={recipient["id"]}',
        access_token=access_token,
    )

    if not relationship["followed_by"]:
        return skip(settings.SUCCESS_FORWARD_MESSAGE.format(mentioned_username))

    spoiler_text = [settings.DEFAULT_CONTENT_WARNING]

    if payload.get("spoiler_text"):
        spoiler_text.append(payload["spoiler_text"])

    forwarded_message = prepare_for_forward(payload["content"], raw_username)

    if not forwarded_message:
        return skip(settings.ERROR_INVALID_MESSAGE)

    return {
        "action": "forward",
        "content": forwarded_message,
        "spoiler_text": " | ".join(spoiler_text),
    }


def is_username(word):
    return word.startswith(settings.MENTION_PLACEHOLDER) and len(word) > 1


def clean_username(word):
    for char in [settings.MENTION_PLACEHOLDER, "?", ":", "!", ",", "(", ")"]:
        word = word.replace(char, "")
    return word


def prepare_for_forward(content, username):
    message = content.split(username, 1)
    if len(message) < 2:
        return

    if not message[1].strip():
        return
    message = message[1].split("\n", 1)
    if len(message) < 2:
        return
    return message[1].strip()
