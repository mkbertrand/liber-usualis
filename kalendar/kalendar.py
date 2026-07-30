#!/usr/bin/env python3

# Copyright 2024-2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

from collections import defaultdict
from datetime import date, datetime, timedelta
import copy
import json
import logging
import re
from typing import NamedTuple, Optional, Self, Set
import itertools
import pathlib

from kalendar.datamanage import load_data, flatten, get_bookshelf
from kalendar.pascha import geteaster, nextsunday
from kalendar.dies import leapyear, menses, mensum, numerals, latindate

threenocturnes = {'semiduplex','duplex-minus','duplex-majus','duplex-ii-classis','duplex-i-classis'}
ranks = {'feria','commemoratio','simplex'} | threenocturnes
octavevigiltags = {'habens-octavam','incipit-libri'}
feriae = ['dominica','feria-ii','feria-iii','feria-iv','feria-v','feria-vi','sabbatum']
roletagsordered = ['primarium', 'commemoratio', 'omissum', 'tempus']
roletags = set(roletagsordered)
noprimarium = roletags | {'psalmi-graduales', 'psalmi-poenitentiales', 'litaniae-sanctorum', 'officium-parvum-bmv', 'officium-defunctorum', 'votiva', 'antiphona-bmv','scriptura','pro-antiphona-magnificat','translatus-originalis','pro-aliis-officiis'}

class SearchResult(NamedTuple):
    date: date
    feast: Set[str]

    def __str__(self) -> str:
        return self.date.strftime('%a %Y-%m-%d') + ':' + str(self.feast)

class Kalendar:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.kal: defaultdict = defaultdict(list)

    def add_entry(self, date: date, entry: set | frozenset) -> SearchResult:
        if type(entry) is frozenset:
            entry = set(entry)
        assert type(entry) is set
        self.kal[date].append(entry)
        return SearchResult(date, entry)

    def __ior__(self, other) -> Self:
        for date0, entries in other.kal.items():
            self.kal[date0] += entries
        return self

    def keys(self):
        return self.kal.keys()

    def items(self):
        return self.kal.items()

    def __getitem__(self, key: date):
        return self.kal[key]

    def __repr__(self) -> str:
        return f'Kalendar()'

    def match(self, include: Set[str] = set(), exclude: Set[str] = set()):
        assert include.isdisjoint(exclude), f'{include!r} and {exclude!r} must be disjoint'
        for date0, entries in self.kal.items():
            if set().union(*entries).isdisjoint(exclude):
                for entry in entries:
                    if entry >= include:
                        yield SearchResult(date0, entry)

    def match_any(self, include: Set[str] = set(), exclude: Set[str] = set()) -> Optional[SearchResult]:
        # Check whether kal.match returns any matches
        return next(self.match(include, exclude), None)

    def match_unique(self, include: Set[str] = set(), exclude: Set[str] = set()) -> SearchResult:
        # Get the first match from kal.match
        it = self.match(include, exclude)
        try:
            match = next(it)
        except StopIteration as e:
            # Fail if zero matches
            raise RuntimeError(f'match_unique({include!r}, {exclude!r}) got no matches!') from e
        else:
            # Fail if multiple matches
            try:
                next(it)
            except StopIteration:
                pass
            else:
                raise RuntimeError(f'match_unique({include!r}, {exclude!r}) got more than one match!')
        return match

    def tags_in_date(self, date: date) -> set:
        ret: Set[str] = set()
        for entry in self.kal.get(date, []):
            ret |= entry
        return ret

    # If mention is False there will be no mention that there was a feast in the original pre-tranfer date
    # The given entry must occur on match_date.
    def transfer_entry(self, match: SearchResult, *, target: Optional[date] = None, obstacles: Optional[Set[str]] = None, mention: bool = True) -> SearchResult:
        assert not (target is None and obstacles is None), 'Useless call to transfer!'
        match_date, entry = match
        newfeast = entry | {'translatum'}

        # Compute date
        if target is None:
            target = match_date
        newdate = target
        if obstacles is not None:
            while not self.tags_in_date(newdate).isdisjoint(obstacles):
                newdate = newdate + timedelta(days=1)

        # Skip transfer if it's to the same day
        if newdate == match_date:
            logging.debug(f'{entry!r} already on {newdate}')
            return match

        entries = self[match_date]
        assert entry in entries

        if mention:
            # Modify matching entries
            entries[:] = [
                e - ranks - octavevigiltags | {'translatus-originalis'}
                if e is entry
                else e
                for e in entries
            ]
        else:
            # Keep all but matching entries
            entries[:] = [e for e in entries if e is not entry]

        match = self.add_entry(newdate, newfeast)

        logging.debug(f'Transfer {entry!r} from {match_date} to {newdate}')
        assert match_date - timedelta(days=1) == newdate or match_date < newdate

        assert not (target is None and obstacles is None)

        return match

    # Automatically decide the suitable date whither the feast should be transferred
    # Fails if not exactly one feast matches
    def transfer(self, tags, *, exclude: Set[str] = set(), target: Optional[date] = None, obstacles: Optional[Set[str]] = None, mention: bool = True) -> SearchResult:
        match = self.match_unique(tags, exclude)
        return self.transfer_entry(match, target=target, obstacles=obstacles, mention=mention)

    # Transfer multiple feasts
    def transfer_all(self, tags, *, exclude: Set[str] = set(), obstacles: Optional[Set[str]] = None, mention: bool = True) -> None:
        for match in list(self.match(tags, exclude)):
            self.transfer_entry(match, obstacles=obstacles, mention=mention)


def nearest_sunday(kalends: date):
    if kalends.isoweekday() < 4:
        return nextsunday(kalends, weeks=-1)
    else:
        return nextsunday(kalends, weeks=0)

# N.B. This is a mutable function. It will change kal
def apply_tabella(kal, tabella):

    rules = flatten(tabella)

    class Job(NamedTuple):
        days: tuple
        rule: dict
        parentnumber: int = -1

    prioritization_stack = [Job(tuple(kal.keys()), rule) for rule in rules]
    prioritization_stack.reverse()
    ruleskip = [False] * len(rules)

    def resolvejob(job):
        if ruleskip[job.rule['number']]:
            return
        # If we have reached a rule following a rule which shouldn't be rechecked, mark it off as done
        if job.rule['number'] != 0 and not rules[job.rule['number'] - 1]['recheck']:
            ruleskip[job.rule['number'] - 1] = True

        for day in job.days:

            tagsetindices = range(len(kal[day]))
            matchset = []
            failsearch = False
            for restriction in job.rule['restrict']:
                search = [tagsetindex for tagsetindex in tagsetindices if restriction.include <= kal[day][tagsetindex] and not (restriction.exclude and (restriction.exclude <= kal[day][tagsetindex] if type(restriction.exclude) is frozenset else any(i <= kal[day][tagsetindex] for i in restriction.exclude)))]
                if len(search) == 0:
                    failsearch = True
                    break
                else:
                    matchset.append(search)

            if failsearch:
                continue

            matches = list(itertools.product(*matchset))

            for match in matches:
                if len(set(match)) == len(job.rule['restrict']):
                    if job.rule['response'] == 'combina':
                        kal[day][match[0]] |= kal[day][match[1]]
                        if len(kal[day][match[0]] & roletags) > 1:
                            for i in roletagsordered:
                                if i in kal[day][match[0]]:
                                    kal[day][match[0]] -= roletags
                                    kal[day][match[0]].add(i)
                                    break
                        kal[day].pop(match[1])
                        # We will restart this job from scratch when we've iterated through the more specific jobs
                        prioritization_stack.append(job)
                        prioritization_stack.extend([Job([day], rules[num]) for num in range(job.rule['number'] - 1, -1, -1)])
                    elif job.rule['response'] == 'errora':
                        raise RuntimeError(f'Unexpected coincidence on day {kal[day]} involving {match}')
                    else:
                        target = match[job.rule['target']]

                        if 'adde' in job.rule:
                            if type(job.rule['adde']) is frozenset:
                                kal[day][target] |= job.rule['adde']
                            else:
                                kal[day][target] |= {job.rule['adde']}
                        if 'remove' in job.rule:
                            if type(job.rule['remove']) is frozenset:
                                kal[day][target] -= job.rule['remove']
                            else:
                                kal[day][target] -= {job.rule['remove']}

                        if job.rule['response'] == 'dele':
                            kal[day].pop(target)
                            prioritization_stack.append(job)
                        elif job.rule['response'] == 'transfer':
                            move = kal[day].pop(target)
                            transferday = (day + timedelta(days=job.rule['movement'])) if type(job.rule['movement']) is int else kal.match_unique(job.rule['movement']).date
                            kal[transferday].append(move)
                            prioritization_stack.append(job)
                            parentnumber = job.parentnumber if job.parentnumber != -1 else job.rule['number']
                            prioritization_stack.extend([Job([transferday], rules[num], parentnumber) for num in range(job.parentnumber, job.rule['number'] - 1, -1)])
                            prioritization_stack.extend([Job([day, transferday], rules[num], parentnumber) for num in range(job.rule['number'] - 1, -1, -1)])
                        elif type(job.rule['response']) is frozenset and 'movement' in job.rule:
                            transferday = (day + timedelta(days=job.rule['movement'])) if type(job.rule['movement']) is int else kal.match_unique(job.rule['movement']).date
                            if job.rule['response'] in kal[transferday]:
                                continue
                            kal[transferday].append(job.rule['response'])
                            prioritization_stack.append(job)
                            parentnumber = job.parentnumber if job.parentnumber != -1 else job.rule['number']
                            prioritization_stack.extend([Job([transferday], rules[num], parentnumber) for num in range(job.parentnumber, job.rule['number'] - 1, -1)])
                            prioritization_stack.extend([Job([day, transferday], rules[num], parentnumber) for num in range(job.rule['number'] - 1, -1, -1)])
                        elif type(job.rule['response']) is frozenset:
                            if job.rule['response'] <= kal[day][target]:
                                continue
                            if job.rule['response'] & roletags:
                                kal[day][target] -= roletags
                            kal[day][target] |= job.rule['response']
                            prioritization_stack.append(job)
                            if not job.rule['continue']:
                                prioritization_stack.extend([Job([day], rules[num]) for num in range(job.rule['number'] - 1, -1, -1)])
                        elif not type(job.rule['response']) is str:
                            raise RuntimeError(type(job.rule['response']))
                        else:
                            if job.rule['response'] in kal[day][target]:
                                continue
                            if job.rule['response'] in roletags:
                                kal[day][target] -= roletags
                            kal[day][target].add(job.rule['response'])
                            prioritization_stack.append(job)
                            if not job.rule['continue']:
                                prioritization_stack.extend([Job([day], rules[num]) for num in range(job.rule['number'] - 1, -1, -1)])
                    if job.rule['continue']:
                        return

    while len(prioritization_stack) != 0:
        resolvejob(prioritization_stack.pop())

def kalendar(bookshelf: pathlib.Path, year: int) -> Kalendar:

    adventcycle = load_data('de-adventu.json', bookshelf.book_srcs()[0])
    nativitycycle = load_data('in-tempore-nativitatis.json', bookshelf.book_srcs()[0])
    epiphanycycle = load_data('epiphania.json', bookshelf.book_srcs()[0])
    paschalcycle = load_data('de-paschali.json', bookshelf.book_srcs()[0])
    autumnalcycle = load_data('autumnalis.json', bookshelf.book_srcs()[0])
    movables = load_data('motabiles.json', bookshelf.book_srcs()[0])
    kalendarium = load_data('kalendarium.json', bookshelf.book_srcs()[0])
    tabella = load_data('tabella.json', bookshelf.book_srcs()[0])

    kal = Kalendar()

    easter = geteaster(year)
    christmas = date(year, 12, 25)
    adventstart = nextsunday(christmas, weeks=-4)
    epiphanysunday = nextsunday(date(year, 1, 7))

    bases = {'dominica-i-adventus': adventstart, 'pascha': easter, 'dominica-infra-epiphaniam': epiphanysunday}

    i = date(year, 1, 1)
    while not i == date(year + 1, 1, 1):
        kal.add_entry(i, {'tempus', menses[i.month - 1], latindate(i)})
        i = i + timedelta(days=1)
    for i in range(0, 13):
        if i == 0:
            kalends = nearest_sunday(date(year - 1, 12, 1))
        else:
            kalends = nearest_sunday(date(year, i, 1))
        if i == 12:
            nextkalends = nearest_sunday(date(year + 1, 1, 1))
        else:
            nextkalends = nearest_sunday(date(year, i + 1, 1))
        j = 0
        while kalends + timedelta(weeks=j) != nextkalends:
            bases[f'dominica-{numerals[j]}-{mensum[(i - 1) % 12]}'] = kalends + timedelta(weeks=j)
            for k in range(0,7):
                if not (kalends + timedelta(weeks=j, days=k)).year == year:
                    continue
                kal[kalends + timedelta(weeks=j, days=k)][0].add(feriae[k])
                kal[kalends + timedelta(weeks=j, days=k)][0].add(f'hebdomada-{numerals[j]}-{mensum[(i - 1) % 12]}')
                kal[kalends + timedelta(weeks=j, days=k)][0].add(f'hebdomadae-{mensum[(i - 1) % 12]}')
            j += 1
        if i == 12 and nextkalends.year == year:
            for j in range(0,7):
                if (nextkalends + timedelta(days=j)).year == year + 1:
                    break
                kal[nextkalends + timedelta(days=j)][0].add(feriae[j])
                kal[nextkalends + timedelta(days=j)][0].add('hebdomada-i-januarii')
                kal[nextkalends + timedelta(days=j)][0].add('hebdomadae-januarii')

    cycles = [adventcycle, paschalcycle, autumnalcycle]

    xxiiipentecost = easter + timedelta(weeks=30)
    xxivpentecost = adventstart - timedelta(weeks=1)

    xxiiipentecostentry: Optional[Set[str]] = None
    omittedepiphanyentry: Optional[Set[str]] = None

    # Octave Processing
    def octavate(ent_date, entry):
        if 'habens-octavam' in entry and 'octava-excepta' not in entry:
            entry_base = entry - ranks - octavevigiltags - {'scriptura-propria'}
            for k in range(1,7):
                date0 = ent_date + timedelta(days=k)
                entrystripped = entry_base | {'semiduplex','infra-octavam','dies-' + numerals[k]}
                if date0.isoweekday() == 7:
                    entrystripped |= {'dominica-infra-octavam'}
                # If a certain day within an Octave is manually entered, do not create one automatically
                if kal.match_any(entrystripped) is None:
                    kal.add_entry(date0, entrystripped)
            date0 = ent_date + timedelta(weeks=1)
            entrystripped = entry_base | {'duplex-minus', 'dies-octava'}
            if date0.isoweekday() == 7:
                entrystripped |= {'dominica-infra-octavam'}
            # If a certain day within an Octave is manually entered, do not create one automatically
            if kal.match_any(entrystripped) is None:
                kal.add_entry(date0, entrystripped)

    for cycle in cycles:
        for entry in cycle:
            for tagset in entry['tags'] if type(entry['tags']) is list else [entry['tags']]:
                kal.add_entry(bases[entry['basis']] + timedelta(days=entry['offset']), tagset)
                octavate(bases[entry['basis']] + timedelta(days=entry['offset']), tagset)

    # Epiphany Sundays
    epiphanyweek = 0
    while epiphanysunday + timedelta(weeks=epiphanyweek) != easter - timedelta(weeks=9):
        for i in range(0,7):
            kal.add_entry(epiphanysunday + timedelta(weeks=epiphanyweek, days=i), epiphanycycle[epiphanyweek][i]['tags'] | {'post-epiphaniam'})
        epiphanyweek += 1
    for i in range(0, 6 - epiphanyweek):
        sunday = xxivpentecost - timedelta(weeks=i + 1)
        if sunday != xxiiipentecost:
            for j in range(0,7):
                kal.add_entry(sunday + timedelta(days=j), epiphanycycle[5 - i][j]['tags'] | {'post-pentecosten'})
        else:
            omittedepiphanyentry = epiphanycycle[5 - i][0]['tags']

    # Nativity & Epiphany
    for entry in nativitycycle:
        for tagset in entry['tags'] if type(entry['tags']) is list else [entry['tags']]:
            kal.add_entry(kal.match_unique(entry['occurrence']).date, tagset)

    kal.add_entry(nextsunday(christmas), {'nativitas','dominica-infra-octavam','semiduplex','in-tempore-nativitatis'})
    kal.add_entry(epiphanysunday, {'epiphania','dominica-infra-octavam','infra-octavam','semiduplex','per-octavam-epiphaniae'})
    if date(year, 1, 6).isoweekday() == 7:
        epiphanysunday = date(year, 1, 12)
        kal.transfer({'epiphania','dominica-infra-octavam'}, target=epiphanysunday)

    currday = 2
    pdom = False
    for i in range(0, 6):
        if not date(year, 1, 7 + i) == epiphanysunday:
            kal.add_entry(date(year, 1, 7 + i), {'epiphania','semiduplex','infra-octavam','dies-' + numerals[currday - 1], 'post-dominicam' if pdom else 'ante-dominicam','per-octavam-epiphaniae'})
            currday += 1
        else:
            kal.add_entry(date(year, 1, 7 + i), {'epiphania','semiduplex','infra-octavam','commemoratio','per-octavam-epiphaniae'})
            pdom = True

    kal.add_entry(date(year, 1, 13), {'epiphania','dies-octava','duplex-minus','per-octavam-epiphaniae'})

    octaveagenda = []
    deferred_entries = []
    # Kalendar (of Saints)
    entries = copy.deepcopy(kalendarium)
    for entry in entries:
        matches = None
        if 'dominica-infra-octavam' in entry['occurrence']:
            deferred_entries.append(entry)
        if type(entry['occurrence']) is list:
            matches = []
            for i in entry['occurrence']:
                matches.extend(kal.match(i, entry.get('excluded', set())))
        else:
            matches = kal.match(entry['occurrence'], entry.get('excluded', set()))
        offset = entry['offset'] if 'offset' in entry else 0
        for match_date in set([i.date for i in matches]):
            for tagset in entry['tags'] if type(entry['tags']) is list else [entry['tags']]:
                kal.add_entry(match_date + timedelta(days=offset), tagset)
                if 'habens-octavam' in tagset and 'octava-excepta' not in tagset:
                    octaveagenda.append((match_date + timedelta(days=offset), tagset))

    # Do Octave stuff after since there may be manually entered days within Octaves or Octave-Days
    for i in octaveagenda:
        octavate(i[0], i[1])

    # Deferred Kalendar entries
    for entry in deferred_entries:
        for tagset in entry['tags'] if type(entry['tags']) is list else [entry['tags']]:
            kal.add_entry(kal.match_unique(entry['occurrence']).date, tagset)

    # Movables
    entries = copy.deepcopy(movables)
    for entry in entries:
        matches = None
        if type(entry['occurrence']) is list:
            matches = []
            for i in entry['occurrence']:
                matches.extend(kal.match(i, entry.get('excluded', set())))
        else:
            matches = kal.match(entry['occurrence'], entry.get('excluded', set()))
        offset = entry['offset'] if 'offset' in entry else 0
        for match_date in set([i.date for i in matches]):
            kal.add_entry(match_date + timedelta(days=offset), entry['tags'])

    # 23rd Sunday Pentecost, 5th Sunday Epiphany Saturday transfer
    if 'hebdomada-xxiii-pentecostes' in kal.tags_in_date(xxivpentecost):
        xxiiipentecostentry = kal.match_unique({'hebdomada-xxiii-pentecostes', 'dominica'}).feast
        xxiiipentecostentry |= {'translatum', 'feria'}
        xxiiipentecostentry -= {'semiduplex'}
        i = 1
        while i < 7:
            if kal.tags_in_date(xxivpentecost - timedelta(days=i)).isdisjoint(threenocturnes):
                kal.add_entry(xxivpentecost - timedelta(days=i), xxiiipentecostentry)
                break
            else:
                i += 1
        if i == 7:
            xxiiipentecostentry |= {'commemoratio'}
            kal.add_entry(xxivpentecost - timedelta(days=1), xxiiipentecostentry)
    if omittedepiphanyentry:
        omittedepiphanyentry |= {'translatum', 'feria', 'post-epiphaniam'}
        omittedepiphanyentry -= {'semiduplex'}
        septuagesima = easter - timedelta(weeks=9)
        i = 1
        while i < 7:
            if kal.tags_in_date(septuagesima - timedelta(days=i)).isdisjoint(threenocturnes):
                kal.add_entry(septuagesima - timedelta(days=i), omittedepiphanyentry)
                break
            else:
                i += 1
        if i == 7:
            omittedepiphanyentry |= {'commemoratio'}
            kal.add_entry(septuagesima - timedelta(days=1), omittedepiphanyentry)

    for entrydate, entries in kal.items():
        for entry in entries:
            if entry.isdisjoint(noprimarium):
                entry.add('primarium')

    for i in tabella:
        apply_tabella(kal, i)

    return kal

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Liturgical calendar generator",
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
        "-y",
        "--year",
        type=int,
        default=datetime.now().year,
        help="Year to generate",
    )

    args = parser.parse_args()

    if args.verbosity:
        logging.getLogger().setLevel(args.verbosity)

    bookshelf = get_bookshelf('breviarium-1888')
    # Generate kalendar
    ret = dict(sorted(kalendar(bookshelf, args.year).items()))

    # Convert datestrings to strings and sets into lists
    ret = {str(k): [list(ent) for ent in v] for k, v in ret.items()}
    # Write JSON output
    args.output.write(json.dumps(ret) + "\n")
