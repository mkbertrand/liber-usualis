#!/usr/bin/env python3

from collections import defaultdict
from datetime import date, datetime, timedelta
import json
import logging
import pathlib
import re
from typing import NamedTuple, Optional, Self, Set

from kalendar.pascha import geteaster, nextsunday


data_root = pathlib.Path(__file__).parent.joinpath("data")

def load_data(p: str):
    data = json.loads(data_root.joinpath(p).read_text(encoding='utf-8'))

    # JSON doesn't support sets. Recursively find and replace anything that
    # looks like a list of tags with a set of tags.
    def recurse(obj):
        match obj:
            case dict():
                return {k: recurse(v) for k, v in obj.items()}
            case list():
                if all(type(x) == str for x in obj):
                    return frozenset(obj)
                return [recurse(v) for v in obj]
            case _:
                return obj

    return recurse(data)

epiphanycycle = load_data('epiphany.json')
paschalcycle = load_data('paschal.json')
adventcycle = load_data('advent.json')
nativitycycle = load_data('nativity.json')
movables = load_data('movables.json')
months = load_data('summer-autumn.json')
sanctoral = load_data('kalendar.json')
coincidence = json.loads(data_root.joinpath('coincidence.json').read_text(encoding='utf-8'))

threenocturnes = {"semiduplex","duplex","duplex-majus","duplex-ii-classis","duplex-i-classis"}
ranks = {"feria","commemoratio","simplex"} | threenocturnes
octavevigiltags = {"habens-octavam","habens-vigiliam","vigilia-excepta","incipit-libri"}
numerals = ['II','III','IV','V','VI','VII']


class SearchResult(NamedTuple):
    date: date
    feast: Set[str]

    def __str__(self) -> str:
        return self.date.strftime("%a %Y-%m-%d") + ":" + str(self.feast)

class Kalendar:
    def __init__(self, year: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.kal: defaultdict = defaultdict(list)
        self.year = year

    def add_entry(self, date: date, entry: set | frozenset) -> SearchResult:
        if type(entry) == frozenset:
            entry = set(entry)
        assert type(entry) == set
        self.kal[date].append(entry)
        return SearchResult(date, entry)

    def __ior__(self, other) -> Self:
        for date0, entries in other.kal.items():
            self.kal[date0] += entries
        return self

    def items(self):
        return self.kal.items()

    def __getitem__(self, key: date):
        return self.kal[key]

    def __repr__(self) -> str:
        return f"Kalendar(year={self.year!r})"

    def match(self, include: Set[str] = set(), exclude: Set[str] = set()):
        assert include.isdisjoint(exclude), f"{include!r} and {exclude!r} must be disjoint"
        for date0, entries in self.kal.items():
            for entry in entries:
                if entry >= include and entry.isdisjoint(exclude):
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
            raise RuntimeError(f"{self.year}: match_unique({include!r}, {exclude!r}) got no matches!") from e
        else:
            # Fail if multiple matches
            try:
                next(it)
            except StopIteration:
                pass
            else:
                raise RuntimeError(f"{self.year}: match_unique({include!r}, {exclude!r}) got more than one match!")
        return match

    def tagsindate(self, date: date) -> set:
        ret: Set[str] = set()
        for entry in self.kal.get(date, []):
            ret |= entry
        return ret

    # If mention is False there will be no mention that there was a feast in the original pre-tranfer date
    # The given entry must occur on match_date.
    def transfer_entry(self, match: SearchResult, *, target: Optional[date] = None, obstacles: Optional[Set[str]] = None, mention: bool = True) -> SearchResult:
        match_date, entry = match
        newfeast = entry | {"translatus"}

        # Compute date
        if target is None:
            target = match_date
        newdate = target
        if obstacles is not None:
            while not self.tagsindate(newdate).isdisjoint(obstacles):
                newdate = newdate + timedelta(days=1)

        # Skip transfer if it's to the same day
        if newdate == match_date:
            logging.debug(f"{self.year}: {entry!r} already on {newdate}")
            return match

        entries = self[match_date]
        assert entry in entries

        if mention:
            # Modify matching entries
            entries[:] = [
                e - ranks - octavevigiltags | {"translatus-originalis"}
                if e is entry
                else e
                for e in entries
            ]
        else:
            # Keep all but matching entries
            entries[:] = [e for e in entries if e is not entry]

        match = self.add_entry(newdate, newfeast)

        logging.debug(f"{self.year}: Transfer {entry!r} from {match_date} to {newdate}")
        assert match_date - timedelta(days=1) == newdate or match_date < newdate

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


def kalendar(year: int) -> Kalendar:
    kal = Kalendar(year=year)

    def todate(text: str, year0: int) -> date:
        m = re.match(r"(\d+)-(\d+)", text)
        if m is None:
            raise ValueError(f"Invalid date: {text}")
        return date(year0, int(m.group(1)), int(m.group(2)))

    easter = geteaster(year)
    christmas = date(year, 12, 25)
    adventstart = nextsunday(christmas, weeks=-4)
    xxiiipentecost = easter + timedelta(weeks=30)
    xxivpentecost = adventstart - timedelta(weeks=1)

    epiphanysunday = nextsunday(date(year, 1, 7))

    xxiiipentecostentry: Optional[Set[str]] = None
    omittedepiphanyentry: Optional[Set[str]] = None

    # Advent Cycle
    for entry in adventcycle:
        date0 = adventstart + timedelta(days=entry["difference"])
        # Christmas Eve is its own liturgical day that outranks whatever Advent day it's on but most of Matins comes from the day so Advent count is only stopped at Christmas
        if date0 == christmas:
            break
        kal.add_entry(date0, entry["tags"])

    # Paschal Cycle
    for entry in paschalcycle:
        date0 = easter + timedelta(days=entry["difference"])
        if date0 == xxivpentecost:
            xxiiipentecostentry = entry["tags"]
            break
        kal.add_entry(date0, entry["tags"])

    # Epiphany Sundays
    epiphanyweek = 0
    while epiphanysunday + timedelta(weeks=epiphanyweek) != easter - timedelta(weeks=9):
        for i in range(0,7):
            kal.add_entry(epiphanysunday + timedelta(weeks=epiphanyweek, days=i), epiphanycycle[epiphanyweek][i]["tags"])
        epiphanyweek += 1
    for i in range(0, 6 - epiphanyweek):
        sunday = xxivpentecost - timedelta(weeks=i + 1)
        if sunday != xxiiipentecost:
            for j in range(0,7):
                kal.add_entry(sunday + timedelta(days=j), epiphanycycle[5 - i][j]["tags"])
        else:
            omittedepiphanyentry = epiphanycycle[5 - i][0]["tags"]

    # Nativity & Epiphany
    for entry in nativitycycle:
        date0 = todate(entry["date"], year)
        kal.add_entry(date0, entry["tags"])
    kal.add_entry(nextsunday(christmas), movables["dominica-nativitatis"]["tags"])
    if date(year, 1, 6).isoweekday() == 7:
        epiphanysunday = date(year, 1, 12)
        kal.transfer({"epiphania","dominica"}, target=epiphanysunday)

    currday = 2
    for i in range(0, 6):
        if not date(year, 1, 7 + i) == epiphanysunday:
            kal.add_entry(date(year, 1, 7 + i), {"epiphania","semiduplex","infra-octavam","dies-" + numerals[currday - 2].lower()})
            currday += 1
    kal.add_entry(date(year, 1, 13), {"epiphania","dies-octava","duplex"})

    # Autumnal Weeks
    def nearsunday(kalends: date):
        if kalends.isoweekday() < 4:
            return nextsunday(kalends, weeks=-1)
        else:
            return nextsunday(kalends, weeks=0)
    for i in range(8, 11):
        kalends = nearsunday(date(year, i, 1))
        # Also works for November - December since Advent begins on the nearest Sunday to the Kalends of December
        nextkalends = nearsunday(date(year, i + 1, 1))
        month = months[["augustus","september","october","november"][i - 8]]
        j = 0
        while kalends + timedelta(weeks=j) != nextkalends:
            for k in range(0,7):
                kal.add_entry(kalends + timedelta(weeks=j, days=k), month[j][k]["tags"])
            j += 1
    kalends = nearsunday(date(year, 11, 1))
    # Also works for November - December since Advent begins on the nearest Sunday to the Kalends of December
    j = 0
    while kalends + timedelta(weeks=j) != adventstart:
        for k in range(0,7):
            kal.add_entry(kalends + timedelta(weeks=j, days=k), months["november"][j][k]["tags"])
        j += 1

    # Saints, and also handles leap years
    leapyear = year % 4 == 0 and (year % 400 == 0 or year % 100 != 0)
    for date0, entries in sanctoral.items():
        date0 = todate(str(date0), year)
        if leapyear and date0.month == 2 and date0.day >= 24:
            date0 = date0 + timedelta(days=1)
        for entry in entries:
            kal.add_entry(date0, entry)

    # List of inferred feasts that get merged in later
    buffer = Kalendar(year=year)

    # Movable feasts with occurrence attribute
    for name, movable in movables.items():
        if "occurrence" in movable:
            matches = kal.match(movable["occurrence"], movable.get("excluded", set()))
            for match_date, entry in matches:
                kal.add_entry(match_date, movable["tags"])

    kal |= buffer
    buffer.kal.clear()

    # Irregular movables
    assumption = date(year, 8, 15)
    if assumption.isoweekday() == 7:
        kal.add_entry(assumption + timedelta(days=1), movables["joachim"]["tags"])
    else:
        kal.add_entry(nextsunday(assumption), movables["joachim"]["tags"])
    # First Sunday of July
    kal.add_entry(nearsunday(date(year,7,1)), movables["pretiosissimi-sanguinis"]["tags"])
    nominis_bmv = date(year, 9, 8)
    if nominis_bmv.isoweekday() == 7:
        kal.add_entry(nominis_bmv + timedelta(days=1), movables["nominis-bmv"]["tags"])
    else:
        kal.add_entry(nextsunday(nominis_bmv), movables["nominis-bmv"]["tags"])

    # Octave and Vigil Processing
    for ent_date, entries in kal.items():
        for entry in entries:
            entry_base = entry - octavevigiltags - ranks
            if "habens-octavam" in entry and not "octava-excepta" in entry:
                for k in range(1,7):
                    date0 = ent_date + timedelta(days=k)
                    if "quadragesima" in kal.tagsindate(date0):
                        break
                    entrystripped = entry_base | {"semiduplex","infra-octavam","dies-" + numerals[k - 1].lower()}
                    # If a certain day within an Octave is manually entered, do not create one automatically
                    if kal.match_any(entrystripped) is None:
                        buffer.add_entry(date0, entrystripped)
                date0 = ent_date + timedelta(weeks=1)
                if "quadragesima" in kal.tagsindate(date0):
                    continue
                entrystripped = entry_base | {"duplex", "dies-octava"}
                # If a certain day within an Octave is manually entered, do not create one automatically
                if kal.match_any(entrystripped) is None:
                    buffer.add_entry(date0, entrystripped)
            if "habens-vigiliam" in entry and not "vigilia-excepta" in entry:
                entrystripped = entry_base | {"vigilia","poenitentialis","feria"}
                buffer.add_entry(ent_date - timedelta(days=1), entrystripped)

    kal |= buffer
    buffer.kal.clear()

    # 23rd Sunday Pentecost, 5th Sunday Epiphany Saturday transfer
    if xxiiipentecostentry:
        xxiiipentecostentry = set(xxiiipentecostentry)
        xxiiipentecostentry.add("translatus")
        i = 1
        while i < 7:
            if kal.tagsindate(xxivpentecost - timedelta(days=i)).isdisjoint(threenocturnes):
                kal.add_entry(xxivpentecost - timedelta(days=i), xxiiipentecostentry)
                break
            else:
                i += 1
        if i == 7:
            xxiiipentecostentry.add("commemoratio")
            xxiiipentecost.discard("semiduplex")
            kal.add_entry(xxivpentecost - timedelta(days=1), xxiiipentecostentry)
    if omittedepiphanyentry:
        omittedepiphanyentry = set(omittedepiphanyentry)
        omittedepiphanyentry.add("translatus")
        septuagesima = easter - timedelta(weeks=9)
        i = 1
        while i < 7:
            if kal.tagsindate(septuagesima - timedelta(days=i)).isdisjoint(threenocturnes):
                kal.add_entry(septuagesima - timedelta(days=i), omittedepiphanyentry)
                break
            else:
                i += 1
        if i == 7:
            omittedepiphanyentry.add("commemoratio")
            omittedepiphanyentry.discard("semiduplex")
            kal.add_entry(septuagesima - timedelta(days=1), omittedepiphanyentry)

    # Transfers
    
    print(coincidence)
    
    sjb = kal.match_unique({"nativitas-joannis-baptistae","duplex-i-classis"})
    corpuschristi = kal.match_unique({"corpus-christi","duplex-i-classis"})
    # N.B. Despite the Feast of the Nativity of S.J.B. being translated, its Octave is not adjusted with it, but still is based off the 24th of June.
    if sjb.date == corpuschristi.date:
        kal.transfer_entry(sjb, target=date(year, 6, 25))

    # Candlemas is granted the special privilege of being transferred to the next Monday if impeded by a Sunday II Class, regardless of the feast which falls on that Monday. It is thus included in the exceptions list.
    # Although Candlemas does not have an Octave, I added the "duplex-ii-classis" search tag in case a local Kalendar were to assign it an Octave.
    kal.transfer({"purificatio","duplex-ii-classis"}, obstacles={"dominica-ii-classis"})

    excepted = {"dominica-i-classis","dominica-ii-classis","pascha","pentecostes","ascensio","corpus-christi","purificatio","non-translandum","dies-octava","epiphania"}

    standardobstacles = {"dominica-i-classis","dominica-ii-classis","non-concurrentia","epiphania"}

    if date(year, 12, 29).isoweekday() != 7:
        # All days of Christmas Octave (or any Octave for that matter) are semiduplex which is why I used the thomas-becket tag specifically
        kal.transfer({"nativitas","dominica-infra-octavam"}, obstacles={"duplex-i-classis","duplex-ii-classis","thomas-cantuariensis"})
    else:
        kal.transfer({"thomas-cantuariensis"}, target=date(year, 12, 30))

    kal.transfer_all({"duplex-i-classis"}, obstacles=standardobstacles, exclude=excepted)
    standardobstacles |= {"duplex-i-classis", "marcus"}
    stmarks = kal.match_unique({"marcus", "duplex-ii-classis"})
    if "pascha" in kal.tagsindate(stmarks.date):
        kal.transfer_entry(stmarks, target=kal.match_unique({"feria-iii","hebdomada-i-paschae"}).date)
    excepted.add("marcus")
    kal.transfer_all({"duplex-ii-classis"}, obstacles=standardobstacles, exclude=excepted)
    standardobstacles |= {"duplex-ii-classis","dies-octava"}
    kal.transfer_all({"duplex-majus"}, obstacles=standardobstacles, exclude=excepted)
    standardobstacles |= {"duplex-majus"}
    kal.transfer_all({"doctor","duplex"}, obstacles=standardobstacles, exclude=excepted)

    for match_date, entry in kal.match({"vigilia"}, {"non-translandum"}):
        if "dominica" in kal.tagsindate(match_date):
            kal.transfer(entry, target=match_date - timedelta(days=1))

    kal.transfer({"fideles-defuncti"}, obstacles={"dominica"})

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

    # Generate kalendar
    ret = dict(sorted(kalendar(args.year).items()))

    # Convert datestrings to strings and sets into list
    ret = {str(k): [list(ent) for ent in v] for k, v in ret.items()}
    # Write JSON output
    args.output.write(json.dumps(ret) + "\n")
