#!/usr/bin/env python3

import pathlib
import json
import copy
from datetime import date, datetime, timedelta
import functools
import prioritizer
import datamanage
import warnings
import logging
import sys

from kalendar import kalendar

data_root = pathlib.Path(__file__).parent
defaultpile = {'formulae','psalmi','cantica'}

responsetags = {'primarium','tempus','commemoratio','antiphona-bmv','psalmi'}

def load_data(p: str):
    data = json.loads(data_root.joinpath(p).read_text(encoding="utf-8"))

    # JSON doesn't support sets. Recursively find and replace anything that
    # looks like a list of tags with a set of tags.
    def recurse(obj, key=None):
        match obj:
            case dict():
                return {k: recurse(v, key=k) for k, v in obj.items()}
            case list():
                if all(type(x) is str for x in obj) and key != 'datum':
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

implicationtable = load_data('kalendar/data/tag-implications.json')
tagsorttable = load_data('kalendar/data/tag-sort.json')

def prettyprint(j):
    def recurse(obj):
        match obj:
            case dict():
                return {k: recurse(v) for k, v in obj.items()}
            case list():
                return [recurse(v) for v in obj]
            case set() | frozenset():
                pass
            case str():
                if (obj.startswith('https')):
                    print(obj)
                else:
                    pieces = obj.split('/')
                    if len(pieces[0]) != 0:
                        print(pieces[0])
                    for i in pieces[1:]:
                        print(' ' + i)
    recurse(j)

def flattensetlist(sets):
    ret = set()
    for i in sets:
        ret |= i
    return ret

def anysearch(query, pile):
    for i in pile:
        if type(i['tags']) == list:
            for j in i['tags']:
                if j.issubset(query):
                    ret = copy.deepcopy(i)
                    ret['tags'] = j
                    yield copy.deepcopy(ret)
        elif i['tags'].issubset(query):
            yield copy.deepcopy(i)

def anysearchmultiple(queries, pile):
    ret = []
    for i in queries:
        ret.extend(list(anysearch(i, pile)))
    return ret

def itemvalue(tags, table):
    val = 0
    for i in range(0, len(tagsorttable[table])):
        include = set(filter(lambda a: a[0] != '!', tagsorttable[table][i]))
        exclude = set([i[1:] for i in filter(lambda a: a[0] == '!', tagsorttable[table][i])])
        val |= include.issubset(tags) and exclude.isdisjoint(tags) << (len(tagsorttable[table]) - i - 1)
    return val

def search(queries, pile, multipleresults = False, multipleresultssort = None, priortags = None):
    result = list(sorted(list(anysearchmultiple(queries, pile)), key=lambda a: itemvalue(a['tags'], 'precedence'), reverse=True))
    if len(result) == 0:
        warnings.warn(f'0 tags found for queries {list(queries)}')
        return None
    bestvalue = itemvalue(result[0]['tags'], 'precedence')
    result = list(filter(lambda a: itemvalue(a['tags'], 'precedence') == bestvalue, result))
    if len(result) == 1:
        return result[0]
    result = list(sorted(result, key=lambda a: len(a['tags']), reverse=True))
    if len(result[0]['tags']) != len(result[1]['tags']):
        return result[0]
    elif priortags is not None:
        logging.debug(f'Search differentiation used priortag to rank {result}' )
        strippedresult = [a['tags'] & priortags for a in result]
        if len(strippedresult[-1]) != len(strippedresult[-2]):
            return result[-1]
    if not multipleresults:
        raise RuntimeError(f'Multiple equiprobable results for queries {queries}:\n{result[-1]}\n{result[-2]}')
    else:
        return list(sorted(filter(lambda a : len(a['tags']) == len(result[-1]['tags']), result), multipleresultssort))

def pickcascades(search, cascades):
    if cascades is None:
        return search
    else:
        ret = copy.deepcopy(search)
        for cascade in cascades:
            if not responsetags.isdisjoint(search & cascade):
                ret |= cascade
        if len(ret) == len(search):
            for cascade in cascades:
                if 'primarium' in cascade:
                    ret |= cascade
        return ret

def process(item, cascades, pile):

    if item is None:
        return 'Absens'

    # Special commemoration handling. Commemorations are hard because they rely on eachother and differ in number by day.
    if 'commemorationes' in item:
        ret = []
        commemorations = sorted(list(filter(lambda a : 'commemoratio' in a, cascades)), key=lambda a:itemvalue(a, 'rank'), reverse=True)
        for i in commemorations:
            probablepile = datamanage.getbreviariumfiles(defaultpile | i)
            ret.append(process({'formula','commemoratio'}, [i], probablepile))
        if len(commemorations) != 0:
            probablepile = datamanage.getbreviariumfiles(defaultpile | commemorations[-1])
            ret.append(process({'collecta','terminatio','commemoratio'}, [commemorations[-1]], probablepile))
        return ret
     # None can sometimes be the result of a search and is expected, but indicates an absent item
    if type(item) is set:
        item = search([pickcascades(item, cascades)], pile, priortags = item)
        if item is None:
            return 'Absens'

    # Next cascade (not to be used for the current search, but only for deeper searches
    nextcascades = [i | item['cascade'] for i in cascades] if 'cascade' in item and cascades else cascades

    if 'from-tags' in item:
        response = process(search([pickcascades(item['from-tags'], cascades)], pile, priortags = item['from-tags']), nextcascades, pile)
        if 'tags' in item:
            return {'tags':item['tags'], 'datum':response}
        else:
            return response

    elif 'forwards-to' in item:
        # Since items in the Breviary may reference seemingly unrelated feasts, process searches a pile made from relevant files
        probableforwardpiles = datamanage.getbreviariumfiles(defaultpile | flattensetlist([pickcascades(item['forwards-to'], cascades)]))
        return process(search([pickcascades(item['forwards-to'], cascades)], probableforwardpiles, priortags = item['forwards-to']), nextcascades, pile)

    elif type(item['datum']) is list:
        ret = []
        for i in item['datum']:
            if type(i) is str:
                ret.append(i)
            else:
                iprocessed = process(i, cascades, pile)
                if iprocessed is None:
                    ret.append('Absens')
                elif type(iprocessed) is list:
                    ret.extend(iprocessed)
                else:
                    ret.append(iprocessed)
        item['datum'] = ret if len(ret) != 1 else ret[0]

    return item

def getbytags(daytags, query):
    for i in daytags:
        if query in i:
            return i

def hour(hour: str, day, forcedprimary=None):
    assert type(day) is not datetime
    daytags = copy.deepcopy(prioritizer.getvespers(day) if hour == 'vesperae' or hour == 'completorium' else datamanage.getdate(day))
    for i in daytags:
        for j in implicationtable:
            if j['tags'].issubset(i):
                i |= j['implies']

    pile = datamanage.getbreviariumfiles(defaultpile | flattensetlist(daytags) | {hour})

    if forcedprimary:
        forcedprimary = set(forcedprimary.split(' '))
        for i in daytags:
            if 'primarium' in i:
                i.remove('primarium')
                i.add('commemoratio')
        for i in daytags:
            if forcedprimary.issubset(i):
                i.add('primarium') 
                i -= {'commemoratio'}
    primary = getbytags(daytags, 'primarium')
    if primary is None and forcedprimary:
        raise RuntimeError('Provided tag(s) not found') 
    for i in daytags:
        i.add(hour)
    primarydatum = process({hour, 'hora'} | primary, daytags, pile)
    return primarydatum

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Divine Office Hours',
    )

    parser.add_argument(
        '-v',
        '--verbosity',
        metavar='LEVEL',
        type=lambda s: s.upper(),
        choices=logging.getLevelNamesMapping().keys(),
        default=logging.getLevelName(logging.getLogger().getEffectiveLevel()),
        const='debug',
        nargs='?',
        help='Verbosity',
    )

    parser.add_argument(
        '-o',
        '--output',
        type=argparse.FileType('w'),
        default='-',
        help='Output filename',
    )

    parser.add_argument(
        '-t',
        '--tags',
        type=str,
        default=None,
        help='Tag search for manually selected primarium',
    )

    parser.add_argument(
        '-d',
        '--date',
        type=str,
        default=str(date.today()),
        help='Date to generate',
    )

    defaulthour = None

    match datetime.now().hour:
        case 0 | 2 | 3 | 4 | 5:
            defaulthour = 'matutinum laudes'
        case 6 | 7:
            defaulthour = 'prima'
        case 8 | 9 | 10:
            defaulthour = 'tertia'
        case 11 | 12 | 13:
            defaulthour = 'sexta'
        case 14 | 15:
            defaulthour = 'nona'
        case 16 | 17 | 18 | 19:
            defaulthour = 'vesperae'
        case 20 | 21 | 22 | 23:
            defaulthour = 'completorium'

    parser.add_argument(
        '-hr',
        '--hour',
        type=str,
        default=str(defaulthour),
        help='Liturgical hour to generate',
    )

    args = parser.parse_args()

    if args.verbosity:
        logging.getLogger().setLevel(args.verbosity)

    # Generate kalendar
    defpile = datamanage.getbreviariumfiles(defaultpile)
    ret = {'tags':{'reditus'},'datum':[process({'ante-officium'}, None, defpile)]}
    for i in args.hour.split(' '):
        ret['datum'].append(hour(i, datetime.strptime(args.date, '%Y-%m-%d').date(), forcedprimary=args.tags))
    ret['datum'].append(process({'post-officium'}, None, defpile))

    if args.output == sys.stdout:
        prettyprint(ret)
    else:
        # Write JSON output
        args.output.write(dump_data(ret) + '\n')
