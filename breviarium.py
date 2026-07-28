#!/usr/bin/env python3

# Copyright 2025-2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import copy
import kalendar.daily_tagger
import warnings

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
                if obj.startswith('https'):
                    print(obj)
                else:
                    pieces = obj.split('/')
                    if len(pieces[0]) != 0:
                        print(pieces[0])
                    for i in pieces[1:]:
                        print(' ' + i)
    recurse(j)

def anysearch(query, pile):
    for i in pile:
        if type(i['tags']) is list:
            for j in i['tags']:
                if j.issubset(query):
                    ret = copy.copy(i)
                    ret['tags'] = j
                    yield ret
        elif i['tags'].issubset(query):
            yield copy.copy(i)

# Numerical rank of query tagset according to a table of tagsets. Outputs a binary number with 1 in positions where the tagset at that table position was a subset of the query.
def discriminate(context, table: str, tags: set):
    table = context.getdiscrimen(table)
    val = 0
    for i in range(0, len(table)):
        if len(table[i]) == 1 and list(table[i])[0].startswith('/'):
            val |= (not tags.isdisjoint(context.expand_cat(list(table[i])[0]))) << (len(table) - i - 1)
        else:
            include = set(filter(lambda a: a[0] != '!', table[i]))
            exclude = {a[1:] for a in table[i] - include}
            # Adds 1 or 0 lower on the number as the position in the table increases using binary operators. The higher the position in the table (IE the farther down in the table), the lower precedence something is.
            val |= include.issubset(tags) and exclude.isdisjoint(tags) << (len(table) - i - 1)
    return val

# Certain hard-coded modifications to the resultants of searches for antiphons and adds some tags
def managesearch(query, result):
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

def search(context, query, multipleresults = False, multipleresultssort = None, pilemod = []):
    for i in query:
        if i.startswith('/'):
            try:
                return context.get_untagged(i)
            except FileNotFoundError:
                return None

    pile = context.get_pile(query) + pilemod
    query |= set(context.get_book_tags())
    result = list(anysearch(query, pile))

    # If there is a non-zero amount of results discrimination is guaranteed to yield at least one result
    if len(result) == 0:
        warnings.warn(f'0 tags found for queries {list(query)} when searching {query}')
        return None

    for rule in context.getdiscrimen('general'):
        def discrim(item):
            tags = item['tags']
            if len(rule) == 1 and list(rule)[0].startswith('/'):
                return not tags.isdisjoint(context.expand_cat(list(rule)[0]))
            else:
                include = set(filter(lambda a: a[0] != '!', rule))
                exclude = {a[1:] for a in rule - include}
                return include.issubset(tags) and exclude.isdisjoint(tags)
        resultvalues = list(map(discrim, result))
        if any(resultvalues):
            result = [v for i, v in enumerate(result) if resultvalues[i]]
        if len(result) == 1:
            return managesearch(query, result[0])

    result = list(sorted(result, key=lambda a: len(a['tags']), reverse=True))
    if len(result[0]['tags']) != len(result[1]['tags']):
        return managesearch(query, result[0])
    elif not multipleresults:
        raise RuntimeError(f'Multiple equiprobable results for queries {query}:\n{result[0]}\n{result[1]}')
    else:
        return list([managesearch(query, i) for i in sorted(filter(lambda a : len(a['tags']) == len(result[-1]['tags']), result), multipleresultssort)])

# Special commemoration handling. Commemorations are hard because they rely on eachother and differ in number by day.
def handlecommemorations(context, item, selected, alternates):
        ret = []
        commemorations = sorted(list(filter(lambda a : 'commemoratio' in a, alternates)), key=lambda a:discriminate(context, 'rank', a), reverse=True)
        for i in commemorations:
            ret.append(process(context, {'formula','formula-commemorationis'}, i | (item - {'commemorationes'}), alternates))
        if len(commemorations) != 0:
            ret.append(process(context, {'collecta','terminatio','commemoratio'}, commemorations[-1] | (item - {'commemorationes'}), alternates))
        return {'tags':{'commemorationes'}, 'datum':ret}

def process(context, item, selected, alternates, pilemod = [], permit_empty = True):
    if item is None:
        return 'Absens'
    if selected is None:
        selected = frozenset()
    if alternates is None:
        alternates = []

    if 'commemorationes' in item:
        return handlecommemorations(context, item, selected, alternates)

    if type(item) is dict and 'quaere' in item:
        item['quaere'] = frozenset(item['quaere'])
        pilemod = [{'tags': item['quaere'], 'datum': item['datum']}]
        item = item['quaere']

    # An entry within an item that is a tagset is calling to search further for sub-items.
    if type(item) is set or type(item) is frozenset:
        selected = copy.deepcopy(selected)
        # Only remove positional tags when they are contradicted (for example, when the nona reading is requested by officium-capituli, remove officium-capituli)
        contras = set().union(*context.contradicted_cats('positionales', item | selected))
        selected -= contras

        result = None
        if not any('/' in i for i in item):
            for i in range(len(alternates)):
                # Basically if the tagset is explicitly calling for some day's propers, remove the other day context to facilitate this
                if 'occurrens' in item and item & context.expand_cat('temporale') <= alternates[i]:
                    item -= {'occurrens'}
                    alternates = copy.copy(alternates)
                    alternates.append(selected - context.expand_cat('positionales'))
                    selected = alternates.pop(i) | (selected & context.expand_cat('positionales'))
                    item -= context.expand_cat('temporale')
                    break

                # If there is an alternate with a specific object and position, it should be imposed on this tagset even if the tagset doesn't otherwise want a different day's item
                # Sometimes there are explicit tagsets in alternates that specify certain things (as oppo/sed to above when the data itself requests something)
                elif item | (selected & context.expand_cat('positionales')) <= alternates[i]:
                    alternates = copy.copy(alternates)
                    alternates.append(selected)

                    if len(list(context.contradicted_cats('positionales', item | alternates[i] | selected))):
                        selected = alternates.pop(i)
                    else:
                        selected = alternates.pop(i) | (selected & context.expand_cat('positionales'))
                    result = search(context, item | selected, pilemod=pilemod)
                    break

        if result is None:
            # Only remove tags referring to propers and commons and whatnot if a different set is suggested
            # This is different than the occurrens system because we're not asking about something on the specific day (for example, we want the ferial readings of the day)
            # but rather we may want the readings for the Common of the Blessed Virgin which isn't specific day-to-day
            if len(item & context.expand_cat('temporale')) != 0:
                selected -= set().union(*context.contradicted_cats('temporale', item | selected))
                selected |= item & context.expand_cat('temporale')

            result = search(context, item | selected, pilemod=pilemod)

        # If result is still None at this point, just tell user what was searched for
        if result is None and permit_empty:
            # It has to be sorted for testing purposes
            return str(sorted(list(item | selected)))
        elif result is None:
            return None
        selected |= item
        response = process(context, result, selected, alternates)

        return response

    elif type(item['datum']) is list:
        ret = []
        for i in item['datum']:
            if type(i) is str:
                if 'N.' in i:
                    i = i.replace('N. et N.', 'N.').replace('N.', search(context, item['tags'] | {'n'} | selected)['datum'])
                ret.append(i)
            elif i is None:
                ret.append(None)
            else:
                iprocessed = process(context, i, selected, alternates)
                if iprocessed is None:
                    ret.append('Absens')
                elif type(iprocessed) is list:
                    ret.extend(iprocessed)
                else:
                    ret.append(iprocessed)
        item['datum'] = ret if len(ret) != 1 else ret[0]
        return item

    # Often in the text there will be an N. replaced with the celebrated Saint's name.
    if type(item) is dict and 'N.' in item['datum']:
        item['datum'] = item['datum'].replace('N. et N.', 'N.').replace('N.', search(context, item['tags'] | {'n'} | selected)['datum'])
    return item

def generate(context, day, hour: str):
    hours = hour.split('+')
    assert set(hours).isdisjoint({'vesperae', 'completorium'}) or set(hours).isdisjoint({'matutinum', 'laudes', 'tertia', 'sexta', 'nona'})
    tags = copy.deepcopy(kalendar.daily_tagger.get_vespers(context, day) if not set(hours).isdisjoint({'vesperae', 'completorium'}) else kalendar.daily_tagger.get_diurnal(context, day))
    primary = list(filter(lambda i: 'primarium' in i, tags))[0]
    tags.remove(primary)

    lit = []
    for hour in hours:
        lit.append({'ritus', hour})
    return process(context, {'tags':{'ritus'},'datum':lit}, primary, tags)

if __name__ == '__main__':
    import argparse
    from datetime import date, datetime, timedelta
    import logging
    import sys

    import datamanage

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
        '-r',
        '--root',
        type=str,
        default='breviarium-1888',
        help='Data Root for Content',
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
            defaulthour = 'ante-officium+matutinum+laudes+post-officium'
        case 6 | 7:
            defaulthour = 'ante-officium+prima+post-officium'
        case 8 | 9 | 10:
            defaulthour = 'ante-officium+tertia+post-officium'
        case 11 | 12 | 13:
            defaulthour = 'ante-officium+sexta+post-officium'
        case 14 | 15:
            defaulthour = 'ante-officium+nona+post-officium'
        case 16 | 17 | 18 | 19:
            defaulthour = 'ante-officium+vesperae+post-officium'
        case 20 | 21 | 22 | 23:
            defaulthour = 'ante-officium+completorium+post-officium'

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
    day = datetime.strptime(args.date, '%Y-%m-%d').date()
    context = datamanage.get_context(args.root)
    ret = generate(context, day, args.hour)

    if args.output == sys.stdout:
        prettyprint(ret)
    else:
        # Write JSON output
        args.output.write(datamanage.dump_data(ret) + '\n')

