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
defaultpile = {'horae','psalterium','formulae','psalmi','cantica'}

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
                    print(pieces[0])
                    for i in pieces[1:]:
                        print(' ' + i)
    recurse(j)

def anysearch(query, pile):
    for i in pile:
        if i['tags'].issubset(query):
            yield i

def search(query, pile, multipleresults = False, multipleresultssort = None):
    result = list(sorted(list(anysearch(query, pile)), key=lambda a: len(a['tags'])))
    if len(result) == 0:
        warnings.warn(f'0 tags found for query {query}')
        return None
    elif len(result) == 1:
        return result[0]
    elif len(result[-1]['tags']) == len(result[-2]['tags']):
        if not multipleresults:
            raise RuntimeError(f'Multiple equiprobable results for query {query}:\n{result[-1]}\n{result[-2]}')
        else:
            return list(sorted(filter(lambda a : len(a['tags']) == len(result[-1]['tags']), result),multipleresultsort))
    else:
        return result[-1]

# None handling is included so that hour searches with tagsets that will produce only partial hours (EG lectionary searches, searches for Vigils, etc) can be generated and used
def process(item, withtags, pile):
    # None can sometimes be the result of a search and is expected, but indicates an absent item
    if item == None:
        return 'Absens'
    elif type(item) == set:
        item = search(item | withtags, pile)
    if 'from-tags' in item:
        response = process(search(item['from-tags'] | withtags, pile), item['with-tags'] | withtags if 'with-tags' in item else withtags, pile)
        return {'tags':item['tags'],'datum':response} if 'tags' in item else response
    elif 'forwards-to' in item:
        return process(search(item['forwards-to'], datamanage.getbreviarumfiles(defaultpile | item['forwards-to'])), withtags, pile)
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

def getbytags(daytags, query):
    for i in daytags:
        if query in i:
            return i

def hour(hour: str, day):
    assert not type(day) == datetime
    daytags = prioritizer.getvespers(day) if hour == 'vesperae' or hour == 'completorium' else datamanage.getdate(day)
    flatday = set()
    for i in daytags:
        flatday |= i
    
    pile = datamanage.getbreviarumfiles(defaultpile | flatday)
    
    primary = getbytags(daytags, 'primarium')
    withtagprimary = primary | (getbytags(daytags, 'antiphona-bmv') - {'i-vesperae','antiphona-bmv', 'temporale'}) | {hour}
    primarydatum = process({hour, 'hora'} | primary, withtagprimary, pile)
    return primarydatum

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Divine Office Hours",
    )

    parser.add_argument(
        "-v",
        "--verbosity",
        metavar="LEVEL",
        type=lambda s: s.upper(),
        choices=logging.getLevelNamesMapping().keys(),
        default=logging.getLevelName(logging.getLogger().getEffectiveLevel()),
        const="debug",
        nargs="?",
        help="Verbosity",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=argparse.FileType("w"),
        default="-",
        help="Output filename",
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
            defaulthour = 'matutinum'
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
    ret = hour(args.hour, datetime.strptime(args.date, '%Y-%m-%d').date())

    if args.output == sys.stdout:
        print(prettyprint(ret))
    else:
        # Write JSON output
        args.output.write(dump_data(ret) + "\n")
