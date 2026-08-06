# Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import os
import copy
import logging
import functools

from composer.util import load_data
from pathlib import Path

VALID_ENDINGS = '.gabc', '.json', '.txt'

class Book:
    def __init__(self, src, title):
        self.src = src
        self.title = title

    def hascategory(self, category):
        return self.src.joinpath(f'categoriae/{category}.json').exists()

    def getcategory(self, category):
        return load_data(f'categoriae/{category}.json', self.src)

    def hasdiscrimen(self, discrimen):
        return self.src.joinpath(f'discrimina/{discrimen}.json').exists()

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

    @functools.lru_cache(maxsize=1024)
    def get_tagged_file(self, query):
        logging.debug(f'Loading {query} from {self.title}')
        got = load_data(query, self.src)
        if len(got) == 0:
            return []

        ret = []
        for entry in got:
            entrycopy = copy.deepcopy(entry)

            # Expands out entries where there's more than one item. e.g. responsories won't usually have a datum, but essentially represent multiple tagged entries.
            for key, val in entrycopy.items():
                if key != 'tags' and key != 'datum':
                    tags = [j | {key, self.title} for j in entrycopy['tags']] if type(entrycopy['tags']) is list else entrycopy['tags'] | {key, self.title}
                    newentry = {'tags':tags, 'datum':val}
                    ret.append(newentry)

            # Adds the book title to tag lists.
            entrycopy['tags'] = [j | {self.title} for j in entrycopy['tags']] if type(entrycopy['tags']) is list else entrycopy['tags'] | {self.title}
            if 'datum' in entry:
                ret.append({'tags': entrycopy['tags'], 'datum': entry['datum']})
        return ret

    def get_pile(self, pilequery):
        ret = []
        for name, file in self.getwalk():
            if name in pilequery:
                ret.extend(self.get_tagged_file(file))
        return ret

    def has_untagged(self, query):
        cand = [self.src.joinpath('untagged' + query + ending) for ending in VALID_ENDINGS if self.src.joinpath('untagged' + query + ending).exists()]
        if cand:
            return cand[0]
        else:
            return None

    @functools.lru_cache(maxsize=128)
    def retrieve_untagged_file(self, src: Path) -> str:
            # Quick sanitization to make sure nobody is up to shady business.
            loc = Path(os.path.abspath(src))
            root = Path(os.path.abspath(self.src.joinpath('untagged')))
            if not loc.is_relative_to(root):
                raise ValueError('Invalid Path')
            else:
                with open(loc, 'r') as f:
                    return f.read()
