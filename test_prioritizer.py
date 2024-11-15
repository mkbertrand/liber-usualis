# Copyright 2024 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import pytest
from datetime import date, timedelta

import prioritizer
import datamanage

@pytest.mark.parametrize('dateoffset',range(0, 365))
def test_singleprimary(dateoffset):
    day = date(2000, 1, 1) + timedelta(days=dateoffset)
    print(datamanage.getdate(day))
    print(datamanage.getdate(day + timedelta(days = 1)))
    result = prioritizer.getvespers(day)
    print(result)
    assert len(list(filter(lambda a: 'primarium' in a, result))) == 1
