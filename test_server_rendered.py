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
