# Copyright 2025 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import pathlib
import json
import functools
import os
import copy
import logging
import requests
import kalendar.display as display

data_root = pathlib.Path(__file__).parent

# Reserved tags
functiontags = {'datum', 'src', 'tags', 'from-tags', 'choose', 'with'}

tagselections = {'tags', 'from-tags', 'implies', 'choose', 'with'}

def load_data(p: str):
	data = json.loads(data_root.joinpath(p).read_text(encoding='utf-8'))

	# JSON doesn't support sets. Recursively find and replace anything that
	# looks like a list of tags with a set of tags.
	def recurse(obj, key=None):
		match obj:
			case dict():
				return {k: recurse(v, key=k) for k, v in obj.items()}
			case list():
				if all(type(x) is str for x in obj) and (key is None or key in tagselections):
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

	ret = []
	for entry in got:
		entrycopy = copy.deepcopy(entry)

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
		if 'datum' in entry:
			ret.append({k: v for k, v in entry.items() if k in functiontags})
	return ret

@functools.lru_cache(maxsize=1024)
def getchantfile(src):
	url = ''
	if 'gregobase' in src and not src.endswith('&format=gabc'):
		url = f'https://gregobase.selapa.net/download.php?id={src[src.index('/') + 1:]}&format=gabc&elem=1'
	elif 'nocturnale' in src:
		url = f'https://nocturnale.marteo.fr/static/gabc/{src[src.index('/') + 1:]}.gabc'
	elif 'fcc' in src:
		url = f'http://localhost:40081/{src[src.index('/') + 1:]}.gabc'
	else:
		raise Exception('Unsupported chant repository')
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

root = 'breviarium-1888'
def getname(tagset, pile):
	import breviarium
	resp = breviarium.process(root, {'nomen'}, tagset, [], pile)
	name = resp['datum'] if 'datum' in resp else '+'.join(tagset)
	if type(name) is list:
		name = (name[0] + name[1]['datum']) if 'datum' in name[1] else '+'.join(tagset)
	return name

@functools.lru_cache(maxsize=1)
def getdisplaykalendar():
	ret = dict(sorted(display.kalendar().items()))
	ret = {str(k): [list(ent) for ent in v] for k, v in ret.items()}
	kalendar = load_data('kalendar/data/kalendarium.json')
	kalendar.extend(load_data('kalendar/data/in-tempore-nativitatis.json'))

	kalendar = display.kalendar2()
	for entry in kalendar:
		if type(entry['tags']) is frozenset:
			entry['tags'] = [entry['tags']]
		entry['names'] = [getname(tagset, getpile(root, tagset | {'formulae'})) for tagset in entry['tags']]
		if any(i in entry['occurrence'] for i in ['feria-ii', 'feria-iii', 'feria-iv', 'feria-v', 'feria-vi', 'sabbatum']):
			entry['occurrence'] |= {'feria'}
		entry['occurrence-name'] = getname(entry['occurrence'], getpile(root, entry['occurrence'] | {'formulae'}))
	return dump_data({'skeleton': ret, 'kalendar': kalendar})
