# Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

from datetime import date

import datamanage

TODAY = date(2026, 10, 9)

def test_dates_within_a_year_are_server_rendered() -> None:
    assert datamanage.is_server_rendered(TODAY, TODAY)
    assert datamanage.is_server_rendered(date(2027, 10, 9), TODAY)
    assert datamanage.is_server_rendered(date(2025, 10, 9), TODAY)

def test_dates_beyond_the_range_are_left_to_the_client() -> None:
    assert not datamanage.is_server_rendered(date(2027, 10, 11), TODAY)
    assert not datamanage.is_server_rendered(date(2025, 10, 7), TODAY)
    assert not datamanage.is_server_rendered(date(9999, 12, 31), TODAY)

def test_server_rendered_dates_span_exactly_the_range() -> None:
    dates = datamanage.server_rendered_dates(TODAY)
    assert dates[0] == date(2025, 10, 8)
    assert dates[-1] == date(2027, 10, 10)
    assert all(datamanage.is_server_rendered(day, TODAY) for day in dates)
    assert not datamanage.is_server_rendered(dates[0] - (dates[1] - dates[0]), TODAY)
    assert not datamanage.is_server_rendered(dates[-1] + (dates[1] - dates[0]), TODAY)
