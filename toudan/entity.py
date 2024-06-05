from typing import TypedDict

import pandera.polars as pa


class Events(TypedDict):
    """
    Event information.
    """

    title: str
    link: str
    summary: str
    published: str
    participants: dict[str, dict[str, int]]


class EventSchema(pa.DataFrameModel):
    """
    Event schema.
    """

    title: str
    link: str
    summary: str
    published: str


class KeywordSchema(pa.DataFrameModel):
    """
    Keyword schema.
    """

    key: str

