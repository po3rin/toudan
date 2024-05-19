import feedparser
import pandera.polars as pa
import polars as pl
from pandera.typing.polars import LazyFrame


COMPASS_RSS = "https://connpass.com/explore/ja.atom"


class EventSchema(pa.DataFrameModel):
    title: str
    link: str
    summary: str
    published: str
    recommend: bool


class KeywordSchema(pa.DataFrameModel):
    key: str


@pa.check_types
def get_event() -> LazyFrame[EventSchema]:
    """
    Get event information from the RSS feed of connpass.
    """
    feed = feedparser.parse(COMPASS_RSS)
    events = (
        {
            "title": event["title"],
            "link": event["link"],
            "summary": event["summary"],
            "published": event["published"],
            "recommend": False,
        }
        for event in feed["entries"]
    )
    return pl.LazyFrame(events)


@pa.check_types
def load_keywords() -> LazyFrame[KeywordSchema]:
    """
    Load keywords from the CSV file.
    """
    return pl.scan_csv("keywords.csv")


def main() -> None:
    events_lf = get_event().collect()
    keywords_lf = load_keywords().collect()

    print(events_lf)
    print(keywords_lf)


if __name__ == "__main__":
    main()
