# Copyright 2025 (AGPL-3.0-or-later), Miles K. Bertrand et al.

from datetime import date, timedelta
import json
import pathlib

data_root = pathlib.Path(__file__).parent

def leapyear(year):
    return year % 4 == 0 and (year % 400 == 0 or year % 100 != 0)

def goldnumber(year):
	return year % 19 + 1

epactsymbols = ['i', 'ii', 'iii', 'iv', 'v',
		'vi', 'vii', 'viii', 'ix', 'x',
		'xi', 'xii', 'xiii', 'xiv', 'xv',
		'xvi', 'xvii', 'xviii', 'xix', 'xx',
		'xxi', 'xxii', 'xxiii', 'xxiv', 'xxv',
		'xxvi', 'xxvii', 'xxviii', 'xxix', '*']
def epact(year):
	century = year // 100 + 1
	correction_lunar = 8*(century - 15) // 25
	correction_solar = 3*(century - 16) // 4
	epact = (11 * goldnumber(year) + (correction_lunar - correction_solar - 10)) % 30
	if epact == 25 and goldnumber(year) > 11:
		return '25'
	else:
		return epactsymbols[epact - 1]

# F-r and F-n correspond to F rubra and F nigra
litterae = {
		'i': 'a', 'ii': 'b', 'iii': 'c', 'iv': 'd', 'v': 'e', 'vi': 'f', 'vii': 'g', 'viii': 'h', 'ix':  'i', 'x': 'k', 'xi': 'l', 'xii': 'm', 'xiii': 'n', 'xiv': 'p', 'xv': 'q', 'xvi': 'r', 'xvii': 's', 'xviii': 't', 'xix': 'u',
		'xx': 'A', 'xxi': 'B', 'xxii': 'C', 'xxiii': 'D', 'xxiv': 'E', 'xxv': 'F-r', '25': 'F-n', 'xxvi': 'G', 'xxvii': 'H', 'xxiii': 'M', 'xxiv': 'N', '*': 'P'
		}
letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'u', 'A', 'B', 'C', 'D', 'E', 'F-r', 'F-n', 'G', 'H', 'M', 'N', 'P']
def littera(year):
	return litterae[epact(year)]

def gen_lunar_chart():
	locations = {
			'a': 2, 'b': 3, 'c': 4, 'd': 5, 'e': 6, 'f': 7, 'g': 8, 'h': 9, 'i': 10, 'k': 11, 'l': 12, 'm': 13, 'n': 14, 'p': 15, 'q': 16, 'r': 17, 's': 18, 't': 19, 'u': 20,
			'A': 21, 'B': 22, 'C': 23, 'D': 24, 'E': 25, 'F-r': 26, 'F-n': 26, 'G': 27, 'H': 28, 'M': 29, 'N': 30, 'P': 1
			}

	twelveletters = ['N', 'P', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'u', 'A', 'B', 'C', 'D', 'E', 'F-r']
	twelves = [30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30]
	thirteens = [30, 30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 29]
	start = date(2001, 1, 1)

	indices = dict()

	days = {date(2001, 1, 1): copy.deepcopy(locations)}

	for i in range(0, 364):
		for j in locations.keys():
			if (locations[j] == 30):
				locations[j] = 1
			elif (locations[j] != 29):
				locations[j] += 1
			else:
				key = twelves[indices.get(j, 0)] if j in twelveletters else thirteens[indices.get(j, 0)]
				if key == 29:
					locations[j] = 1
				else:
					locations[j] += 1
				indices[j] = indices.get(j, 0) + 1

		days[list(days.keys())[-1] + timedelta(days=1)] = copy.deepcopy(locations)

	# For debugging
	# ret = {str(k): ' '.join([f'{i} {j}' for i, j in v.items()]) for k, v in days.items()}
	ret = {str(k)[5:]: v for k, v in days.items()}

	with open(data_root.joinpath('lunar_chart.json'), 'w') as f:
		f.write(json.dumps(ret))

import os
if not os.path.exists(data_root.joinpath('lunar_chart.json')):
	import copy
	gen_lunar_chart()

lunar_chart = json.loads(data_root.joinpath('lunar_chart.json').read_text(encoding='utf-8'))

def lunardate(day):
	search = str(day)[5:]
	letter = littera(day.year)
	if leapyear(day.year):
		if day >= date(day.year, 2, 25):
			if day <= date(day.year, 2, 29):
				search = str(day - timedelta(days=1))[5:]
	return lunar_chart[search][letter]

