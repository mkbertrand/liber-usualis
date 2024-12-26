# Copyright 2024 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import pytest
from datetime import date, timedelta
import random
import warnings
import copy

import breviarium
import prioritizer
import datamanage

root = 'breviarium-1888'
implicationtable = datamanage.load_data(f'data/{root}/tag-implications.json')

def flattensetlist(sets):
    ret = set()
    for i in sets:
        ret |= i
    return ret

@pytest.mark.parametrize('dateoffset', random.sample(range(0,365), k=365))
def test_breaks(dateoffset: int) -> None:
    day = date(2000, 1, 1) + timedelta(days=dateoffset)
    warnings.filterwarnings('ignore')
    for hour in ['matutinum', 'laudes', 'prima', 'tertia', 'sexta', 'nona', 'vesperae', 'completorium']:
        tags = copy.deepcopy(prioritizer.getvespers(day) if hour == 'vesperae' or hour == 'completorium' else prioritizer.getdiurnal(day))
        for i in tags:
            for j in implicationtable:
                if j['tags'].issubset(i):
                    i |= j['implies']
        pile = datamanage.getbreviariumfiles(root, breviarium.defaultpile | flattensetlist(tags) | set(hour.split('+')))
        tags = [frozenset(i) for i in tags]
        primary = list(filter(lambda i: 'primarium' in i, tags))[0]
        tags.remove(primary)
        breviarium.process(root, {hour, 'hora'}, primary | {hour}, tags, pile)
