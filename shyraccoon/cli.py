import logging

import click

from . import main
from . import settings


@click.group()
def cli():
    pass


@cli.command
def stream():
    click.echo("Getting user info…")
    user_data = main.get_data(
        server_url=settings.SERVER_URL,
        access_token=settings.ACCESS_TOKEN,
        path="/api/v1/accounts/verify_credentials",
    )
    click.echo(f"Logged in as {user_data['url']}")
    click.echo("Starting stream…")
    s = main.start_stream(
        server_url=settings.SERVER_URL,
        streaming_url=settings.STREAMING_URL,
        access_token=settings.ACCESS_TOKEN,
    )
    for event in s:
        logging.info("Received event: %s", event)
        action = None
        if event["event"] == "notification" and event["data"]["type"] == "follow":
            action = {
                "type": "follow",
                "sender": event["data"]["account"],
                "bot_data": user_data,
            }
            main.handle_follow(action)
        if event["event"] == "notification" and event["data"]["type"] == "mention":
            action = main.handle_message(
                event["data"]["status"],
                bot_data=user_data,
                server_url=settings.SERVER_URL,
                access_token=settings.ACCESS_TOKEN,
            )
        if action:
            logging.info("Handling action %s", action)
            handler = getattr(main, f'handle_{action["action"]}')
            handler(action)


if __name__ == "__main__":
    cli()
