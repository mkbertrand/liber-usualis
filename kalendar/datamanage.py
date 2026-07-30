# Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import functools
import copy
import json
import re
from typing import NamedTuple
from bookshelf import Bookshelf

from pathlib import Path

BOOK_ROOT = Path(__file__).parent.parent.joinpath('data').resolve()

def load_data(p: str, root):
    data = json.loads(root.joinpath('kalendarium').joinpath(p).read_text(encoding='utf-8'))

    # JSON doesn't support sets. Recursively find and replace anything that
    # looks like a list of tags with a set of tags.
    def recurse(obj):
        match obj:
            case dict():
                return {datetime.strptime(k, '%Y-%m-%d').date() if re.search(r'^\d{4}-\d{2}-\d{2}$',k) is not None else k: recurse(v) for k, v in obj.items()}
            case list():
                if all(type(x) is str for x in obj):
                    return frozenset(obj)
                return [recurse(v) for v in obj]
            case _:
                return obj

    return recurse(data)

class Restriction(NamedTuple):
    include: set
    exclude: set

def flatten(table):
    rules = []
    rulenumber = 0
    for i in copy.deepcopy(table):
        if not 'exclude' in i:
            i['exclude'] = None
        if not 'recheck' in i:
            i['recheck'] = True
        if not 'continue' in i:
            i['continue'] = True
        i['restrict'] = [Restriction(i['include'], i['exclude'])]
        if not 'response' in i:
            i['response'] = 'mutate'
        if type(i['response']) is str:
            i['target'] = 0
            i['number'] = rulenumber
            rules.append(i)
            rulenumber += 1
        else:
            for j in i['response']:
                if not 'exclude' in j:
                    j['exclude'] = None
                j['restrict'] = [i['restrict'][0], Restriction(j['include'], j['exclude'])]
                j['number'] = rulenumber
                if not 'recheck' in j:
                    j['recheck'] = i['recheck']
                if not 'continue' in j:
                    j['continue'] = i['continue']
                rules.append(j)
                rulenumber += 1
    return rules

@functools.lru_cache(maxsize=16)
def get_year(book, year):
    import kalendar.kalendar as kalendar
    return kalendar.kalendar(book, year)

def get_date(book, day):
    year = get_year(book, day.year)
    return year[day]

class KalendarCorpus(Bookshelf):
    def __init__(self, srcs: list):
        self.srcs = srcs

    def book_srcs(self):
        return self.srcs

def get_bookshelf(name):
    return KalendarCorpus([BOOK_ROOT.joinpath(name)])
