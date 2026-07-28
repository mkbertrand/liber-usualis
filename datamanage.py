# Copyright 2025-2026 (AGPL-4.0-or-later), Miles K. Bertrand et al.

from pathlib import Path
import json
import functools
import os
import copy
import logging

import kalendar.display as display

from composer import Book

DATA_ROOT = Path(__file__).parent.joinpath('data').resolve()

# Reserved tags
functiontags = {'datum', 'tags'}

tagselections = {'tags', 'implies', 'quaesitum'}

@functools.lru_cache(maxsize=32)
def load_data(p: str, src):
    data = json.loads(src.joinpath(p).read_text(encoding='utf-8'))

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
                    return list(obj)
                return [recurse(v) for v in obj]
            case _:
                return obj

    return json.dumps(recurse(j))

def get_generated_book(title):
    return Book(DATA_ROOT.joinpath('generated').joinpath(title), title)

def get_book(title):
    return Book(DATA_ROOT.joinpath(title), title)

def get_name(context, tagset):
    import breviarium
    resp = breviarium.process(context, {'nomen'}, tagset, [])
    name = resp['datum'] if 'datum' in resp else '+'.join(tagset)
    if type(name) is list:
        name = (name[0] + name[1]['datum']) if 'datum' in name[1] else '+'.join(tagset)
    return name

@functools.lru_cache(maxsize=1)
def getdisplaykalendar(context):
    ret = dict(sorted(display.kalendar(context).items()))
    ret = {str(k): [list(ent) for ent in v] for k, v in ret.items()}

    kalendar = display.kalendar2(context)
    for entry in kalendar:
        if type(entry['tags']) is frozenset:
            entry['tags'] = [entry['tags']]
        entry['names'] = [get_name(context, tagset) for tagset in entry['tags']]
        if any(i in entry['occurrence'] for i in ['feria-ii', 'feria-iii', 'feria-iv', 'feria-v', 'feria-vi', 'sabbatum']):
            entry['occurrence'] |= {'feria'}
        entry['occurrence-name'] = get_name(context, entry['occurrence'])
    return dump_data({'skeleton': ret, 'kalendar': kalendar})
