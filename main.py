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


@pa.check_types
def extract_events_include_keywords(events_lf: LazyFrame[EventSchema], keywords_lf: LazyFrame[KeywordSchema]) -> LazyFrame[EventSchema]:
    keywords_list = keywords_lf.to_pandas()["key"].tolist()
    events_lf["recommend"] = events_lf["summary"].str.contains("|".join(keywords_list))
    return events_lf


def main() -> None:
    events_lf = get_event().collect()
    keywords_lf = load_keywords().collect()
    events_lf = extract_events_include_keywords(events_lf, keywords_lf)

    print(events_lf)
    print(keywords_lf)


if __name__ == "__main__":
    main()
