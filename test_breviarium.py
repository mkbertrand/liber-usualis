import pytest
from datetime import date, timedelta
import random
import warnings

import breviarium

@pytest.mark.parametrize('dateoffset', random.sample(range(0,365), k=20))
def test_breaks(dateoffset: int) -> None:
    day = date(2000, 1, 1) + timedelta(days=dateoffset)
    warnings.filterwarnings('ignore')
    for hour in ['matutinum', 'laudes', 'prima', 'tertia', 'sexta', 'nona', 'vesperae', 'completorium']:
            breviarium.hour('breviarium-1888', hour, day)

