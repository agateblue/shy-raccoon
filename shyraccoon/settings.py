import os
import logging

ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
SERVER_URL = os.environ["SERVER_URL"]  # no final slash
STREAMING_URL = os.environ.get("STREAMING_URL", "/api/v1/streaming")
DRY_RUN = (os.environ.get("DRY_RUN") or None) is not None

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO").upper())

# Copy / wording
MENTION_PLACEHOLDER = os.environ.get("MENTION_PLACEHOLDER", "?")
EXAMPLE_USERNAME = os.environ.get("EXAMPLE_USERNAME", "user@mastodon.test")
EXAMPLE_MESSAGE = os.environ.get(
    "EXAMPLE_MESSAGE",
    """@{bot_account} this is a question for ?{recipient}:

How old are you?""",
)
FOLLOW_MESSAGE = os.environ.get(
    "FOLLOW_MESSAGE",
    """Welcome to Shy Raccoon!

Now that you follow me, I can forward you anonymous questions and messages. Whenever someone writes me a direct message like the one below, you will be notified. 

---
"""
    + EXAMPLE_MESSAGE
    + """
---

Give it a try yourself if you want to see how it works!

If you want to stop receiving anonymous messages, unfollow this account. Check out my bio/pinned posts for more info.
""",
)
FORWARD_MESSAGE = os.environ.get(
    "FORWARD_MESSAGE",
    """{message}

---

If you want to report it, contact UnePorte@eldritch.cafe with a screenshot of the conversation.

If you don't want to receive anonymous message in the future, please unfollow this account.
""",
)
DEFAULT_CONTENT_WARNING = os.environ.get(
    "DEFAULT_CONTENT_WARNING", "You received a Shy Raccoon message"
)
FORWARD_INSTRUCTIONS_MESSAGE = os.environ.get(
    "FORWARD_INSTRUCTIONS_MESSAGE",
    """To send an anonymous message to someone, please use the following format:

---
"""
    + EXAMPLE_MESSAGE
    + """
---

The important parts are:

1. The question mark at the beginning of the recipient username (instead of an @)
2. A line break before your question
""",
)

ERROR_INVALID_ACCOUNT = os.environ.get(
    "ERROR_INVALID_ACCOUNT",
    "The account '{account}' does not exist. " + FORWARD_INSTRUCTIONS_MESSAGE,
)
ERROR_INVALID_MESSAGE = os.environ.get(
    "ERROR_INVALID_MESSAGE",
    """Your message is invalid. """ + FORWARD_INSTRUCTIONS_MESSAGE,
)
SUCCESS_FORWARD_MESSAGE = os.environ.get(
    "SUCCESS_FORWARD_MESSAGE",
    "Received! I will forward your message to '{0}' immediatly if they enabled Shy Raccoon.",
)
