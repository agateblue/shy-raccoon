import pytest
from shyraccoon import main, settings

import requests_mock


@pytest.mark.parametrize(
    "payload, expected",
    [
        # not a DM
        ({"visibility": "public"}, main.SKIP),
        # A DM but shy raccount isn't mentionned
        ({"visibility": "direct", "mentions": [{"id": "nope"}]}, main.SKIP),
        # A DM with too much mentions
        (
            {
                "visibility": "direct",
                "mentions": [
                    {"id": "110108208783335072"},
                    {"id": "another"},
                ],
            },
            main.SKIP,
        ),
        # The bot should never answer itself
        (
            {
                "visibility": "direct",
                "account": {
                    "id": "110108208783335072",
                },
                "mentions": [
                    {"id": "110108208783335072"},
                ],
            },
            main.SKIP,
        ),
        # A DM mentioning shy raccoon, but no other account
        (
            {
                "visibility": "direct",
                "content": "Question pour quelqu'un",
                "mentions": [{"id": "110108208783335072"}],
            },
            {"action": "skip", "message": settings.ERROR_INVALID_ACCOUNT.format("")},
        ),
        # A DM mentioning shy raccoon, but the other
        # account isn't following shy raccoon
        (
            {
                "visibility": "direct",
                "content": "Question pour ?not_following:",
                "mentions": [{"id": "110108208783335072"}],
            },
            {
                "action": "skip",
                "message": settings.SUCCESS_FORWARD_MESSAGE.format("not_following"),
            },
        ),
        # A DM with two mentions, including shy raccoon and a followed account
        # so we move forward
        (
            {
                "visibility": "direct",
                "content": "for ?following : \nSome content\n",
                "spoiler_text": "A content warning",
                "mentions": [{"id": "110108208783335072"}],
            },
            {
                "action": "forward",
                "content": "Some content",
                "spoiler_text": f"{settings.DEFAULT_CONTENT_WARNING} | A content warning",
            },
        ),
    ],
)
def test_handle_message(payload, expected, requests_mock):
    bot_data = {
        "id": "110108208783335072",
        "username": "ShyRaccoon",
        "acct": "ShyRaccoon",
    }
    requests_mock.get(
        f"{settings.SERVER_URL}/api/v1/accounts/relationships?id[]=not_following",
        json={"followed_by": False},
    )
    requests_mock.get(
        f"{settings.SERVER_URL}/api/v1/accounts/relationships?id[]=following",
        json={"followed_by": True},
    )
    requests_mock.get(
        f"{settings.SERVER_URL}/api/v1/accounts/lookup?acct=not_following",
        json={"id": "not_following"},
    )
    requests_mock.get(
        f"{settings.SERVER_URL}/api/v1/accounts/lookup?acct=following",
        json={"id": "following"},
    )

    assert (
        main.handle_message(
            payload,
            bot_data=bot_data,
            server_url=settings.SERVER_URL,
            access_token=settings.ACCESS_TOKEN,
        )
        == expected
    )


@pytest.mark.parametrize(
    "content,expected",
    [
        ("question for ?toto\n\n", None),
        ("question for ?toto\n\ncoucou  ", "coucou"),
        ("question for ?toto\nbonjour\ncoucou  ", "bonjour\ncoucou"),
        ("for ?toto : \nSome content\n", "Some content"),
    ],
)
def test_prepare_for_forward(content, expected):
    assert main.prepare_for_forward(content, "?toto") == expected
