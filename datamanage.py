# Copyright 2025 (AGPL-3.0-or-later), Miles K. Bertrand et al.

from pathlib import Path
import json
import functools
import os
import copy
import logging
import requests

import kalendar.display as display
import psalms

data_root = Path(__file__).parent

# Reserved tags
functiontags = {'datum', 'tags'}

tagselections = {'tags', 'implies', 'quaesitum'}

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

DATA_CHANT = Path('data-chant').resolve()

def retrieve_untagged_file(src: Path) -> str:
        # Quick sanitization to make sure nobody is up to shady business.
        loc = src.resolve()
        if not loc.is_relative_to(DATA_CHANT):
            raise ValueError('Invalid Path')
        else:
            with open(loc, 'r') as f:
                return f.read()

@functools.lru_cache(maxsize=1024)
def getchantfile(src):
    if 'nocturnale' in src:
        return requests.get(f'https://nocturnale.marteo.fr/static/gabc/{src[src.index('/') + 1:]}.gabc', stream=True).text
    else:
        src = src.split('/')
        return retrieve_untagged_file(DATA_CHANT.joinpath(src[0]).joinpath('untagged').joinpath('/'.join(src[1:]) + '.gabc'))

class LiturgicalBook:
    def __init__(self, src, title):
        self.src = src
        self.title = title

    def hascategory(self, category):
        return self.src.joinpath(f'categoriae/{category}.json').exists()

    @functools.lru_cache(maxsize=64)
    def getcategory(self, category):
        return load_data(f'categoriae/{category}.json', self.src)

    def hasdiscrimen(self, discrimen):
        return self.src.joinpath(f'discrimina/{discrimen}.json').exists()

    @functools.lru_cache(maxsize=32)
    def getdiscrimen(self, discrimen):
        return load_data(f'discrimina/{discrimen}.json', self.src)

    # Has the list of files in the tagged directory to prevent multiple discoveratory traversals from having to be done
    @functools.lru_cache(maxsize=16)
    def getwalk(self):
        ret = []
        for roo,dirs,files in os.walk(self.src.joinpath('tagged')):
            for i in files:
                if not i.endswith('.json'):
                    continue
                else:
                    ret.append((i[:-5], self.src.joinpath('tagged').joinpath(roo).joinpath(i)))
        return ret

    @functools.cache
    def getbreviariumfile(self, query):
        logging.debug(f'Loading {query} from {self.title}')
        got = load_data(query, self.src)
        if len(got) == 0:
            return []

        ret = []
        for entry in got:
            entrycopy = copy.deepcopy(entry)

            # Expands out entries where there's more than one item
            for key, val in entrycopy.items():
                if key not in functiontags:
                    tags = [j | {key} for j in entrycopy['tags']] if type(entrycopy['tags']) is list else entrycopy['tags'] | {key}
                    newentry = {'tags':tags, 'datum':val}
                    ret.append(newentry)
            if 'datum' in entry:
                ret.append({k: v for k, v in entry.items() if k in functiontags})
        return ret

    def get_pile(self, pilequery):
        ret = []
        for name, file in self.getwalk():
            if name in pilequery:
                ret.extend(self.getbreviariumfile(file))
        return ret

def get_book(title):
    return LiturgicalBook(data_root.joinpath('data').joinpath(title), title)

class LiturgicalContext:
    def __init__(self, *books):
        booklist = []
        for i in books:
            if type(i) is list:
                booklist.extend(i)
            else:
                booklist.append(i)
        self.books = booklist

    def getcategory(self, category):
        finds = [book.getcategory(category) for book in self.books if book.hascategory(category)]
        if all(type(cat) is frozenset for cat in finds):
            return set().union(*finds)
        else:
            ret = []
            for i in finds:
                ret.extend(i)
            return ret

    def getdiscrimen(self, discrimen):
        finds = [book.getdiscrimen(discrimen) for book in self.books if book.hasdiscrimen(discrimen)]
        ret = []
        for i in finds:
            ret.extend(i)
        return ret

    def get_pile(self, pilequery):
        ret = []
        for book in self.books:
            ret.extend(book.get_pile(pilequery))
        return ret

    def get_untagged(self, query):
        return {'tags': {query}, 'datum':psalms.get(self.books[0], query)}

class SecondaryLiturgicalContext(LiturgicalContext):
    def __init__(self, books, content_books):
        super().__init__(books)
        self.content_books = content_books

    def get_pile(self, pilequery):
        ret = []
        for book in self.content_books:
            ret.extend(book.get_pile(pilequery))
        return ret

    def get_untagged(self, query):
        if query.startswith('/psalmi'):
            return {'tags': {query}, 'datum':psalms.get(self.content_books[0], query)}
        else:
            return {'tags': {query}, 'datum': retrieve_untagged_file(self.content_books[0].src.joinpath(f'untagged/{query}.gabc'))}

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
