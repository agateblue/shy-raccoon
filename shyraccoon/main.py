import json
import logging

import requests
import websockets
from . import settings


def get_data(server_url, path, access_token):
    headers = {
        "authorization": f"Bearer {access_token}",
    }
    url = f"{server_url}{path}"
    logging.debug("GET Requesting %s…", url)
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    logging.debug("Received %s", data)
    return data


def post_data(server_url, path, access_token, data):
    headers = {
        "authorization": f"Bearer {access_token}",
    }
    url = f"{server_url}{path}"
    logging.debug("POST Requesting %s with data %s…", url, data)
    if settings.DRY_RUN:
        logging.info("DRY_RUN is on, not posting anything")
        return {}
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    data = response.json()
    logging.debug("Received %s", data)
    return data


async def start_stream(server_url, streaming_url, access_token, callback):
    s = requests.Session()
    url = f"{server_url}{streaming_url}"
    url = url.replace("http://", "ws://")
    url = url.replace("https://", "wss://")
    url += "?stream=user"
    headers = {"authorization": f"Bearer {access_token}"}
    logging.info("[WS] Connecting on %s…", url)
    async for websocket in websockets.connect(url, extra_headers=headers):
        logging.info("[WS] Connected!")
        while True:
            try:
                message = await websocket.recv()
            except websockets.ConnectionClosed:
                logging.info("[WS] Connection closed")
                break
            message = json.loads(message)
            logging.debug(f"[WS] Received: %s", message)
            callback(
                {"event": message["event"], "data": json.loads(message["payload"])}
            )


SKIP = {"action": "skip"}


def reply(message, recipient, in_reply_to_id=None):
    return {
        "action": "reply",
        "message": message,
        "recipient": recipient,
        "in_reply_to_id": in_reply_to_id,
    }


def handle_message(
    payload,
    bot_data,
    server_url,
    access_token,
):
    account_data = payload.get("account", {})
    if account_data.get("id") == bot_data["id"]:
        return SKIP

    if payload["visibility"] != "direct":
        return SKIP

    mentions = payload.get("mentions", []) or []
    mentioned = False

    if len(mentions) != 1:
        return SKIP

    for mention in mentions:
        if mention["id"] == bot_data["id"]:
            mentioned = True

    if not mentioned:
        return SKIP

    content = payload["content"]
    # ugly HTML cleanup
    if content.startswith("<p>"):
        content = content[3:]
    if content.endswith("</p>"):
        content = content[:-4]
    content = content.replace("</p><p>", "\n\n")
    # end of ugly HTML cleanup

    words = content.split(" ")
    mentioned_username = None
    raw_username = None
    for word in words:
        if is_username(word):
            raw_username = word
            mentioned_username = clean_username(word)
    if not mentioned_username:
        return reply(
            settings.ERROR_INVALID_ACCOUNT.format(
                account="",
                bot_account=bot_data["acct"],
                recipient=settings.EXAMPLE_USERNAME,
            ),
            recipient=payload["account"],
            in_reply_to_id=payload["id"],
        )
    try:
        recipient = get_data(
            server_url,
            f"/api/v1/accounts/lookup?acct={mentioned_username}",
            access_token=access_token,
        )
    except requests.RequestException:
        return reply(
            settings.ERROR_INVALID_ACCOUNT.format(
                account=mentioned_username,
                bot_account=bot_data["acct"],
                recipient=settings.EXAMPLE_USERNAME,
            ),
            recipient=payload["account"],
            in_reply_to_id=payload["id"],
        )

    # check if the other mentioned account is following shy raccoon
    relationship = get_data(
        server_url,
        f'/api/v1/accounts/relationships?id[]={recipient["id"]}',
        access_token=access_token,
    )[0]

    if not relationship["followed_by"]:
        return reply(
            settings.SUCCESS_FORWARD_MESSAGE.format(recipient["acct"]),
            recipient=payload["account"],
            in_reply_to_id=payload["id"],
        )

    spoiler_text = [settings.DEFAULT_CONTENT_WARNING]

    if payload.get("spoiler_text"):
        spoiler_text.append(payload["spoiler_text"])

    forwarded_message = prepare_for_forward(content)

    if not forwarded_message:
        return reply(
            settings.ERROR_INVALID_MESSAGE.format(
                bot_account=bot_data["acct"],
                recipient=settings.EXAMPLE_USERNAME,
            ),
            recipient=payload["account"],
            in_reply_to_id=payload["id"],
        )

    return {
        "action": "forward",
        "recipient": recipient,
        "sender": payload["account"],
        "message": forwarded_message,
        "spoiler_text": " | ".join(spoiler_text),
        "in_reply_to_id": payload["id"],
    }


def is_username(word):
    return word.startswith(settings.MENTION_PLACEHOLDER) and len(word) > 1


def clean_username(word):
    for char in [settings.MENTION_PLACEHOLDER, "?", ":", "!", ",", "(", ")"]:
        word = word.replace(char, "")
    return word.splitlines()[0]


def prepare_for_forward(content):
    lines = [l.strip() for l in content.splitlines() if l.strip()]
    if len(lines) < 2:
        return

    return "\n\n".join(lines[1:])


def handle_skip(action):
    return


def handle_reply(action):
    data = {
        "visibility": "direct",
        "status": f'@{action["recipient"]["acct"]} {action["message"]}',
        "in_reply_to_id": action.get("in_reply_to_id"),
    }

    return post_data(
        server_url=settings.SERVER_URL,
        path="/api/v1/statuses",
        access_token=settings.ACCESS_TOKEN,
        data=data,
    )


def handle_forward(action):
    # first, forward the message
    message = settings.FORWARD_MESSAGE.format(message=action["message"])
    data = {
        "visibility": "direct",
        "status": f'@{action["recipient"]["acct"]} {message}',
        "spoiler_text": action["spoiler_text"],
        "in_reply_to_id": action.get("in_reply_to_id"),
    }

    post_data(
        server_url=settings.SERVER_URL,
        path="/api/v1/statuses",
        access_token=settings.ACCESS_TOKEN,
        data=data,
    )

    # then, send a confirmation
    message = settings.SUCCESS_FORWARD_MESSAGE.format(action["recipient"]["acct"])
    data = {
        "visibility": "direct",
        "status": f'@{action["sender"]["acct"]} {message}',
        "in_reply_to_id": action.get("in_reply_to_id"),
    }

    return post_data(
        server_url=settings.SERVER_URL,
        path="/api/v1/statuses",
        access_token=settings.ACCESS_TOKEN,
        data=data,
    )


def handle_follow(action):
    message = settings.FOLLOW_MESSAGE.format(
        bot_account=action["bot_data"]["acct"],
        recipient=action["sender"]["acct"],
    )
    data = {
        "visibility": "direct",
        "status": f'@{action["sender"]["acct"]} {message}',
    }

    return post_data(
        server_url=settings.SERVER_URL,
        path="/api/v1/statuses",
        access_token=settings.ACCESS_TOKEN,
        data=data,
    )
