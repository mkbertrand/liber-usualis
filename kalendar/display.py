#!/usr/bin/env python3

# Copyright 2025 (AGPL-3.0-or-later), Miles K. Bertrand et al.

# Creates display Kalendars

import logging
import copy
from datetime import date, datetime, timedelta
import json

import kalendar.datamanage as datamanage
import kalendar.kalendar as kalendar
from kalendar.kalendar import SearchResult, Kalendar, todate, threenocturnes, ranks, octavevigiltags, feriae, load_data, noprimarium, process
from kalendar.pascha import geteaster
from kalendar.dies import leapyear, menses, mensum, numerals, latindate

adventcycle = load_data('de-adventu.json')
epiphanycycle = load_data('epiphania.json')
paschalcycle = load_data('de-paschali.json')
sanctoral = load_data('kalendarium.json')
nativitycycle = load_data('in-tempore-nativitatis.json')

def kalendar() -> Kalendar:
	kal = Kalendar()

	easter = date(2001, 4, 9)
	# 2001 is just chosen randomly since a year is needed for date
	christmas = date(2001, 12, 25)
	adventstart = date(2001, 12, 1)
	bases = {'dominica-i-adventus': adventstart, 'pascha': easter}

	i = date(2001, 1, 1)
	while not i == date(2002, 1, 1):
		kal.add_entry(i, {'tempus', menses[i.month - 1], latindate(i)})
		i = i + timedelta(days=1)
	for i in range(0, 12):
		kalends = date(2001, i + 1, 1)
		for j in range(0, 4):
			for k in range(0,7):
				if not (kalends + timedelta(weeks=j, days=k)).year == 2001:
					continue
				kal.add_entry(kalends + timedelta(weeks=j, days=k), {feriae[k], f'hebdomada-{numerals[j]}-{mensum[i % 12]}'})

	cycles = [adventcycle, paschalcycle]

	xxiiipentecost = easter + timedelta(weeks=30)
	xxivpentecost = adventstart - timedelta(weeks=1)

	epiphanysunday = date(2001, 1, 7)

	# Octave Processing
	def octavate(ent_date, entry):
		if 'habens-octavam' in entry and 'octava-excepta' not in entry:
			entry_base = entry - ranks - octavevigiltags
			for k in range(1,7):
				date0 = ent_date + timedelta(days=k)
				entrystripped = entry_base | {'semiduplex','infra-octavam','dies-' + numerals[k]}
				if k == 1:
					entrystripped |= {'dominica-infra-octavam'}
				# If a certain day within an Octave is manually entered, do not create one automatically
				if kal.match_any(entrystripped) is None:
					kal.add_entry(date0, entrystripped)
			date0 = ent_date + timedelta(weeks=1)
			entrystripped = entry_base | {'duplex-minus', 'dies-octava'}
			# If a certain day within an Octave is manually entered, do not create one automatically
			if kal.match_any(entrystripped) is None:
				kal.add_entry(date0, entrystripped)

	for cycle in cycles:
		for entry in cycle:
			kal.add_entry(bases[entry['basis']] + timedelta(days=entry['offset']), entry['tags'])
			octavate(bases[entry['basis']] + timedelta(days=entry['offset']), entry['tags'])

	# Epiphany Sundays
	for epiphanyweek in range(0, 6):
		for i in range(0,7):
			kal.add_entry(epiphanysunday + timedelta(weeks=epiphanyweek, days=i), epiphanycycle[epiphanyweek][i]['tags'] | {'post-epiphaniam'})

	return kal

def kalendar2() -> Kalendar:
	kal = Kalendar()

	i = date(2001, 1, 1)
	while not i == date(2002, 1, 1):
		kal.add_entry(i, {'tempus', latindate(i)})
		i = i + timedelta(days=1)

	# Octave Processing
	def octavate(ent_date, entry):
		if 'habens-octavam' in entry and 'octava-excepta' not in entry:
			entry_base = entry - ranks - octavevigiltags
			for k in range(1,7):
				date0 = ent_date + timedelta(days=k)
				entrystripped = entry_base | {'semiduplex','infra-octavam','dies-' + numerals[k]}
				if k == 1:
					entrystripped |= {'dominica-infra-octavam'}
				# If a certain day within an Octave is manually entered, do not create one automatically
				if kal.match_any(entrystripped) is None:
					kal.add_entry(date0, entrystripped)
			date0 = ent_date + timedelta(weeks=1)
			entrystripped = entry_base | {'duplex-minus', 'dies-octava'}
			# If a certain day within an Octave is manually entered, do not create one automatically
			if kal.match_any(entrystripped) is None:
				kal.add_entry(date0, entrystripped)

	movables = []
	octaveagenda = []
	# Sanctorals
	entries = copy.deepcopy(sanctoral)
	for entry in entries:
		matches = None
		if type(entry['occurrence']) is list:
			matches = []
			for i in entry['occurrence']:
				matches.extend(kal.match(i, entry.get('excluded', set())))
		else:
			matches = kal.match(entry['occurrence'], entry.get('excluded', set()))
		offset = entry['offset'] if 'offset' in entry else 0
		matches = list(matches)
		if len(matches) == 0:
			if 'generic-occurrence' in entry:
				entry['occurrence'] = entry['generic-occurrence']
			movables.append(entry)
		for match_date in set([i.date for i in matches]):
			for tagset in entry['tags'] if type(entry['tags']) is list else [entry['tags']]:
				kal.add_entry(match_date + timedelta(days=offset), tagset)
				if 'habens-octavam' in tagset and 'octava-excepta' not in tagset:
					octaveagenda.append((match_date + timedelta(days=offset), tagset))

	for i in octaveagenda:
		octavate(i[0], i[1])

	# Nativity & Epiphany
	for entry in nativitycycle:
		for tagset in entry['tags'] if type(entry['tags']) is list else [entry['tags']]:
			kal.add_entry(kal.match_unique(entry['occurrence']).date, tagset)

	for i in range(0, 7):
		kal.add_entry(date(2001, 1, 7 + i), {'epiphania','semiduplex','infra-octavam','dies-' + numerals[i + 1]})

	kal.add_entry(date(2001, 1, 13), {'epiphania','dies-octava','duplex-minus','per-octavam-epiphaniae'})

	for entrydate, entries in kal.items():
		for entry in entries:
			if entry.isdisjoint(noprimarium):
				entry.add('primarium')

	process(kal)

	ret = []
	for (k, i) in kal.items():
		if len(i) == 1:
			continue
		ret0 = {'occurrence': i[0] - {'tempus'}, 'tags': []}
		primary = list(filter(lambda p: 'primarium' in p, i[1:]))
		if len(primary) != 0:
			ret0['tags'].append(primary[0])

		noprimary = list(filter(lambda p: not 'primarium' in p, i[1:]))
		ret0['tags'].extend(noprimary)
		ret.append(ret0)
	ret.extend(movables)
	return ret

if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser(
		formatter_class=argparse.ArgumentDefaultsHelpFormatter,
		description="Liturgical calendar generator",
	)

	parser.add_argument(
		"-v",
		"--verbosity",
		metavar="LEVEL",
		type=lambda s: s.upper(),
		choices=logging.getLevelNamesMapping().keys(),
		default=logging.getLevelName(logging.getLogger().getEffectiveLevel()),
		const="debug",
		nargs="?",
		help="Verbosity",
	)

	parser.add_argument(
		"-o",
		"--output",
		type=argparse.FileType("w"),
		default="-",
		help="Output filename",
	)

	parser.add_argument(
		"-y",
		"--year",
		type=int,
		default=datetime.now().year,
		help="Year to generate",
	)

	args = parser.parse_args()

	if args.verbosity:
		logging.getLogger().setLevel(args.verbosity)

	# Generate kalendar
	ret = dict(sorted(kalendar().items()))

	# Convert datestrings to strings and sets into lists
	ret = {str(k): [list(ent) for ent in v] for k, v in ret.items()}
	# Write JSON output
	args.output.write(json.dumps(ret) + "\n")
