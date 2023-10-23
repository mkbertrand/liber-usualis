import pathlib
import json
import functools
import os
import copy
import logging

from kalendar import kalendar

data_root = pathlib.Path(__file__).parent

def load_data(p: str):
    data = json.loads(data_root.joinpath(p).read_text(encoding="utf-8"))

    # JSON doesn't support sets. Recursively find and replace anything that
    # looks like a list of tags with a set of tags.
    def recurse(obj, key=None):
        match obj:
            case dict():
                return {k: recurse(v, key=k) for k, v in obj.items()}
            case list():
                if all(type(x) == str for x in obj) and not key == 'datum':
                    return set(obj)
                return [recurse(v) for v in obj]
            case _:
                return obj

    return recurse(data)

@functools.lru_cache(maxsize=16)
def getyear(year):
    return kalendar.kalendar(year)

def getdate(day):
    year = getyear(day.year)
    return year[day]

@functools.lru_cache(maxsize=32)
def getbreviarumfile(query):
    logging.debug(f'Loading {query}')
    return load_data(query)

#No error management is needed for missing queries since queries aren't checked for actively, but rather all files in the system are checked to see if they match any of the queries
def getbreviarumfiles(queries):
    ret = []
    for (root,dirs,files) in os.walk(data_root.joinpath('breviarum')):
        for i in files:
            if i[:-5] in queries:
                got = getbreviarumfile(data_root.joinpath('breviarum').joinpath(root).joinpath(i))
                added = []
                for i in got:
                    if 'antiphona' in i['tags']:
                        icopy = copy.deepcopy(i)
                        icopy['tags'].add('intonata')
                        icopy['datum'] = icopy['datum'].split('*')[0].rstrip()
                        if not icopy['datum'][-1] in ['.',',','?','!',':',';']:
                            icopy['datum'] += '.'
                        added.append(icopy)
                ret.extend(got)
                ret.extend(added)
                
    return ret
