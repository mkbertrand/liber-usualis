#!/usr/bin/env python3

# Copyright 2025-2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import copy
import kalendar.daily_tagger

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

def generate(context, day, hours):
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
    ret = generate(context, day, args.hour.split('+'))

    if args.output == sys.stdout:
        prettyprint(ret)
    else:
        # Write JSON output
        args.output.write(datamanage.dump_data(ret) + '\n')

