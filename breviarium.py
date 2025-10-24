#!/usr/bin/env python3

# Copyright 2025 (AGPL-3.0-or-later), Miles K. Bertrand et al.

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

defaultpile = {'formulae', 'litaniae-sanctorum','absolutiones-benedictiones', 'dies-lunae', 'nomen-temporis'}

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

def contradicts(root, category, tags):
	# In other words, are there any contradictions?
	return len(list(contradictions(root, category, tags)))

def contradictions(root, category, tags):
	category = getcategory(root, category)
	if type(category) is set or type(category) is frozenset:
		return []
	elif type(category) is list:
		for subcat in category:
			subcat = expandcat0(root, subcat)
			if sum([tag in tags for tag in subcat]) > 1:
				yield subcat
	else:
		return RuntimeError()

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
					ret = copy.copy(i)
					ret['tags'] = j
					yield ret
		elif i['tags'].issubset(query):
			yield copy.copy(i)

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

# Certain hard-coded modifications to the resultants of searches for antiphons and adds some tags
def managesearch(query, result):
	if not 'tags' in result or not 'antiphona' in result['tags'] or result['datum'] == '' or not type(result['datum']) is str:
		return result
	else:
		try:
			if 'intonata' in query:
				result['datum'] = result['datum'].split('*')[0].rstrip()
				if result['datum'][-1] not in ['.',',','?','!',':',';']:
					result['datum'] += '.'
				result['tags'] |= {'intonata'}
			elif 'repetita' in query:
				result['datum'] = result['datum'].split('* ')[0] + result['datum'].split('* ')[1]
				result['tags'] |= {'repetita'}
			elif 'pars' in query:
				result['datum'] = result['datum'].split('*')[1].lstrip()
				result['tags'] |= {'pars'}
			return result
		except IndexError:
			raise RuntimeError(f'Bad formatting for antiphon {result['datum']}')


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
		return managesearch(query, result[0])
	result = list(sorted(result, key=lambda a: len(a['tags']), reverse=True))
	if len(result[0]['tags']) != len(result[1]['tags']):
		return managesearch(query, result[0])
	elif not multipleresults:
		raise RuntimeError(f'Multiple equiprobable results for queries {query}:\n{result[0]}\n{result[1]}')
	else:
		return list([managesearch(query, i) for i in sorted(filter(lambda a : len(a['tags']) == len(result[-1]['tags']), result), multipleresultssort)])

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
		return {'tags':{'commemorationes'}, 'datum':ret}

def process(root, item, selected, alternates, pile):
	if item is None:
		return 'Absens'
	if selected is None:
		selected = frozenset()
	if alternates is None:
		alternates = []
	if pile is None:
		pile = []

	if 'commemorationes' in item:
		return handlecommemorations(root, item, selected, alternates)

	# Within the data, a set (represented in JSON as a list of strings) is a euphemism for from: tags
	if type(item) is set or type(item) is frozenset:
		item = {'from':item}

	if 'from' in item:
		if 'martyrologium' in item['from']:
			root = 'martyrologium-1846'
			pile = datamanage.getpile(root, item['from'] | {'dies-lunae'})

		selected = copy.deepcopy(selected)
		repile = False
		# Only remove positional tags when they are contradicted (for example, when the nona reading is requested by officium-capituli, remove officium-capituli)
		for cclass in contradictions(root, 'positionales', item['from'] | selected):
			selected -= cclass
			repile = True

		if repile:
			pile = datamanage.getpile(root, item['from'] | selected | defaultpile)

		result = None
		if not any('/' in i for i in item['from']):
			for i in range(len(alternates)):
				# Basically if the from is explicitly calling for some day's propers, remove the other day context to facilitate this
				if 'occurrens' in item['from'] and item['from'] & expandcat(root, 'temporale') <= alternates[i]:
					item['from'] -= {'occurrens'}
					alternates = copy.copy(alternates)
					alternates.append(selected - expandcat(root, 'positionales'))
					selected = alternates.pop(i) | (selected & expandcat(root, 'positionales'))
					pile = datamanage.getpile(root, defaultpile | item['from'] | selected)
					item['from'] -= expandcat(root, 'temporale')
					break

				# If there is an alternate with a specific object and position, it should be imposed on the from tag even if it doesn't otherwise want a different day's item
				# Sometimes there are explicit tagsets in alternates that specify certain things (as opposed to above when the data itself requests something)
				elif item['from'] | (selected & expandcat(root, 'positionales')) <= alternates[i]:
					alternates = copy.copy(alternates)
					alternates.append(selected)

					if contradicts(root, 'positionales', item['from'] | alternates[i] | selected):
						selected = alternates.pop(i)
					else:
						selected = alternates.pop(i) | (selected & expandcat(root, 'positionales'))
					pile = datamanage.getpile(root, defaultpile | item['from'] | selected)
					result = search(root, item['from'] | selected, pile)
					break

		if result is None:
			# Only remove tags referring to propers and commons and whatnot if a different set is suggested
			# This is different than the occurrens system because we're not asking about something on the specific day (for example, we want the ferial readings of the day)
			# but rather we may want the readings for the Common of the Blessed Virgin which isn't specific day-to-day
			if len(item['from'] & expandcat(root, 'temporale')) != 0:
				for cclass in contradictions(root, 'temporale', item['from'] | selected):
					selected -= cclass
				selected |= item['from'] & expandcat(root, 'temporale')
				pile = datamanage.getpile(root, defaultpile | item['from'] | selected)

			result = search(root, item['from'] | selected, pile)

		# If result is still None at this point, just tell user what was searched for
		if result is None:
			# It has to be sorted for testing purposes
			return str(sorted(list(item['from'] | selected)))
		selected |= item['from']
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

	# Often in the text there will be an N. replaced with the celebrated Saint's name.
	if type(item) is dict and 'N.' in item['datum']:
		item['datum'] = item['datum'].replace('N. et N.', 'N.').replace('N.', search(root, item['tags'] | {'n'} | selected, pile)['datum'])
	return item

def generate(root, day, hour: str):
	hours = hour.split('+')
	assert set(hours).isdisjoint({'vesperae', 'completorium'}) or set(hours).isdisjoint({'matutinum', 'laudes', 'tertia', 'sexta', 'nona'})
	tags = copy.deepcopy(prioritizer.getvespers(day) if not set(hours).isdisjoint({'vesperae', 'completorium'}) else prioritizer.getdiurnal(day))
	primary = list(filter(lambda i: 'primarium' in i, tags))[0]
	tags.remove(primary)
	pile = datamanage.getpile(root, defaultpile | primary | set(hours))

	lit = []
	for hour in hours:
		lit.append({'ritus', hour})
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

