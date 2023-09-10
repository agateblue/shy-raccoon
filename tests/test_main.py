import pytest
from shyraccoon import main, settings

import requests_mock

bot_data = {
    "id": "110108208783335072",
    "username": "ShyRaccoon",
    "acct": "ShyRaccoon",
}


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
                    {"id": bot_data["id"]},
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
                    "id": bot_data["id"],
                },
                "mentions": [
                    {"id": bot_data["id"]},
                ],
            },
            main.SKIP,
        ),
        # A DM mentioning shy raccoon, but no other account
        (
            {
                "id": "postid",
                "visibility": "direct",
                "content": "Question pour quelqu'un",
                "account": {"id": "someone"},
                "mentions": [{"id": bot_data["id"]}],
            },
            {
                "action": "reply",
                "in_reply_to_id": "postid",
                "recipient": {"id": "someone"},
                "message": settings.ERROR_INVALID_ACCOUNT.format(
                    account="",
                    bot_account="ShyRaccoon",
                    recipient=settings.EXAMPLE_USERNAME,
                ),
            },
        ),
        # A DM mentioning shy raccoon, but the other
        # account isn't following shy raccoon
        (
            {
                "id": "postid",
                "visibility": "direct",
                "account": {"id": "someone", "acct": "someone"},
                "content": "Question pour ?not_following:",
                "mentions": [{"id": bot_data["id"]}],
            },
            {
                "action": "reply",
                "in_reply_to_id": "postid",
                "recipient": {"id": "someone", "acct": "someone"},
                "message": settings.SUCCESS_FORWARD_MESSAGE.format("not_following"),
            },
        ),
        # A DM with two mentions, including shy raccoon and a followed account
        # so we move forward
        (
            {
                "id": "postid",
                "visibility": "direct",
                "account": {"id": "someone", "acct": "someone"},
                "content": """<p><span class="h-card"><a href="https://server/@ShyRaccoon" class="u-url mention" rel="nofollow noopener noreferrer" target="_blank">@<span>ShyRaccoon</span></a></span> this is a question for ?following:</p><p>How old are you?</p>""",
                "spoiler_text": "A content warning",
                "mentions": [{"id": bot_data["id"]}],
            },
            {
                "action": "forward",
                "sender": {"id": "someone", "acct": "someone"},
                "recipient": {"id": "following", "acct": "following"},
                "message": "How old are you?",
                "in_reply_to_id": "postid",
                "spoiler_text": f"{settings.DEFAULT_CONTENT_WARNING} | A content warning",
            },
        ),
        # A report message, but no reply_to_id
        # so we skip
        (
            {
                "id": "postid",
                "visibility": "direct",
                "account": {"id": "someone"},
                "content": """noop""",
                "tags": [{"name": "report", "url": "https://server.test/tags/report"}],
                "mentions": [{"id": bot_data["id"]}],
            },
            {
                "action": "skip",
            },
        ),
        # A report message, but the message author isn't the bot
        # so we skip
        (
            {
                "id": "postid",
                "visibility": "direct",
                "account": {"id": "someone"},
                "in_reply_to_id": "somerandompost",
                "content": """noop""",
                "tags": [{"name": "report", "url": "https://server.test/tags/report"}],
                "mentions": [{"id": bot_data["id"]}],
            },
            {
                "action": "skip",
            },
        ),
        # A report message, with proper reported id (from the bot)
        (
            {
                "id": "postid",
                "visibility": "direct",
                "account": {"id": "someone"},
                "in_reply_to_id": "someshyraccoonpost",
                "content": """noop""",
                "tags": [{"name": "report", "url": "https://server.test/tags/report"}],
                "mentions": [{"id": bot_data["id"]}],
            },
            {
                "action": "report",
                "anonymous_sender": {"id": "not_following"},
                "sender": {"id": "someone"},
                "report": {
                    "id": "postid",
                    "visibility": "direct",
                    "account": {"id": "someone"},
                    "in_reply_to_id": "someshyraccoonpost",
                    "content": """noop""",
                    "tags": [
                        {"name": "report", "url": "https://server.test/tags/report"}
                    ],
                    "mentions": [{"id": bot_data["id"]}],
                },
                "reported_message": {
                    "id": "someshyraccoonpost",
                    "in_reply_to_account_id": "not_following",
                    "account": {"id": bot_data["id"]},
                },
            },
        ),
    ],
)
def test_handle_message(payload, expected, requests_mock):
    requests_mock.get(
        f"{settings.SERVER_URL}/api/v1/statuses/someshyraccoonpost",
        json={
            "id": "someshyraccoonpost",
            "account": {"id": bot_data["id"]},
            "in_reply_to_account_id": "not_following",
        },
    )
    requests_mock.get(
        f"{settings.SERVER_URL}/api/v1/statuses/somerandompost",
        json={"account": {"id": "randomuser"}},
    )
    requests_mock.get(
        f"{settings.SERVER_URL}/api/v1/accounts/relationships?id[]=not_following",
        json=[{"followed_by": False}],
    )
    requests_mock.get(
        f"{settings.SERVER_URL}/api/v1/accounts/relationships?id[]=following",
        json=[{"followed_by": True}],
    )
    requests_mock.get(
        f"{settings.SERVER_URL}/api/v1/accounts/lookup?acct=not_following",
        json={"id": "not_following", "acct": "not_following"},
    )
    requests_mock.get(
        f"{settings.SERVER_URL}/api/v1/accounts/lookup?acct=following",
        json={"id": "following", "acct": "following"},
    )
    requests_mock.get(
        f"{settings.SERVER_URL}/api/v1/accounts/not_following",
        json={"id": "not_following"},
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
        ("question for ?toto:\n\nbonjour\n\ncoucou  ", "bonjour\n\ncoucou"),
        ("for ?toto : \nSome content\n", "Some content"),
    ],
)
def test_prepare_for_forward(content, expected):
    assert main.prepare_for_forward(content) == expected


def test_handle_skip():
    main.handle_skip({"action": "skip"})


def test_handle_notification_follow(requests_mock):
    requests_mock.post(f"{settings.SERVER_URL}/api/v1/statuses", json={})
    main.handle_follow(
        {
            "action": "follow",
            "sender": {"acct": "hello@world"},
            "bot_data": {"acct": "shyraccoon"},
        }
    )

    request = requests_mock.request_history[0]

    message = settings.FOLLOW_MESSAGE.format(
        bot_account="shyraccoon",
        recipient="hello@world",
    )
    assert request.json() == {
        "status": f"@hello@world {message}",
        "visibility": "direct",
    }


def test_handle_reply(requests_mock):
    requests_mock.post(f"{settings.SERVER_URL}/api/v1/statuses", json={})

    main.handle_reply(
        {
            "action": "reply",
            "message": "hello",
            "recipient": {"acct": "hello@world"},
            "in_reply_to_id": "previous",
        }
    )

    request = requests_mock.request_history[0]

    assert request.json() == {
        "status": f"@hello@world hello",
        "visibility": "direct",
        "in_reply_to_id": "previous",
    }


def test_handle_forward(requests_mock):
    requests_mock.post(f"{settings.SERVER_URL}/api/v1/statuses", json={})

    main.handle_forward(
        {
            "action": "forward",
            "spoiler_text": "cw",
            "message": "hello",
            "sender": {"acct": "sender@world"},
            "recipient": {"acct": "recipient@world"},
            "in_reply_to_id": "previous",
        }
    )

    forward = requests_mock.request_history[0]
    confirmation = requests_mock.request_history[1]

    forward_message = settings.FORWARD_MESSAGE.format(
        message="hello",
        report_hashtags=", ".join(f"#\\{t}" for t in settings.REPORT_HASHTAGS),
    )
    assert forward.json() == {
        "status": f"@recipient@world {forward_message}",
        "visibility": "direct",
        "spoiler_text": "cw",
        "in_reply_to_id": "previous",
    }
    assert confirmation.json() == {
        "status": f"@sender@world {settings.SUCCESS_FORWARD_MESSAGE.format('recipient@world')}",
        "visibility": "direct",
        "in_reply_to_id": "previous",
    }


def test_handle_report(requests_mock):
    payload = {
        "action": "report",
        "anonymous_sender": {
            "acct": "anonymous_sender",
            "url": "https://anonymous.test",
        },
        "sender": {"acct": "sender"},
        "report": {"id": "reportid"},
        "reported_message": {
            "id": "reportedpost",
            "url": "http://url.test/reported",
        },
    }
    requests_mock.post(
        f"{settings.SERVER_URL}/api/v1/statuses/reportedpost/bookmark", json={}
    )
    requests_mock.post(
        f"{settings.SERVER_URL}/api/v1/statuses/resultid/bookmark", json={}
    )
    requests_mock.post(
        f"{settings.SERVER_URL}/api/v1/statuses", json={"id": "resultid"}
    )
    main.handle_report(payload)

    reported_bookmark = requests_mock.request_history[0]
    mod_notification = requests_mock.request_history[1]
    mod_notification_bookmark = requests_mock.request_history[2]
    sender_reply = requests_mock.request_history[3]
    sender_reply_bookmark = requests_mock.request_history[4]

    # all posts related to moderation/reports should be bookmarked
    # to avoid deletion
    assert reported_bookmark.path == "/api/v1/statuses/reportedpost/bookmark"
    assert mod_notification_bookmark.path == "/api/v1/statuses/resultid/bookmark"
    assert sender_reply_bookmark.path == "/api/v1/statuses/resultid/bookmark"

    mod_message = settings.REPORT_MOD_MESSAGE.format(
        sender="sender",
        reported_message_url="http://url.test/reported",
        anonymous_sender="anonymous_sender",
        anonymous_sender_url="https://anonymous.test",
    )
    mods = [f"@{m}" for m in settings.MODERATORS_USERNAMES]
    assert mod_notification.json() == {
        "status": f"{' '.join(mods)} {mod_message}",
        "visibility": "direct",
        "in_reply_to_id": "reportid",
    }
    assert sender_reply.json() == {
        "status": f"@sender {settings.REPORT_CONFIRMATION_MESSAGE.format(mods=', '.join(settings.MODERATORS_USERNAMES))}",
        "visibility": "direct",
        "in_reply_to_id": "reportid",
    }
