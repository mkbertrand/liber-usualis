# Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import functools
import json

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

# Certain hard-coded modifications to the resultants of searches for antiphons and adds some tags
def transform_search(query, result):
    if 'tags' in result:
        result['quaesitum'] = query
    if not 'tags' in result or not 'antiphona' in result['tags'] or result['datum'] == '' or not type(result['datum']) is str:
        return result
    else:
        try:
            if not '*' in result['datum']:
                return result
            if 'n' in query:
                return result
            elif 'intonata' in query:
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
            return result
