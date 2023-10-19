import pathlib
import json
import copy
from datetime import date, datetime, timedelta
import functools
import prioritizer
import datamanage

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
                    return frozenset(obj)
                return [recurse(v) for v in obj]
            case _:
                return obj

    return recurse(data)

def dump_data(j):

    # JSON doesn't support sets. Recursively find and replace anything that
    # looks like a list of tags with a set of tags.
    def recurse(obj, key=None):
        match obj:
            case dict():
                return {k: recurse(v, key=k) for k, v in obj.items()}
            case list():
                return [recurse(v) for v in obj]
            case set() | frozenset():
                if all(type(x) == str for x in obj):
                    return list(obj)
                return [recurse(v) for v in obj]
            case _:
                return obj

    return json.dumps(recurse(j))

def anysearch(query, pile):
    print(query)
    for i in pile:
        if i['tags'].issubset(query):
            yield i

def exactsearch(query, pile):
    def exactsearchyield():
        for i in pile:
            if i['tags'] == query:
                yield i
    result = list(exactsearchyield())
    if not len(result) == 1:
        raise RuntimeError(f'{len(result)} tags found for query {query}:\n{result}')
    else:
        return result[0]

def singlesearch(query, pile):
    result = list(anysearch(query, pile))
    if not len(result) == 1:
        raise RuntimeError(f'{len(result)} tags found for query {query}:\n{result}')
    else:
        return result[0]

def search(query, pile):
    result = list(anysearch(query, pile))
    if len(result) == 1:
        return result[0]
    elif len(result) == 0:
        raise RuntimeError(f'{len(result)} tags found for query {query}:\n{result}')
    else:
        return sorted(result, key=lambda a: len(a['tags']))[-1]

def process(item, withtags, pile):
    if type(item) == set:
        item = search(item.union(withtags), pile)
    if 'from-tags' in item:
        return process(search(item['from-tags'].union(withtags), pile), item['with-tags'] if 'with-tags' in item else {}, pile)
    elif 'forwards-to' in item:
        return process(search(item['forwards-to'].union(withtags), pile), {}, pile)
    elif type(item['datum']) == list:
        ret = []
        for i in item['datum']:
            if type(i) == str:
                ret.append(i)
            else:
                iprocessed = process(i, withtags, pile)
                if type(iprocessed) == list:
                    ret.extend(iprocessed)
                else:
                    ret.append(iprocessed)
        item['datum'] = ret if len(ret) != 1 else ret[0]
        return item
    else:
        return item
        

def template(template, passed):
    return 

defaultpile = {'horae','psalterium','formulae','psalmi','cantica'}

def hour(hour: str, day):

    daytags = prioritizer.getvespers(day) if hour == 'vesperae' or hour == 'completorium' else datamanage.getdate(day)
    flatday = set()
    for i in daytags:
        flatday |= i
    
    pile = datamanage.getbreviarumfiles(defaultpile | flatday)
    
    return process({hour, 'hora'},{}, pile)

print(dump_data(hour('completorium',date.today())))
