#!/usr/bin/env python3

# Copyright 2024 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import os
import pathlib
import json
import copy
from datetime import date, datetime, timedelta
import functools
import prioritizer
import datamanage
import warnings
import logging
import sys
import functools

import psalms

defaultpile = {'formulae', 'litaniae-sanctorum'}

@functools.lru_cache(maxsize=64)
def getcategory(root, category):
	return datamanage.load_data(f'data/{root}/categoriae/{category}.json')

def flattensetlist(sets):
	ret = set()
	for i in sets:
		ret |= i
	return ret

def flatcat(root, category):
	return flatcat0(getcategory(root, category))

def flatcat0(category):
	if type(category) is set:
		return category
	elif type(category) is list:
		return flattensetlist(category)
	else:
		raise RuntimeError()

@functools.lru_cache(maxsize=16)
def expandcat(root, category):
	return expandcat0(root, getcategory(root, category))

def expandcat0(root, category):
	if type(category) is set or type(category) is frozenset:
		ret = set()
		for i in category:
			if i.startswith('/'):
				ret |= expandcat(root, i[1:])
			else:
				ret.add(i)
		return ret
	elif type(category) is list:
		return expandcat0(root, flattensetlist(category))
	else:
		raise RuntimeError(str(category))

def matches(root, tag, tags):
	if tag.startswith('/'):
		return check(getcategory(root, tag[1:]), tags)
	else:
		return tag in tags

def check(root, category, tags):
	return check0(root, getcategory(root, category))

def check0(root, category, tags):
	if type(category) is set or type(category) is frozenset:
		return any([matches(root, tag, tags) for tag in category])
	elif type(category) is list:
		return any([check0(root, i, tags) for i in categories])
	else:
		raise RuntimeError()


def contradicts(root, category, tags):
	return contradicts0(root, getcategory(root, category), tags)

def contradicts0(root, category, tags):
	if type(category) is set or type(category) is frozenset:
		return False
	elif type(category) is list:
		return any([sum([matches(root, tag, tags) for tag in subcat]) > 1 for subcat in category])
	else:
		return RuntimeError()

implicationtable = datamanage.load_data('data/breviarium-1888/tag-implications.json')

def prettyprint(j):
	def recurse(obj):
		match obj:
			case dict():
				return {k: recurse(v) for k, v in obj.items()}
			case list():
				return [recurse(v) for v in obj]
			case set() | frozenset():
				pass
			case str():
				if obj.startswith('https'):
					print(obj)
				else:
					pieces = obj.split('/')
					if len(pieces[0]) != 0:
						print(pieces[0])
					for i in pieces[1:]:
						print(' ' + i)
	recurse(j)

def anysearch(query, pile):
	for i in pile:
		if type(i['tags']) is list:
			for j in i['tags']:
				if j.issubset(query):
					ret = copy.deepcopy(i)
					ret['tags'] = copy.deepcopy(j)
					yield ret
		elif i['tags'].issubset(query):
			yield copy.deepcopy(i)

# Numerical rank of query tagset according to a table of tagsets. Outputs a binary number with 1 in positions where the tagset at that table position was a subset of the query.
def discriminate(root, table: str, tags: set):
	table = datamanage.getdiscrimina(root, table)
	val = 0
	for i in range(0, len(table)):
		if len(table[i]) == 1 and list(table[i])[0].startswith('/'):
			val |= (not tags.isdisjoint(expandcat(root, list(table[i])[0]))) << (len(table) - i - 1)
		else:
			include = set(filter(lambda a: a[0] != '!', table[i]))
			exclude = {a[1:] for a in table[i] - include}
			# Adds 1 or 0 lower on the number as the position in the table increases using binary operators. The higher the position in the table (IE the farther down in the table), the lower precedence something is.
			val |= include.issubset(tags) and exclude.isdisjoint(tags) << (len(table) - i - 1)
	return val

def search(root, query, pile, multipleresults = False, multipleresultssort = None, rootappendix = ''):

	for i in query:
		if '/' in i:
			try:
				return {'tags': {i}, 'datum':psalms.get(root + rootappendix, i)}
			except FileNotFoundError:
				return None

	result = list(sorted(list(anysearch(query, pile)), key=lambda a: discriminate(root, 'general', a['tags']), reverse=True))
	if len(result) == 0:
		warnings.warn(f'0 tags found for queries {list(query)}')
		return None
	bestvalue = discriminate(root, 'general', result[0]['tags'])
	result = list(filter(lambda a: discriminate(root, 'general', a['tags']) == bestvalue, result))
	if len(result) == 1:
		return result[0]
	result = list(sorted(result, key=lambda a: len(a['tags']), reverse=True))
	if len(result[0]['tags']) != len(result[1]['tags']):
		return result[0]
	elif not multipleresults:
		raise RuntimeError(f'Multiple equiprobable results for queries {query}:\n{result[0]}\n{result[1]}')
	else:
		return list(sorted(filter(lambda a : len(a['tags']) == len(result[-1]['tags']), result), multipleresultssort))

# Special commemoration handling. Commemorations are hard because they rely on eachother and differ in number by day.
def handlecommemorations(root, item, selected, alternates):
		ret = []
		commemorations = sorted(list(filter(lambda a : 'commemoratio' in a, alternates)), key=lambda a:discriminate(root, 'rank', a), reverse=True)
		for i in commemorations:
			probablepile = datamanage.getpile(root, defaultpile | item | i)
			ret.append(process(root, {'formula','formula-commemorationis'}, i | (item - {'commemorationes'}), alternates, probablepile))
		if len(commemorations) != 0:
			probablepile = datamanage.getpile(root, defaultpile | commemorations[-1])
			ret.append(process(root, {'collecta','terminatio','commemoratio'}, commemorations[-1] | (item - {'commemorationes'}), alternates, probablepile))
		return ret

def process(root, item, selected, alternates, pile):
	if item is None:
		return 'Absens'
	if selected is None:
		selected = set()
	if alternates is None:
		alternates = []
	if pile is None:
		pile = []

	if 'commemorationes' in item:
		return handlecommemorations(root, item, selected, alternates)

	# Within the data, a set (represented in JSON as a list of strings) is a euphemism for from: tags
	if type(item) is set or type(item) is frozenset:
		item = {'from':item}

	if 'reference' in item:
		alternates = copy.deepcopy(alternates)
		alternates.append(selected & expandcat(root, 'temporale'))
		# Just in case an item needs to change depending on whether it is a reference
		selected = item['reference'] | {'referens'}
		pile = datamanage.getpile(root, defaultpile | selected)
		response = process(root, search(root, selected, pile), selected - expandcat(root, 'objecta'), alternates, pile)
		return response

	if 'from' in item:
		result = None
		if not any('/' in i for i in item['from']):
			for i in range(len(alternates)):
				# Basically if the from is explicitly calling for some day's propers, remove the other day context to facilitate this
				if 'occurrens' in item['from'] and len(item['from'] & expandcat(root, 'temporale')) != 0 and item['from'] & expandcat(root, 'temporale') <= alternates[i]:
					item['from'] -= {'occurrens'}
					alternates = copy.deepcopy(alternates)
					alternates.append(selected - expandcat(root, 'positionales'))
					selected = alternates.pop(i) | (selected & expandcat(root, 'positionales'))
					pile = datamanage.getpile(root, defaultpile | item['from'] | selected)
					result = search(root, item['from'] | selected, pile)
					break

				# If there is an alternate with a specific object and position, it should be imposed on the from tag even if it doesn't otherwise want a different day's item
				elif item['from'] <= alternates[i]:
					alternates = copy.deepcopy(alternates)
					alternates.append(selected)
					if contradicts(root, 'positionales', item['from'] | alternates[i] | selected):
						selected = alternates.pop(i) - expandcat(root, 'objecta')
					else:
						selected = alternates.pop(i) - expandcat(root, 'objecta') | (selected & expandcat(root, 'positionales'))
					pile = datamanage.getpile(root, defaultpile | item['from'] | selected)
					result = search(root, item['from'] | selected, pile)
					break

		if result is None:
			# Only remove tags referring to propers and commons and whatnot if a different set is suggested
			if len(item['from'] & expandcat(root, 'temporale')) != 0:
				selected -= expandcat(root, 'temporale')
				selected |= item['from'] & expandcat(root, 'temporale')
				print(item['from'])
				print(selected)
				pile = datamanage.getpile(root, defaultpile | item['from'] | selected)

			# Only remove tags referring to positional things like nocturna-i, vesperae, etc if mutually exclusive positionals are specified, but otherwise let them carry over
			if contradicts(root, 'positionales', item['from'] | selected):
				selected -= expandcat(root, 'positionales')
			result = search(root, item['from'] | selected, pile)

		# If result is still None at this point, just tell user what was searched for
		if result is None:
			# It has to be sorted for testing purposes
			return str(sorted(list(item['from'] | selected)))
		# Removes tags referring to things like Antiphons, Responsories, etc
		selected = (selected | item['from']) - expandcat(root, 'objecta')
		response = process(root, result, selected, alternates, pile)

		if 'tags' in item:
			response = {'tags': item['tags'], 'datum': response}
		return response

	elif type(item['datum']) is list:
		ret = []
		for i in item['datum']:
			if type(i) is str:
				ret.append(i)
			else:
				iprocessed = process(root, i, selected, alternates, pile)
				if iprocessed is None:
					ret.append('Absens')
				elif type(iprocessed) is list:
					ret.extend(iprocessed)
				else:
					ret.append(iprocessed)
		item['datum'] = ret if len(ret) != 1 else ret[0]

	return item

def generate(root, day, hour: str):
	hours = hour.split('+')
	assert set(hours).isdisjoint({'vesperae', 'completorium'}) or set(hours).isdisjoint({'matutinum', 'laudes', 'tertia', 'sexta', 'nona'})
	tags = copy.deepcopy(prioritizer.getvespers(day) if not set(hours).isdisjoint({'vesperae', 'completorium'}) else prioritizer.getdiurnal(day))
	for i in tags:
		for j in implicationtable:
			if j['tags'].issubset(i):
				i |= j['implies']
	tags = [frozenset(i) for i in tags]
	primary = list(filter(lambda i: 'primarium' in i, tags))[0]
	tags.remove(primary)
	pile = datamanage.getpile(root, defaultpile | primary | set(hours))

	lit = []
	for hour in hours:
		if hour in {'matutinum', 'laudes', 'prima', 'tertia', 'sexta', 'nona', 'vesperae', 'completorium', 'psalmi-graduales', 'psalmi-poenitentiales'}:
			lit.extend([{'nomen-ritus', hour}, {'hora', hour}])
		else:
			lit.append({'hora', hour})
	return process(root, {'tags':{'ritus'},'datum':lit}, primary, tags, pile)

if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser(
		formatter_class=argparse.ArgumentDefaultsHelpFormatter,
		description='Divine Office Hours',
	)

	parser.add_argument(
		'-v',
		'--verbosity',
		metavar='LEVEL',
		type=lambda s: s.upper(),
		choices=logging.getLevelNamesMapping().keys(),
		default=logging.getLevelName(logging.getLogger().getEffectiveLevel()),
		const='debug',
		nargs='?',
		help='Verbosity',
	)

	parser.add_argument(
		'-o',
		'--output',
		type=argparse.FileType('w'),
		default='-',
		help='Output filename',
	)

	parser.add_argument(
		'-r',
		'--root',
		type=str,
		default='breviarium-1888',
		help='Data Root for Content',
	)

	parser.add_argument(
		'-d',
		'--date',
		type=str,
		default=str(date.today()),
		help='Date to generate',
	)

	defaulthour = None

	match datetime.now().hour:
		case 0 | 2 | 3 | 4 | 5:
			defaulthour = 'ante-officium+matutinum+laudes+post-officium'
		case 6 | 7:
			defaulthour = 'ante-officium+prima+post-officium'
		case 8 | 9 | 10:
			defaulthour = 'ante-officium+tertia+post-officium'
		case 11 | 12 | 13:
			defaulthour = 'ante-officium+sexta+post-officium'
		case 14 | 15:
			defaulthour = 'ante-officium+nona+post-officium'
		case 16 | 17 | 18 | 19:
			defaulthour = 'ante-officium+vesperae+post-officium'
		case 20 | 21 | 22 | 23:
			defaulthour = 'ante-officium+completorium+post-officium'

	parser.add_argument(
		'-hr',
		'--hour',
		type=str,
		default=str(defaulthour),
		help='Liturgical hour to generate',
	)

	args = parser.parse_args()

	if args.verbosity:
		logging.getLogger().setLevel(args.verbosity)

	# Generate kalendar
	day = datetime.strptime(args.date, '%Y-%m-%d').date()
	ret = generate(args.root, day, args.hour)

	if args.output == sys.stdout:
		prettyprint(ret)
	else:
		# Write JSON output
		args.output.write(datamanage.dump_data(ret) + '\n')

