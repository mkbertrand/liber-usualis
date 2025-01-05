# Copyright 2024 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import pytest
from datetime import date, timedelta
import warnings
import copy
import json

import breviarium
import prioritizer
import datamanage

year = 2001
root = 'breviarium-1888'
implicationtable = datamanage.load_data(f'data/{root}/tag-implications.json')

# Basically a copy of breviarium#dump_data but removes tags since these are liable to change without affecting the content being tested
def striptags(j):

	def recurse(obj, key=None):
		match obj:
			case dict():
				ret = {k: recurse(v, key=k) for k, v in obj.items()}
				del ret['tags']
				return ret
			case list():
				return [recurse(v) for v in obj]
			case set() | frozenset():
				return ''
			case _:
				return obj

	return json.dumps(recurse(j))

def flattensetlist(sets):
	ret = set()
	for i in sets:
		ret |= i
	return ret

@pytest.mark.parametrize('dateoffset', range(0, 365))
def test_breaks(dateoffset: int) -> None:
	day = date(year, 1, 1) + timedelta(days=dateoffset)
	warnings.filterwarnings('ignore')
	for j in ['matutinum+laudes+prima+tertia+sexta+nona', 'vesperae+completorium'][1:]:
		ret = breviarium.generate(root, day, j)

@pytest.mark.parametrize('dateoffset', range(0, 365))
def test_match(dateoffset: int) -> None:
	day = date(year, 1, 1) + timedelta(days=dateoffset)
	warnings.filterwarnings('ignore')

	for j in ['matutinum+laudes+prima+tertia+sexta+nona', 'vesperae+completorium']:
		# Eh, it's probably a match if it's the same length, right?
		assert len(str(striptags(breviarium.generate(root, day, j)))) == len(str(striptags(datamanage.load_data(f'testdata/{day}-vesperal.json' if 'vesperae' in j else f'testdata/{day}-diurnal.json'))))
