
import feedparser
import pandera.polars as pa
import polars as pl
import requests
from bs4 import BeautifulSoup
from pandera.typing.polars import LazyFrame

from toudan.entity import Events, EventSchema, KeywordSchema

CONNPASS_RSS = "https://connpass.com/explore/ja.atom"


@pa.check_types
def get_event() -> LazyFrame[EventSchema]:
    """
    Get event information from the RSS feed of connpass.
    """
    feed = feedparser.parse(CONNPASS_RSS)
    events = (
        {
            "title": event["title"],
            "link": event["link"],
            "summary": event["summary"],
            "published": event["published"],
        }
        for event in feed["entries"]
    )
    return pl.LazyFrame(events)


@pa.check_types
def load_keywords_from_csv(csv_path: str) -> LazyFrame[KeywordSchema]:
    """
    Load keywords from the CSV file.
    """
    return pl.scan_csv(csv_path)


@pa.check_types
def extract_events_include_keywords(
    events_lf: LazyFrame[EventSchema], keywords_lf: LazyFrame[KeywordSchema]
) -> LazyFrame[EventSchema]:
    """
    Extract events that include keywords.
    """
    keywords_list = keywords_lf.to_pandas()["key"].tolist()
    return events_lf.filter(pl.col("summary").str.contains("|".join(keywords_list)))


def extract_event_participants_info(link: str) -> dict[str, dict[str, int]]:
    """
    Check if the event has a presentation.
    """
    response = requests.get(link, timeout=10, headers={"User-Agent": ""})
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")
    results = {}
    paticipations = soup.select(".ptype")
    for paticipation in paticipations:
        name = paticipation.select(".ptype_name")[0].get_text()
        amount_txt = paticipation.select(".participants > .amount")[0].get_text()
        try:
            amout_txt = amount_txt.replace("人", "")
            if "/" not in amout_txt:
                amount_numerator = int(amout_txt)
                amount_denominator = 0
            else:
                amount_numerator = int(amout_txt.split("/")[0])
                amount_denominator = int(amout_txt.split("/")[1])
        except IndexError as index_error:
            print(
                f"Failed to parse amount: {amount_txt}, link: {link}, exception: {index_error}"
            )
            continue
        results[name] = {
            "numerator": amount_numerator,
            "denominator": amount_denominator,
        }
    return results


def is_events_has_presentation(participants_info: dict[str, dict[str, int]]) -> bool:
    """
    Check if the event has a presentation.
    """
    keys = participants_info.keys()
    for key in keys:
        if (
            "発表" in key
            or "プレゼン" in key
            or "LT" in key
            or "lightning talk" in key
            or "登壇" in key
        ):
            return True
    return False


def connpass_events(keywords_csv_path: str) -> list[Events]:
    """
    Main function to get connpass events.
    """
    events_lf = get_event().collect()
    print(events_lf)
    keywords_lf = load_keywords_from_csv(keywords_csv_path).collect()
    events_lf = extract_events_include_keywords(events_lf, keywords_lf)

    events_df = events_lf.to_pandas()
    result: list[Events] = []
    for _, row in events_df.iterrows():
        participants_info = extract_event_participants_info(row["link"])
        if is_events_has_presentation(participants_info):
            result.append(
                {
                    "title": row["title"],
                    "link": row["link"],
                    "summary": row["summary"],
                    "published": row["published"],
                    "participants": participants_info,
                }
            )
    return result

