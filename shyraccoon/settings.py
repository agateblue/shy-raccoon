import os
import logging

ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
SERVER_URL = os.environ["SERVER_URL"]  # no final slash
STREAMING_URL = os.environ.get("STREAMING_URL", "/api/v1/streaming/direct")

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO").upper())

# Copy / wording
MENTION_PLACEHOLDER = os.environ.get("MENTION_PLACEHOLDER", "?")
DEFAULT_CONTENT_WARNING = os.environ.get(
    "DEFAULT_CONTENT_WARNING", "You received a Shy Raccoon question"
)
ERROR_INVALID_ACCOUNT = os.environ.get(
    "ERROR_INVALID_ACCOUNT", "The account '{0}' does not exist."
)
SUCCESS_FORWARD_MESSAGE = os.environ.get(
    "SUCCESS_FORWARD_MESSAGE",
    "Received! I will forward your message to '{0}' immediatly if they enabled Shy Raccoon.",
)
