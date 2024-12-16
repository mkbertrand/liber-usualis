#!/usr/bin/env python3

# Copyright 2024 (AGPL-3.0-or-later), Miles K. Bertrand et al.

from collections import defaultdict
from datetime import date, datetime, timedelta
import copy
import json
import logging
import pathlib
import re
from typing import NamedTuple, Optional, Self, Set

from kalendar.pascha import geteaster, nextsunday
from kalendar.dies import leapyear, menses, mensum, numerals, latindate

data_root = pathlib.Path(__file__).parent.joinpath('data')

def load_data(p: str):
	data = json.loads(data_root.joinpath(p).read_text(encoding='utf-8'))

	# JSON doesn't support sets. Recursively find and replace anything that
	# looks like a list of tags with a set of tags.
	def recurse(obj):
		match obj:
			case dict():
				return {k: recurse(v) for k, v in obj.items()}
			case list():
				if all(type(x) is str for x in obj):
					return frozenset(obj)
				return [recurse(v) for v in obj]
			case _:
				return obj

	return recurse(data)

epiphanycycle = load_data('epiphany.json')
paschalcycle = load_data('paschal.json')
adventcycle = load_data('advent.json')
nativitycycle = load_data('nativity.json')
autumnalcycle = load_data('autumnalis.json')
movables = load_data('movables.json')
sanctoral = load_data('kalendar.json')
coincidencetable = load_data('coincidence.json')

threenocturnes = {'semiduplex','duplex-minus','duplex-majus','duplex-ii-classis','duplex-i-classis'}
ranks = {'feria','commemoratio','simplex'} | threenocturnes
octavevigiltags = {'habens-octavam','habens-vigiliam','vigilia-excepta','incipit-libri'}
feriae = ['dominica','feria-ii','feria-iii','feria-iv','feria-v','feria-vi','sabbatum']

class SearchResult(NamedTuple):
	date: date
	feast: Set[str]

	def __str__(self) -> str:
		return self.date.strftime('%a %Y-%m-%d') + ':' + str(self.feast)

class Kalendar:
	def __init__(self, year: int, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.kal: defaultdict = defaultdict(list)
		self.year = year

	def add_entry(self, date: date, entry: set | frozenset) -> SearchResult:
		if type(entry) is frozenset:
			entry = set(entry)
		assert type(entry) is set
		self.kal[date].append(entry)
		return SearchResult(date, entry)

	def __ior__(self, other) -> Self:
		for date0, entries in other.kal.items():
			self.kal[date0] += entries
		return self

	def keys(self):
		return self.kal.keys()

	def items(self):
		return self.kal.items()

	def __getitem__(self, key: date):
		return self.kal[key]

	def __repr__(self) -> str:
		return f'Kalendar(year={self.year!r})'

	def match(self, include: Set[str] = set(), exclude: Set[str] = set()):
		assert include.isdisjoint(exclude), f'{include!r} and {exclude!r} must be disjoint'
		for date0, entries in self.kal.items():
			if set().union(*entries).isdisjoint(exclude):
				for entry in entries:
					if entry >= include:
						yield SearchResult(date0, entry)

	def match_any(self, include: Set[str] = set(), exclude: Set[str] = set()) -> Optional[SearchResult]:
		# Check whether kal.match returns any matches
		return next(self.match(include, exclude), None)

	def match_unique(self, include: Set[str] = set(), exclude: Set[str] = set()) -> SearchResult:
		# Get the first match from kal.match
		it = self.match(include, exclude)
		try:
			match = next(it)
		except StopIteration as e:
			# Fail if zero matches
			raise RuntimeError(f'{self.year}: match_unique({include!r}, {exclude!r}) got no matches!') from e
		else:
			# Fail if multiple matches
			try:
				next(it)
			except StopIteration:
				pass
			else:
				raise RuntimeError(f'{self.year}: match_unique({include!r}, {exclude!r}) got more than one match!')
		return match

	def tagsindate(self, date: date) -> set:
		ret: Set[str] = set()
		for entry in self.kal.get(date, []):
			ret |= entry
		return ret

	# If mention is False there will be no mention that there was a feast in the original pre-tranfer date
	# The given entry must occur on match_date.
	def transfer_entry(self, match: SearchResult, *, target: Optional[date] = None, obstacles: Optional[Set[str]] = None, mention: bool = True) -> SearchResult:
		assert not (target is None and obstacles is None), 'Useless call to transfer!'
		match_date, entry = match
		newfeast = entry | {'translatum'}

		# Compute date
		if target is None:
			target = match_date
		newdate = target
		if obstacles is not None:
			while not self.tagsindate(newdate).isdisjoint(obstacles):
				newdate = newdate + timedelta(days=1)

		# Skip transfer if it's to the same day
		if newdate == match_date:
			logging.debug(f'{self.year}: {entry!r} already on {newdate}')
			return match

		entries = self[match_date]
		assert entry in entries

		if mention:
			# Modify matching entries
			entries[:] = [
				e - ranks - octavevigiltags | {'translatus-originalis'}
				if e is entry
				else e
				for e in entries
			]
		else:
			# Keep all but matching entries
			entries[:] = [e for e in entries if e is not entry]

		match = self.add_entry(newdate, newfeast)

		logging.debug(f'{self.year}: Transfer {entry!r} from {match_date} to {newdate}')
		assert match_date - timedelta(days=1) == newdate or match_date < newdate

		assert not (target is None and obstacles is None)

		return match

	# Automatically decide the suitable date whither the feast should be transferred
	# Fails if not exactly one feast matches
	def transfer(self, tags, *, exclude: Set[str] = set(), target: Optional[date] = None, obstacles: Optional[Set[str]] = None, mention: bool = True) -> SearchResult:
		match = self.match_unique(tags, exclude)
		return self.transfer_entry(match, target=target, obstacles=obstacles, mention=mention)

	# Transfer multiple feasts
	def transfer_all(self, tags, *, exclude: Set[str] = set(), obstacles: Optional[Set[str]] = None, mention: bool = True) -> None:
		for match in list(self.match(tags, exclude)):
			self.transfer_entry(match, obstacles=obstacles, mention=mention)


def kalendar(year: int) -> Kalendar:
	kal = Kalendar(year=year)

	def nearsunday(kalends: date):
		if kalends.isoweekday() < 4:
			return nextsunday(kalends, weeks=-1)
		else:
			return nextsunday(kalends, weeks=0)
	def todate(text: str, year0: int) -> date:
		m = re.match(r'(\d+)-(\d+)', text)
		if m is None:
			raise ValueError(f"Invalid date: {text}")
		return date(year0, int(m.group(1)), int(m.group(2)))

	i = date(year, 1, 1)
	while not i == date(year + 1, 1, 1):
		kal.add_entry(i, {'tempus', menses[i.month - 1], latindate(i)})
		i = i + timedelta(days=1)
	for i in range(0, 13):
		if i == 0:
			kalends = nearsunday(date(year - 1, 12, 1))
		else:
			kalends = nearsunday(date(year, i, 1))
		if i == 12:
			nextkalends = nearsunday(date(year + 1, 1, 1))
		else:
			nextkalends = nearsunday(date(year, i + 1, 1))
		j = 0
		while kalends + timedelta(weeks=j) != nextkalends:
			for k in range(0,7):
				if not (kalends + timedelta(weeks=j, days=k)).year == year:
					continue
				kal[kalends + timedelta(weeks=j, days=k)][0].add(feriae[k])
				kal[kalends + timedelta(weeks=j, days=k)][0].add(f'hebdomada-{numerals[j]}-{mensum[(i - 1) % 12]}')
			j += 1
		if i == 12 and nextkalends.year == year:
			for j in range(0,7):
				if (nextkalends + timedelta(days=j)).year == year + 1:
					break
				kal[nextkalends + timedelta(days=j)][0].add(feriae[j])
				kal[nextkalends + timedelta(days=j)][0].add('hebdomada-i-januarii')

	easter = geteaster(year)
	christmas = date(year, 12, 25)
	adventstart = nextsunday(christmas, weeks=-4)
	bases = {'dominica-i-adventus': nextsunday(christmas, weeks=-4),
		'pascha': geteaster(year),
		'dominica-i-decembris': nearsunday(date(year, 12, 1))}
	cycles = [adventcycle, paschalcycle, autumnalcycle]

	xxiiipentecost = easter + timedelta(weeks=30)
	xxivpentecost = adventstart - timedelta(weeks=1)

	epiphanysunday = nextsunday(date(year, 1, 7))

	xxiiipentecostentry: Optional[Set[str]] = None
	omittedepiphanyentry: Optional[Set[str]] = None

	for cycle in cycles:
		for entry in cycle:
			kal.add_entry(bases[entry['basis']] + timedelta(days=entry['offset']), entry['tags'])

	# Epiphany Sundays
	epiphanyweek = 0
	while epiphanysunday + timedelta(weeks=epiphanyweek) != easter - timedelta(weeks=9):
		for i in range(0,7):
			kal.add_entry(epiphanysunday + timedelta(weeks=epiphanyweek, days=i), epiphanycycle[epiphanyweek][i]['tags'] | {'post-epiphaniam'})
		epiphanyweek += 1
	for i in range(0, 6 - epiphanyweek):
		sunday = xxivpentecost - timedelta(weeks=i + 1)
		if sunday != xxiiipentecost:
			for j in range(0,7):
				kal.add_entry(sunday + timedelta(days=j), epiphanycycle[5 - i][j]['tags'] | {'post-pentecosten'})
		else:
			omittedepiphanyentry = epiphanycycle[5 - i][0]['tags']

	# Nativity & Epiphany
	for entry in nativitycycle:
		date0 = todate(entry['date'], year)
		kal.add_entry(date0, entry['tags'])
	kal.add_entry(nextsunday(christmas), {'dominica','nativitas','dominica-infra-octavam','semiduplex'})
	if date(year, 1, 6).isoweekday() == 7:
		epiphanysunday = date(year, 1, 12)
		kal.transfer({'epiphania','dominica'}, target=epiphanysunday)

	currday = 2
	for i in range(0, 6):
		if not date(year, 1, 7 + i) == epiphanysunday:
			kal.add_entry(date(year, 1, 7 + i), {'epiphania','semiduplex','infra-octavam','dies-' + numerals[currday - 1]})
			currday += 1
	kal.add_entry(date(year, 1, 13), {'epiphania','dies-octava','duplex-minus'})

	# List of inferred feasts that get merged in later
	buffer = Kalendar(year=year)

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
		for match_date in set([i.date for i in matches]):
			kal.add_entry(match_date, entry['tags'])

	# Octave and Vigil Processing
	for ent_date, entries in kal.items():
		for entry in entries:
			entry_base = entry - ranks - octavevigiltags
			if 'habens-octavam' in entry and 'octava-excepta' not in entry:
				for k in range(1,7):
					date0 = ent_date + timedelta(days=k)
					if 'quadragesima' in kal.tagsindate(date0):
						break
					entrystripped = entry_base | {'semiduplex','infra-octavam','dies-' + numerals[k]}
					if date0.isoweekday() == 7:
						entrystripped.add('dominica-infra-octavam')
					# If a certain day within an Octave is manually entered, do not create one automatically
					if kal.match_any(entrystripped) is None:
						buffer.add_entry(date0, entrystripped)
				date0 = ent_date + timedelta(weeks=1)
				if 'quadragesima' in kal.tagsindate(date0):
					continue
				entrystripped = entry_base | {'duplex-minus', 'dies-octava'}
				if date0.isoweekday() == 7:
					entrystripped.add('dominica-infra-octavam')
				# If a certain day within an Octave is manually entered, do not create one automatically
				if kal.match_any(entrystripped) is None:
					buffer.add_entry(date0, entrystripped)
			if 'habens-vigiliam' in entry and 'vigilia-excepta' not in entry:
				entrystripped = entry_base | {'vigilia','poenitentialis','simplex'}
				buffer.add_entry(ent_date - timedelta(days=1), entrystripped)

	kal |= buffer
	buffer.kal.clear()

	# Movables
	entries = copy.deepcopy(movables)
	for entry in entries:
		matches = None
		if type(entry['occurrence']) is list:
			matches = []
			for i in entry['occurrence']:
				matches.extend(kal.match(i, entry.get('excluded', set())))
		else:
			matches = kal.match(entry['occurrence'], entry.get('excluded', set()))
		offset = entry['offset'] if 'offset' in entry else 0
		for match_date in set([i.date for i in matches]):
			kal.add_entry(match_date + timedelta(days=offset), entry['tags'])

	# 23rd Sunday Pentecost, 5th Sunday Epiphany Saturday transfer
	if xxiiipentecostentry:
		xxiiipentecostentry = set(xxiiipentecostentry)
		xxiiipentecostentry.add('translatum')
		i = 1
		while i < 7:
			if kal.tagsindate(xxivpentecost - timedelta(days=i)).isdisjoint(threenocturnes):
				kal.add_entry(xxivpentecost - timedelta(days=i), xxiiipentecostentry)
				break
			else:
				i += 1
		if i == 7:
			xxiiipentecostentry.add('simplex')
			xxiiipentecostentry.discard('semiduplex')
			kal.add_entry(xxivpentecost - timedelta(days=1), xxiiipentecostentry)
	if omittedepiphanyentry:
		omittedepiphanyentry = set(omittedepiphanyentry)
		omittedepiphanyentry.add('translatum')
		septuagesima = easter - timedelta(weeks=9)
		i = 1
		while i < 7:
			if kal.tagsindate(septuagesima - timedelta(days=i)).isdisjoint(threenocturnes):
				kal.add_entry(septuagesima - timedelta(days=i), omittedepiphanyentry)
				break
			else:
				i += 1
		if i == 7:
			omittedepiphanyentry.add('simplex')
			omittedepiphanyentry.discard('semiduplex')
			kal.add_entry(septuagesima - timedelta(days=1), omittedepiphanyentry)

	# RestartRequest is used to define what extent of the coincidencetable should be rechecked and what days should be examined in that restart.
	class RestartRequest(NamedTuple):
		# The reason these are needed is to specify which days should be rechecked under previous coincidencetable rules.  Obviously the whole kalendar could just be rechecked for all rules, but that is super slow and miserable.
		days: list
		rulenumber: int

	roletags = {'primarium', 'commemoratio', 'omissum', 'tempus'}
	roletagsordered = ['primarium', 'commemoratio', 'omissum', 'tempus']

	for entrydate, entries in kal.items():
		for entry in entries:
			if entry.isdisjoint(roletags):
				entry.add('primarium')

	# perform_action() fulfils the action specified by a certain rule in the coincidencetable. The return is either None, or a RestartRequest.
	def perform_action(instruction, day, target, rulenumber):
		if instruction['response'] == 'combina':
			target[0] |= target[1]
			# If there are multiple role tags (which are mutually exclusive), it picks the highest one to use and removes the others
			if len(target[0] & roletags) > 1:
				for i in roletagsordered:
					if i in target[0]:
						target[0] -= roletags
						target[0].add(i)
						break

			kal[day].remove(target[1])
			return RestartRequest([day], rulenumber)
		elif instruction['response'] == 'dele':
			kal[day].remove(target)
			return
		elif instruction['response'] == 'transfer':
			target.add('translatum')
			transferday = (day + timedelta(days=instruction['movement'])) if type(instruction['movement']) is int else kal.match_unique(instruction['movement']).date
			kal[transferday].append(target)
			kal[day].remove(target)
			return RestartRequest([day, transferday], rulenumber)
		elif instruction['response'] == 'errora':
			raise RuntimeError(f'Unexpected coincidence on day {kal[day]} involving {target}')
		# These remaining conditions are when the response is anything else, which means that the string(s) in the response are tags to be given to the target.
		elif type(instruction['response']) is frozenset:
			# Prevents redundant instructions from being executed. Not perfectly optimized. This whole algo is being rewritten anyway so it can suck for now
			if instruction['response'] <= target:
				return 1
			if not instruction['response'].isdisjoint(roletags):
				target -= roletags
			target |= instruction['response']
			return RestartRequest([day], rulenumber)
		else:
			# Same as previous
			if instruction['response'] in target:
				return 1
			if not type(instruction['response']) is str:
				raise RuntimeError(type(instruction['response']))
			if instruction['response'] in roletags:
				target -= roletags
			target.add(instruction['response'])
			return RestartRequest([day], rulenumber)

	# Applies only a specified rule for a certain day. May be recursed when perform_action returns None so that the whole process() doesn't need to be restarted.
	def applyruleonday(rule, i, rulenumber):
		for tags in kal[i]:
			if rule['include'] <= tags and not ('exclude' in rule and rule['exclude'] <= tags):
				if type(rule['response']) is not list:
					response = perform_action(rule, i, tags, rulenumber)
					if response is None:
						return applyruleonday(rule, i, rulenumber)
					elif response != 1:
						return response
				else:
					for secondaryrule in rule['response']:
						for secondarytags in kal[i]:
							if secondaryrule['include'] <= secondarytags and not ('exclude' in secondaryrule and secondaryrule['exclude'] <= secondarytags) and not tags == secondarytags:
								target = tags
								if 'target' in secondaryrule and secondaryrule['target'] == 'b':
									target = secondarytags
								elif 'target' in secondaryrule and secondaryrule['target'] == 'ab':
									target = [tags, secondarytags]
								# Performs the action. If no restart is necessary (IE response is None) it recurses the applyruleonday function since a rule could be applied multiple times in a single day, but it can't just continue the existing loop because an element could've been removed.
								response = perform_action(secondaryrule, i, target, rulenumber)
								if response is None:
									return applyruleonday(rule, i, rulenumber)
								elif response != 1:
									return response
		return None

	# This is where the rules are looped through and applied to either all days, or just specified days (if they are previously checked rules being retroactively rechecked).
	def process(promptingresponse):
		for rulenumber in range(0, len(coincidencetable)):
			for day in (promptingresponse.days if rulenumber < promptingresponse.rulenumber else kal.keys()):
				response = applyruleonday(coincidencetable[rulenumber], day, rulenumber)
				if not response is None:
					return response
		return None

	# This is the response that process() returns.  It has to be out here so that it persists for the loop to reuse it.
	workingresponse = RestartRequest(None, 0)
	# Continually reruns process with the specified RestartRequest, which is just a NamedTuple which specifies until which rule only a list of specified days should be checked against previous rules. Previous rules need to be checked since sometimes a previously inapplicable rule may be made applicable because another tag is added to a tagset.
	while True:
		workingresponse = process(workingresponse)
		if workingresponse is None:
			break

	return kal

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
	ret = dict(sorted(kalendar(args.year).items()))

	# Convert datestrings to strings and sets into lists
	ret = {str(k): [list(ent) for ent in v] for k, v in ret.items()}
	# Write JSON output
	args.output.write(json.dumps(ret) + "\n")
