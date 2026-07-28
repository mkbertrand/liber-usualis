# Copyright 2025-2026 (AGPL-4.0-or-later), Miles K. Bertrand et al.

from pathlib import Path
import json
import functools

import kalendar.display as display

from composer import Book
from composer import util

DATA_ROOT = Path(__file__).parent.joinpath('data').resolve()

def get_generated_book(title):
    return Book(DATA_ROOT.joinpath('generated').joinpath(title), title)

def get_book(title):
    return Book(DATA_ROOT.joinpath(title), title)

@functools.lru_cache(maxsize=1)
def getdisplaykalendar(context):
    ret = dict(sorted(display.kalendar(context).items()))
    ret = {str(k): [list(ent) for ent in v] for k, v in ret.items()}

    kalendar = display.kalendar2(context)
    for entry in kalendar:
        if type(entry['tags']) is frozenset:
            entry['tags'] = [entry['tags']]
        entry['names'] = [context.get_name(tagset) for tagset in entry['tags']]
        if any(i in entry['occurrence'] for i in ['feria-ii', 'feria-iii', 'feria-iv', 'feria-v', 'feria-vi', 'sabbatum']):
            entry['occurrence'] |= {'feria'}
        entry['occurrence-name'] = context.get_name(entry['occurrence'])
    return util.dump_data({'skeleton': ret, 'kalendar': kalendar})
