import pathlib
import json
import copy
from datetime import date, datetime, timedelta
import functools
import prioritizer
import datamanage
import warnings

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
    for i in pile:
        if i['tags'].issubset(query):
            yield i

def exactsearch(query, pile):
    def exactsearchyield():
        for i in pile:
            if i['tags'] == query:
                yield i
    result = list(exactsearchyield())
    if len(result) == 0:
        warnings.warn(f'0 tags found for query {query}')
        return None
    elif not len(result) == 1:
        raise RuntimeError(f'{len(result)} tags found for query {query}:\n{result}')
    else:
        return result[0]

def singlesearch(query, pile):
    result = list(anysearch(query, pile))
    if len(result) == 0:
        warnings.warn(f'0 tags found for query {query}')
        return None
    elif not len(result) == 1:
        raise RuntimeError(f'{len(result)} tags found for query {query}:\n{result}')
    else:
        return result[0]

def search(query, pile):
    result = list(sorted(list(anysearch(query, pile)), key=lambda a: len(a['tags'])))
    if len(result) == 0:
        warnings.warn(f'0 tags found for query {query}')
        return None
    elif len(result) == 1:
        return result[0]
    elif len(result[-1]['tags']) == len(result[-2]['tags']):
        raise RuntimeError(f'Multiple equiprobable results for query {query}:\n{result[-1]}\n{result[-2]}')
    else:
        return result[-1]

# None handling is included so that hour searches with tagsets that will produce only partial hours (EG lectionary searches, searches for Vigils, etc) can be generated and used
def process(item, withtags, pile):
    # None can sometimes be the result of a search and is expected, but indicates an absent item
    if item == None:
        return 'Absens'
    elif type(item) == set:
        item = search(item.union(withtags), pile)
    if 'from-tags' in item:
        response = process(search(item['from-tags'].union(withtags), pile), item['with-tags'].union(withtags) if 'with-tags' in item else withtags, pile)
        return {'tags':item['tags'],'datum':response} if 'tags' in item else response
    elif 'forwards-to' in item:
        return process(search(item['forwards-to'].union(withtags), pile), {}, pile)
    elif type(item['datum']) == list:
        ret = []
        for i in item['datum']:
            if type(i) == str:
                ret.append(i)
            else:
                iprocessed = process(i, withtags, pile)
                if iprocessed == None:
                    ret.append('Absens')
                elif type(iprocessed) == list:
                    ret.extend(iprocessed)
                else:
                    ret.append(iprocessed)
        item['datum'] = ret if len(ret) != 1 else ret[0]
        return item
    else:
        return item

def replacetagrecurse(datum, target, item):
    if type(datum) == str:
        return datum
    elif target.issubset(datum['tags']):
        datum['datum'] = item
    elif type(datum['datum']) == list:
        for i in range(0, len(datum['datum'])):
            ret = replacetagrecurse(datum['datum'][i], target, item)
            if not datum['datum'][i] == ret:
                datum['datum'][i] = ret
                return datum
    return datum

defaultpile = {'horae','psalterium','formulae','psalmi','cantica'}

def getbytags(daytags, query):
    for i in daytags:
        if query in i:
            return i

def hour(hour: str, day):

    daytags = prioritizer.getvespers(day) if hour == 'vesperae' or hour == 'completorium' else datamanage.getdate(day)
    flatday = set()
    for i in daytags:
        flatday |= i
    
    pile = datamanage.getbreviarumfiles(defaultpile | flatday)
    
    primary = getbytags(daytags, 'primarium')
    withtagprimary = primary | getbytags(daytags, 'antiphona-bmv')
    withtagprimary -= {'i-vesperae','antiphona-bmv'}
    primarydatum = process({hour, 'hora'} | primary, withtagprimary, pile)
    return primarydatum

print(dump_data(hour('vesperae', date.today() - timedelta(days=1))))
