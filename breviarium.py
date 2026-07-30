#!/usr/bin/env python3

# Copyright 2025-2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import copy
import kalendar.daily_tagger
from composer import Rite

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

def generate(corpus, day, hours) -> Rite:
    tags = copy.deepcopy(kalendar.daily_tagger.get_vespers(corpus, day) if not set(hours).isdisjoint({'vesperae', 'completorium'}) else kalendar.daily_tagger.get_diurnal(corpus, day))
    primary = list(filter(lambda i: 'primarium' in i, tags))[0]
    tags.remove(primary)

    lit = []
    for hour in hours:
        lit.append({'ritus', hour})
    return corpus.compose({'tags':{'ritus'},'datum':lit}, primary, tags)

if __name__ == '__main__':
    import argparse
    from datetime import date, datetime, timedelta
    import logging
    import sys

    from composer import Corpus, Book
    import composer.util
    from pathlib import Path

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
            defaulthour = 'aperi-domine+matutinum+laudes+sacrosanctae'
        case 6 | 7:
            defaulthour = 'aperi-domine+prima+sacrosanctae'
        case 8 | 9 | 10:
            defaulthour = 'aperi-domine+tertia+sacrosanctae'
        case 11 | 12 | 13:
            defaulthour = 'aperi-domine+sexta+sacrosanctae'
        case 14 | 15:
            defaulthour = 'aperi-domine+nona+sacrosanctae'
        case 16 | 17 | 18 | 19:
            defaulthour = 'aperi-domine+vesperae+sacrosanctae'
        case 20 | 21 | 22 | 23:
            defaulthour = 'aperi-domine+completorium+sacrosanctae'

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
    corpus = Corpus(Book(Path(__file__).parent.joinpath('data').joinpath(args.root), ''))
    ret = generate(corpus, day, args.hour.split('+')).rite

    if args.output == sys.stdout:
        prettyprint(ret)
    else:
        # Write JSON output
        args.output.write(util.dump_data(ret) + '\n')

