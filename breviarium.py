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

from kalendar import kalendar
import psalms

data_root = pathlib.Path(__file__).parent
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
					return list(obj)
				return [recurse(v) for v in obj]
			case _:
				return obj

	return json.dumps(recurse(j))

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

def flattensetlist(sets):
	ret = set()
	for i in sets:
		ret |= i
	return ret

def anysearch(query, pile):
	for i in pile:
		if type(i['tags']) is list:
			for j in i['tags']:
				if j.issubset(query):
					ret = copy.deepcopy(i)
					ret['tags'] = j
					yield copy.deepcopy(ret)
		elif i['tags'].issubset(query):
			yield copy.deepcopy(i)

# Numerical rank of query tagset according to a table of tagsets. Outputs a binary number with 1 in positions where the tagset at that table position was a subset of the query.
def discriminate(root, table: str, tags: set):
	table = datamanage.getdiscrimina(root, table)
	val = 0
	for i in range(0, len(table)):
		include = set(filter(lambda a: a[0] != '!', table[i]))
		exclude = {a[1:] for a in table[i] - include}
		# Adds 1 or 0 lower on the number as the position in the table increases using binary operators. The higher the position in the table (IE the farther down in the table), the lower precedence something is.
		val |= include.issubset(tags) and exclude.isdisjoint(tags) << (len(table) - i - 1)
	return val

def search(root, query, pile, multipleresults = False, multipleresultssort = None, priortags = None, rootappendix = ''):

	for i in query:
		if '/' in i:
			try:
				return {'tags': [i], 'datum':psalms.get(root + rootappendix, i)}
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
	elif priortags is not None:
		logging.debug(f'Search differentiation used priortag to rank {result}' )
		strippedresult = [a['tags'] & priortags for a in result]
		if len(strippedresult[-1]) != len(strippedresult[-2]):
			return result[-1]

	if not multipleresults:
		raise RuntimeError(f'Multiple equiprobable results for queries {query}:\n{result[-1]}\n{result[-2]}')
	else:
		return list(sorted(filter(lambda a : len(a['tags']) == len(result[-1]['tags']), result), multipleresultssort))

def process(root, item, selected, alternates, pile):
	try:
		if item is None:
			return 'Absens'
		if selected is None:
			selected = set()
		if alternates is None:
			alternates = []
		if pile is None:
			pile = []

		# Special commemoration handling. Commemorations are hard because they rely on eachother and differ in number by day.
		if 'commemorationes' in item:
			ret = []
			commemorations = sorted(list(filter(lambda a : 'commemoratio' in a, alternates)), key=lambda a:discriminate(root, 'rank', a), reverse=True)
			for i in commemorations:
				probablepile = datamanage.getbreviariumfiles(root, defaultpile | item | i)
				ret.append(process(root, {'formula','commemoratio'}, i | (item - {'commemorationes'}), alternates, probablepile))
			if len(commemorations) != 0:
				probablepile = datamanage.getbreviariumfiles(root, defaultpile | commemorations[-1])
				ret.append(process(root, {'collecta','terminatio','commemoratio'}, commemorations[-1] | (item - {'commemorationes'}), alternates, probablepile))
			return ret

		# None can sometimes be the result of a search and is expected, but indicates an absent item
		if type(item) is set or type(item) is frozenset:
			result = search(root, item | selected, pile, priortags = item)
			if result is None:
				return str(list(item | selected))
			else:
				item = result

		if 'choose' in item:
			if any([item['choose'].issubset(i) for i in alternates]):
				for i in range(0, len(alternates)):
					if item['choose'].issubset(alternates[i]):
						alternates.append(selected)
						selected = alternates.pop(i)
						break
		if 'reference' in item:
			alternates.append(selected)
			# Just in case an item needs to change depending on whether it is a reference
			selected = item['reference'] | {'referens'}
			pile = datamanage.getbreviariumfiles(root, defaultpile | item['reference'])

		if 'with' in item:
			selected |= set(item['with'])
		if 'from-tags' in item:
			response = process(root, search(root, item['from-tags'] | selected, pile, priortags = item['from-tags']), selected, alternates, pile)
			if 'tags' in item:
				return {'tags': item['tags'], 'datum': response}
			else:
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
	except:
		raise Exception(f'Error occured while generating for {item} with {selected} and {alternates}')


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
		'-t',
		'--tags',
		type=str,
		default=None,
		help='Tag search for manually selected primarium',
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
	defpile = datamanage.getbreviariumfiles(args.root, defaultpile)
	day = datetime.strptime(args.date, '%Y-%m-%d').date()
	argtags = set() if args.tags is None else set(args.tags.split(' '))
	ret = {'tags':{'reditus'},'datum':[process(args.root, {'ante-officium'}, None, None, defpile)]}

	for i in args.hour.split(' '):
		tags = copy.deepcopy(prioritizer.getvespers(day) if i == 'vesperae' or i == 'completorium' else datamanage.getdate(day))
		for j in tags:
			for k in implicationtable:
				if k['tags'].issubset(j):
					j |= k['implies']
		pile = datamanage.getbreviariumfiles(args.root, defaultpile | flattensetlist(tags) | {i} | argtags)
		primary = None
		if len(argtags) == 0:
			primary = list(filter(lambda i: 'primarium' in i, tags))[0]
			for j in tags:
				if 'primarium' in j:
					tags.remove(j)
					break
		else:
			primary = argtags
		ret['datum'].append(process(args.root, {i, 'hora'}, primary, tags, pile))
	ret['datum'].append(process(args.root, {'post-officium'}, None, None, defpile))

	if args.output == sys.stdout:
		prettyprint(ret)
	else:
		# Write JSON output
		args.output.write(dump_data(ret) + '\n')

