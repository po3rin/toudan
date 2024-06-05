from slack_sdk.webhook import WebhookClient

from toudan.entity import Events


def post_slack_message(slack_webhook_url: str, txt: str) -> None:
    """
    Post a message to Slack.
    """
    webhook = WebhookClient(slack_webhook_url)
    response = webhook.send(text=txt)
    print(f"status: {response.status_code} body: {response.body}")


def events_to_message(result: list[Events]) -> str:
    """
    Convert events to a message.
    """
    events_txt = ""
    for event in result:
        events_txt += f"""
        --------------------------------
        # title: {event["title"]}
        # link: {event["link"]}
        # participants: {event["participants"]}
        """

    msg = f"""
    皆さんが興味を持ちそうな発表枠があるイベントを見つけました！
    {events_txt}
    """
    return msg

