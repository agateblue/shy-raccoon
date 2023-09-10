import os
import logging

ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
SERVER_URL = os.environ["SERVER_URL"]  # no final slash
STREAMING_URL = os.environ.get("STREAMING_URL", "/api/v1/streaming")
DRY_RUN = os.environ.get("DRY_RUN") and os.environ.get("DRY_RUN") != "0"

RATE_LIMIT_USER_RATE = os.environ.get("RATE_LIMIT_USER", "50/day")
RATE_LIMIT_USER_COUPLE_RATE = os.environ.get("RATE_LIMIT_USER_COUPLE", "10/hour")
RATE_LIMIT_EXEMPTED_USERS = [
    user.strip().lower()
    for user in os.environ.get("RATE_LIMIT_EXEMPTED_USERS", "").split(",")
    if user.strip()
]

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO").upper())

MODERATORS_USERNAMES = [
    mod.strip() for mod in os.environ["MODERATORS_USERNAMES"].split(",") if mod.strip()
]

# Copy / wording
REPORT_HASHTAGS = [
    tag.lower().strip()
    for tag in os.environ.get("REPORT_HASHTAGS", "report").split(",")
    if tag.strip()
]

MENTION_PLACEHOLDER = os.environ.get("MENTION_PLACEHOLDER", "?")
EXAMPLE_USERNAME = os.environ.get("EXAMPLE_USERNAME", "user@mastodon.test")
EXAMPLE_MESSAGE = os.environ.get(
    "EXAMPLE_MESSAGE",
    """@{bot_account} for ?{recipient}:

How are you?""",
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

Give it a try yourself to see how it works!

To stop receiving anonymous messages, unfollow this account. Check out my bio/pinned posts for more info.
""",
)
FORWARD_MESSAGE = os.environ.get(
    "FORWARD_MESSAGE",
    """{message}

---

To report it, reply to this message, including any relevant information and one of the following hashtags: {report_hashtags}.

If you don't want to receive anonymous messages in the future, please unfollow this account.
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

1. The question mark at the beginning of the recipient username (instead of an @). THIS IS IMPORTANT TO AVOID you don't mention the person directly!
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

REPORT_MOD_MESSAGE = os.environ.get(
    "REPORT_MOD_MESSAGE",
    """User '{sender}' has reported a Shy Raccoon message.

Please check the reported message and conversation at {reported_message_url}.

The anonymous message was sent by '{anonymous_sender}' ({anonymous_sender_url}).

#ShyRaccoonReport""",
)
REPORT_CONFIRMATION_MESSAGE = os.environ.get(
    "REPORT_CONFIRMATION_MESSAGE",
    """We have received your report, we'll contact you to let you know the actions that have been taken.

If you need to contact a moderator directly, please reach out in private with {mods}""",
)
