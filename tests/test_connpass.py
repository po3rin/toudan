import unittest

import polars as pl

from toudan.connpass import extract_events_include_keywords, is_events_has_presentation
from polars.testing import assert_frame_equal


class TestExtractEventsIncludeKeywords(unittest.TestCase):
    def test_run(self):
        events = {
            "title": ["機械学習LT会", "フロントエンドカンファレンス"],
            "link": ["https://example.com/1", "https://example.com/2"],
            "summary": ["機械学習についてのLT会です", "フロントエンドについてのカンファレンスです"],
            "published": ["2021-01-01T00:00:00+09:00", "2021-01-02T00:00:00+09:00"],
        }
        events_lf = pl.LazyFrame(events).collect()

        keywords_data = {"key": ["機械学習", "データ分析"]}
        keywords_lf = pl.LazyFrame(keywords_data).collect()

        want = {
            "title": ["機械学習LT会"],
            "link": ["https://example.com/1"],
            "summary": ["機械学習についてのLT会です"],
            "published": ["2021-01-01T00:00:00+09:00"],
        }
        want_lf = pl.LazyFrame(want).collect()

        result = extract_events_include_keywords(events_lf, keywords_lf)
        assert_frame_equal(result, want_lf)


class TestIsEventsHasPresentation(unittest.TestCase):
    def test_run(self):
        participants_info = {
                "参加枠": {"numerator": 100, "denominator": 200},
                "発表枠": {"numerator": 5, "denominator": 10},
        }

        self.assertTrue(is_events_has_presentation(participants_info))

        participants_info = {
                "現地参加枠": {"numerator": 100, "denominator": 200},
                "リモート枠": {"numerator": 5, "denominator": 10},
        }

        self.assertFalse(is_events_has_presentation(participants_info))
