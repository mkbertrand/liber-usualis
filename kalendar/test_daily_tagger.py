# Copyright 2024 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import pytest
from datetime import date, timedelta

from kalendar.daily_tagger import get_vespers
from kalendar.datamanage import get_bookshelf

year = 2001
bookshelf = get_bookshelf('breviarium-1888')

@pytest.mark.parametrize('day', [date(year, 1, 1) + timedelta(days=i) for i in range(365)])
def test_singleprimary(day: date) -> None:
	result = get_vespers(bookshelf, day)
	assert len(list(filter(lambda a: 'primarium' in a, result))) == 1
	assert all([len(i & {'primarium', 'commemoratio', 'omissum', 'psalmi'}) < 2 for i in result])
