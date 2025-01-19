# Copyright 2024 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import pathlib
import json
import functools
import os
import copy
import logging
import requests

data_root = pathlib.Path(__file__).parent

# Reserved tags
functiontags = {'datum', 'src', 'tags', 'from-tags', 'reference', 'choose', 'with'}

def load_data(p: str):
	data = json.loads(data_root.joinpath(p).read_text(encoding='utf-8'))

	# JSON doesn't support sets. Recursively find and replace anything that
	# looks like a list of tags with a set of tags.
	def recurse(obj, key=None):
		match obj:
			case dict():
				return {k: recurse(v, key=k) for k, v in obj.items()}
			case list():
				if all(type(x) is str for x in obj) and key != 'datum':
					return frozenset(obj)
				return [recurse(v) for v in obj]
			case _:
				return obj

	return recurse(data)

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

@functools.lru_cache(maxsize=32)
def getdiscrimina(root, query):
	return load_data(f'data/{root}/discrimina/{query}.json')

@functools.lru_cache(maxsize=64)
def getbreviariumfile(query):
	logging.debug(f'Loading {query}')
	got = load_data(query)
	if len(got) == 0:
		return []
	added = []

	for entry in got:
		if 'reference' in entry and ('antiphona-invitatorium' in entry['tags'] or (type(entry['tags']) is list and 'antiphona-invitatorium' in entry['tags'][0])):
			newentry = copy.deepcopy(entry)
			if type(newentry['tags']) is list:
				newentry['tags'] = [i | {'pars'} for i in newentry['tags']]
			else:
				newentry['tags'] = newentry['tags'] | {'pars'}
			if type(newentry['reference']) is list:
				newentry['reference'][0] = newentry['reference'][0] | {'pars'}
			else:
				newentry['reference'] = newentry['reference'] | {'pars'}
			added.append(newentry)
		elif 'reference' in entry and ('antiphona' in entry['tags'] or (type(entry['tags']) is list and 'antiphona' in entry['tags'][0])):
			newentry = copy.deepcopy(entry)
			if type(newentry['tags']) is list:
				newentry['tags'] = [i | {'intonata'} for i in newentry['tags']]
			else:
				newentry['tags'] = newentry['tags'] | {'intonata'}
			if type(newentry['reference']) is list:
				newentry['reference'][0] = newentry['reference'][0] | {'intonata'}
			else:
				newentry['reference'] = newentry['reference'] | {'intonata'}
			added.append(newentry)
			newentry = copy.deepcopy(entry)
			if type(newentry['tags']) is list:
				newentry['tags'] = [i | {'repetita'} for i in newentry['tags']]
			else:
				newentry['tags'] = newentry['tags'] | {'repetita'}
			if type(newentry['reference']) is list:
				newentry['reference'][0] = newentry['reference'][0] | {'repetita'}
			else:
				newentry['reference'] = newentry['reference'] | {'repetita'}
			added.append(newentry)

	got.extend(added)

	ret = []
	for entry in got:
		entrycopy = copy.deepcopy(entry)

		# Handle antiphons
		if ('antiphona-invitatorium' in entrycopy['tags'] or (type(entrycopy['tags']) is list and 'antiphona-invitatorium' in entrycopy['tags'][0])) and 'datum' in entrycopy:
			if '*' not in entry['datum']:
				raise RuntimeError(f'Missing intonation mark in {entry}')
			entrycopy['pars'] = entrycopy['datum'].split('*')[1].lstrip()
		elif ('antiphona' in entrycopy['tags'] or (type(entrycopy['tags']) is list and 'antiphona' in entrycopy['tags'][0])) and 'datum' in entrycopy:
			if '*' not in entry['datum']:
				raise RuntimeError(f'Missing intonation mark in {entry}')
			entrycopy['intonata'] = entrycopy['datum'].split('*')[0].rstrip()
			if entrycopy['intonata'][-1] not in ['.',',','?','!',':',';']:
				entrycopy['intonata'] += '.'
			entrycopy['repetita'] = entrycopy['datum'].split('* ')[0] + entrycopy['datum'].split('* ')[1]
		# Expands out entries where there's more than one item
		for key, val in entrycopy.items():
			if key not in functiontags:
				tags = None
				if type(entrycopy['tags']) is list:
					tags = [j | {key} for j in entrycopy['tags']]
				else:
					tags = entrycopy['tags'] | {key}
				newentry = {'tags':tags, 'datum':val}
				if 'src' in entrycopy:
					newentry['src'] = entrycopy['src']
				ret.append(newentry)
		if 'datum' in entry or 'reference' in entry:
			ret.append(entry)
	return ret

@functools.lru_cache(maxsize=1024)
def getchantfile(url):
	return requests.get(url, stream=True).text

# Has the list of files in the tagged directory to prevent multiple discoveratory traversals from having to be done
@functools.lru_cache(maxsize=16)
def getwalk(root):
	ret = []
	for roo,dirs,files in os.walk(data_root.joinpath(f'data/{root}/tagged')):
		for i in files:
			if not i.endswith('.json'):
				continue
			else:
				ret.append((i[:-5], data_root.joinpath(f'data/{root}/tagged').joinpath(roo).joinpath(i)))
	return ret

def getpile(root, pile):
	ret = []
	for name, file in getwalk(root):
		if name in pile:
			ret.extend(getbreviariumfile(file))
	return ret
