# Copyright 2024 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import pytest
from datetime import date, timedelta

import prioritizer
import kalendar.datamanage

import pathlib

year = 2001
book = pathlib.Path(__file__).parent.joinpath('data/breviarium-1888')

@pytest.mark.parametrize('day', [date(year, 1, 1) + timedelta(days=i) for i in range(365)])
def test_singleprimary(day):
	result = prioritizer.get_vespers(book, day)
	assert len(list(filter(lambda a: 'primarium' in a, result))) == 1
	assert all([len(i & {'primarium', 'commemoratio', 'omissum', 'psalmi'}) < 2 for i in result])
