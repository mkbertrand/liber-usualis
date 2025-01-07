#!/usr/bin/env python3

# Copyright 2024 (AGPL-3.0-or-later), Miles K. Bertrand et al.

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

import psalms

defaultpile = {'formulae'}

def dump_data(j):

	# JSON doesn't like sets, so turn sets back into lists for JSON encoding.

	def recurse(obj, key=None):
		match obj:
			case dict():
				return {k: recurse(v, key=k) for k, v in obj.items()}
			case list():
				return [recurse(v) for v in obj]
			case set() | frozenset():
				if all(type(x) is str for x in obj):
					return sorted(list(obj))
				return [recurse(v) for v in obj]
			case _:
				return obj

	return json.dumps(recurse(j))

def flattensetlist(sets):
	ret = set()
	for i in sets:
		ret |= i
	return ret

implicationtable = datamanage.load_data('data/breviarium-1888/tag-implications.json')

# List of tags which are reserved for ID'ing content (like chapters, antiphons, etc)
objects = datamanage.load_data('data/breviarium-1888/categoriae/objecta.json')
positionals2d = datamanage.load_data('data/breviarium-1888/categoriae/positionales.json')
positionals = flattensetlist(positionals2d)
propria = datamanage.load_data('data/breviarium-1888/categoriae/propria.json')

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
	if not tags.isdisjoint(propria):
		tags |= {':propria'}
	for i in range(0, len(table)):
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
		alternates.append(selected - objects - positionals)
		# Just in case an item needs to change depending on whether it is a reference
		selected = item['reference'] | {'referens'}
		pile = datamanage.getpile(root, defaultpile | selected)
		response = process(root, search(root, selected, pile), selected - objects, alternates, pile)
		return response

	if 'from' in item:
		result = None
		for i in range(len(alternates)):
			if len(item['from'] - objects - positionals) != 0 and item['from'] - objects - positionals <= alternates[i]:
				alternates = copy.deepcopy(alternates)
				alternates.append(selected - positionals)
				selected = alternates.pop(i) | (selected & positionals)
				break
			elif item['from'] <= alternates[i]:
				result = search(root, item['from'] | alternates[i], pile)
				alternates = copy.deepcopy(alternates)
				alternates.append(selected)
				selected = alternates.pop(i) - objects | (selected & positionals)
				break

		selected = copy.deepcopy(selected)
		# Only remove tags referring to positional things like nocturna-i, vesperae, etc if mutually exclusive positionals are specified, but otherwise let them carry over
		if any([len(i & (item['from'] | selected)) > 1 for i in positionals2d]):
			selected -= positionals
		if result is None:
			result = search(root, item['from'] | selected, pile)
		if result is None:
			# It has to be sorted for testing purposes
			return str(sorted(list(item['from'] | selected)))
		# Removes tags referring to things like Antiphons, Responsories, etc
		selected = (selected | item['from']) - objects
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
	pile = datamanage.getpile(root, defaultpile | flattensetlist(tags) | set(hours))
	tags = [frozenset(i) for i in tags]
	primary = list(filter(lambda i: 'primarium' in i, tags))[0]
	tags.remove(primary)

	lit = []
	for hour in hours:
		lit.extend([{'nomen-ritus', hour}, {'hora', hour}])
	return process(root, {'tags':{'ritus'},'datum':[
		{'ante-officium'}, *lit, {'post-officium'}
		]}, primary, tags, pile)

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
			defaulthour = 'matutinum laudes'
		case 6 | 7:
			defaulthour = 'prima'
		case 8 | 9 | 10:
			defaulthour = 'tertia'
		case 11 | 12 | 13:
			defaulthour = 'sexta'
		case 14 | 15:
			defaulthour = 'nona'
		case 16 | 17 | 18 | 19:
			defaulthour = 'vesperae'
		case 20 | 21 | 22 | 23:
			defaulthour = 'completorium'

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
		args.output.write(dump_data(ret) + '\n')

