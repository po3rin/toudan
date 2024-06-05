import os


from toudan.connpass import connpass_events
from toudan.slack import events_to_message, post_slack_message

CONNPASS_RSS = "https://connpass.com/explore/ja.atom"


def main() -> None:
    """
    Main function.
    """
    slack_webhook_url = os.environ["SLACK_WEBHOOK_URL"]
    result = connpass_events("keywords.csv")
    if len(result) == 0:
        print("No events found.")
        return
    message = events_to_message(result)
    post_slack_message(slack_webhook_url, message)


if __name__ == "__main__":
    main()
