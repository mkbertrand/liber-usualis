# Copyright 2024 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import pytest
from datetime import date, timedelta
import warnings
import copy
import re

import diff_match_patch

import breviarium
import prioritizer
import datamanage

year = 2001
root = 'breviarium-1888'
implicationtable = datamanage.load_data(f'data/{root}/tag-implications.json')

dmp = diff_match_patch.diff_match_patch()

# Basically a copy of datamanage#dump_data but removes tags since these are liable to change without affecting the content being tested
def striptags(j):

	def recurse(obj, key=None):
		match obj:
			case dict():
				return str({k: recurse(v, key=k) for k, v in obj.items()})
			case list():
				return ''.join([recurse(v) for v in obj])
			case set() | frozenset():
				return ''
			case _:
				return str(obj)

	return recurse(j)

def flattensetlist(sets):
	ret = set()
	for i in sets:
		ret |= i
	return ret

@pytest.mark.parametrize('day', [date(year, 1, 1) + timedelta(days=i) for i in range(365)])
def test_match(day) -> None:
	warnings.filterwarnings('ignore')

	for j in ['matutinum', 'laudes+prima+tertia+sexta+nona', 'vesperae+completorium']:
		old = str(striptags(datamanage.load_data(f'testdata/{day}-{j.replace("+", "-")}.json')))
		new = str(striptags(breviarium.generate(root, day, j)))

		diffs = dmp.diff_main(old, new)
		dmp.diff_cleanupSemantic(diffs)

		change = False
		changelog = ''
		for (op, item) in diffs:
			if op == dmp.DIFF_DELETE:
				print(f'- {item.replace('\\', '')}\n')
				changelog += f'- {item.replace('\\', '')}\n\n'
				change = True
			elif op == dmp.DIFF_INSERT:
				print(f'+ {item.replace('\\', '')}')
				changelog += f'+ {item.replace('\\', '')}\n'
				change = True
			# Don't print if there's an equal section since this is superfluous

		if change:
			with open(f'testresults/{day}-{j.replace("+", "-")}.json', 'w') as fileout:
				fileout.write(changelog)

		assert not change
