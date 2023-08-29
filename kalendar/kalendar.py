#!/usr/bin/env python3

from __future__ import annotations
from collections import defaultdict
from datetime import date, datetime, timedelta
import json
import logging
import pathlib
import re
from typing import NamedTuple, Optional, Self, Set

from kalendar.pascha import geteaster, nextsunday


class SearchResult(NamedTuple):
    date: date
    feast: Set[str]

    def __str__(self) -> str:
        return self.date.strftime("%a %Y-%m-%d") + ":" + str(self.feast)


class KalendarRange:
    def __init__(self, year: int, kal_def: Kalendar, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.kal_def = kal_def

        self.kal: defaultdict = defaultdict(list)
        self.pending: defaultdict = defaultdict(list)
        self.year = year
        self.hold = 0

    def add_entry(self, date: date, entry: set | frozenset) -> SearchResult:
        if type(entry) == frozenset:
            entry = set(entry)
        assert type(entry) == set
        if self.hold > 0:
            self.pending[date].append(entry)
        else:
            self.kal[date].append(entry)
        return SearchResult(date, entry)

    def hold_pending(self) -> None:
        assert self.hold >= 0
        if self.hold == 0:
            assert len(self.pending) == 0
        self.hold = self.hold + 1

    def merge_pending(self) -> None:
        assert self.hold > 0, "Haven't been holding any changes"
        self.hold = self.hold - 1
        if self.hold == 0:
            for date0, entries in self.pending.items():
                self.kal[date0] += entries
            self.pending.clear()

    def __ior__(self, other) -> Self:
        for date0, entries in other.kal.items():
            self.kal[date0] += entries
        return self

    def items(self):
        return self.kal.items()

    def __getitem__(self, key: date):
        return self.kal[key]

    def __repr__(self) -> str:
        return f"KalendarRange(kal_def={self.kal_def!r}, year={self.year!r})"

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
        assert not (target is None and obstacles is None), "Useless call to transfer!"
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
                e - self.kal_def.strip_transfer | {"translatus-originalis"}
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


class Kalendar:
    def __init__(self, data_root: pathlib.Path, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.data_root = data_root

        self.strip_transfer: Set[str] = set()

    def gen(self, year: int) -> KalendarRange:
        raise NotImplementedError("Subclass must implement this!")

    def load_data(self, p: str) -> dict:
        data = json.loads(self.data_root.joinpath(p).read_text(encoding="utf-8"))

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

    def KalendarRange(self, *args, **kwargs) -> KalendarRange:
        return KalendarRange(*args, kal_def=self, **kwargs)


class Kalendar1888(Kalendar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, data_root=pathlib.Path(__file__).parent.joinpath("data"), **kwargs)

        self.epiphanycycle = self.load_data('epiphany.json')
        self.paschalcycle = self.load_data('paschal.json')
        self.adventcycle = self.load_data('advent.json')
        self.nativitycycle = self.load_data('nativity.json')
        self.movables = self.load_data('movables.json')
        self.months = self.load_data('summer-autumn.json')
        self.sanctoral = self.load_data('kalendar.json')
        self.coincidence = json.loads(self.data_root.joinpath('coincidence.json').read_text(encoding='utf-8'))

        self.threenocturnes = {"semiduplex","duplex","duplex-majus","duplex-ii-classis","duplex-i-classis"}
        self.ranks = {"feria","commemoratio","simplex"} | self.threenocturnes
        self.octavevigiltags = {"habens-octavam","habens-vigiliam","vigilia-excepta","incipit-libri"}
        self.strip_transfer = self.ranks | self.octavevigiltags
        self.numerals = ['II','III','IV','V','VI','VII']

    def gen(self, year: int) -> KalendarRange:
        kal = self.KalendarRange(year)

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

        def do_cycle(cycle, origin: Optional[date] = None, end: Optional[date] = None) -> Optional[Set[str]]:
            for i, entry in enumerate(cycle):
                match entry:
                    case {"difference": difference}:
                        assert origin is not None
                        date0 = origin + timedelta(days=entry["difference"])
                    case {"date": date}:
                        date0 = todate(date, year)
                    case _:
                        raise AssertionError("Unknown entry!")
                tags = entry["tags"]
                if end is not None and date0 == end:
                    return tags
                kal.add_entry(date0, tags)
            return None

        # Advent Cycle
        # Christmas Eve is its own liturgical day that outranks whatever Advent day it's on but most of Matins comes from the day so Advent count is only stopped at Christmas
        do_cycle(self.adventcycle, adventstart, christmas)

        # Paschal Cycle
        xxiiipentecostentry = do_cycle(self.paschalcycle, easter, xxivpentecost)

        # Epiphany Sundays
        epiphanyweek = 0
        while epiphanysunday + timedelta(weeks=epiphanyweek) != easter - timedelta(weeks=9):
            for i in range(0,7):
                kal.add_entry(epiphanysunday + timedelta(weeks=epiphanyweek, days=i), self.epiphanycycle[epiphanyweek][i]["tags"])
            epiphanyweek += 1
        for i in range(0, 6 - epiphanyweek):
            sunday = xxivpentecost - timedelta(weeks=i + 1)
            if sunday != xxiiipentecost:
                for j in range(0,7):
                    kal.add_entry(sunday + timedelta(days=j), self.epiphanycycle[5 - i][j]["tags"])
            else:
                omittedepiphanyentry = self.epiphanycycle[5 - i][0]["tags"]

        # Nativity & Epiphany
        do_cycle(self.nativitycycle)
        kal.add_entry(nextsunday(christmas), self.movables["dominica-nativitatis"]["tags"])
        if date(year, 1, 6).isoweekday() == 7:
            epiphanysunday = date(year, 1, 12)
            kal.transfer({"epiphania","dominica"}, target=epiphanysunday)

        currday = 2
        for i in range(0, 6):
            if not date(year, 1, 7 + i) == epiphanysunday:
                kal.add_entry(date(year, 1, 7 + i), {"epiphania","semiduplex","infra-octavam","dies-" + self.numerals[currday - 2].lower()})
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
            month = self.months[["augustus","september","october","november"][i - 8]]
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
                kal.add_entry(kalends + timedelta(weeks=j, days=k), self.months["november"][j][k]["tags"])
            j += 1

        # Saints, and also handles leap years
        leapyear = year % 4 == 0 and (year % 400 == 0 or year % 100 != 0)
        for date0, entries in self.sanctoral.items():
            date0 = todate(str(date0), year)
            if leapyear and date0.month == 2 and date0.day >= 24:
                date0 = date0 + timedelta(days=1)
            for entry in entries:
                kal.add_entry(date0, entry)

        kal.hold_pending()

        # Movable feasts with occurrence attribute
        for name, movable in self.movables.items():
            if "occurrence" in movable:
                matches = kal.match(movable["occurrence"], movable.get("excluded", set()))
                for match_date, entry in matches:
                    kal.add_entry(match_date, movable["tags"])

        kal.merge_pending()

        # Irregular movables
        assumption = date(year, 8, 15)
        if assumption.isoweekday() == 7:
            kal.add_entry(assumption + timedelta(days=1), self.movables["joachim"]["tags"])
        else:
            kal.add_entry(nextsunday(assumption), self.movables["joachim"]["tags"])
        # First Sunday of July
        kal.add_entry(nearsunday(date(year,7,1)), self.movables["pretiosissimi-sanguinis"]["tags"])
        nominis_bmv = date(year, 9, 8)
        if nominis_bmv.isoweekday() == 7:
            kal.add_entry(nominis_bmv + timedelta(days=1), self.movables["nominis-bmv"]["tags"])
        else:
            kal.add_entry(nextsunday(nominis_bmv), self.movables["nominis-bmv"]["tags"])

        kal.hold_pending()

        # Octave and Vigil Processing
        for ent_date, entries in kal.items():
            for entry in entries:
                entry_base = entry - self.ranks - self.octavevigiltags
                if "habens-octavam" in entry and not "octava-excepta" in entry:
                    for k in range(1,7):
                        date0 = ent_date + timedelta(days=k)
                        if "quadragesima" in kal.tagsindate(date0):
                            break
                        entrystripped = entry_base | {"semiduplex","infra-octavam","dies-" + self.numerals[k - 1].lower()}
                        # If a certain day within an Octave is manually entered, do not create one automatically
                        if kal.match_any(entrystripped) is None:
                            kal.add_entry(date0, entrystripped)
                    date0 = ent_date + timedelta(weeks=1)
                    if "quadragesima" in kal.tagsindate(date0):
                        continue
                    entrystripped = entry_base | {"duplex", "dies-octava"}
                    # If a certain day within an Octave is manually entered, do not create one automatically
                    if kal.match_any(entrystripped) is None:
                        kal.add_entry(date0, entrystripped)
                if "habens-vigiliam" in entry and not "vigilia-excepta" in entry:
                    entrystripped = entry_base | {"vigilia","poenitentialis","feria"}
                    kal.add_entry(ent_date - timedelta(days=1), entrystripped)

        kal.merge_pending()

        # 23rd Sunday Pentecost, 5th Sunday Epiphany Saturday transfer
        if xxiiipentecostentry:
            xxiiipentecostentry = set(xxiiipentecostentry)
            xxiiipentecostentry.add("translatus")
            i = 1
            while i < 7:
                if kal.tagsindate(xxivpentecost - timedelta(days=i)).isdisjoint(self.threenocturnes):
                    kal.add_entry(xxivpentecost - timedelta(days=i), xxiiipentecostentry)
                    break
                else:
                    i += 1
            if i == 7:
                xxiiipentecostentry.add("commemoratio")
                xxiiipentecostentry.discard("semiduplex")
                kal.add_entry(xxivpentecost - timedelta(days=1), xxiiipentecostentry)
        if omittedepiphanyentry:
            omittedepiphanyentry = set(omittedepiphanyentry)
            omittedepiphanyentry.add("translatus")
            septuagesima = easter - timedelta(weeks=9)
            i = 1
            while i < 7:
                if kal.tagsindate(septuagesima - timedelta(days=i)).isdisjoint(self.threenocturnes):
                    kal.add_entry(septuagesima - timedelta(days=i), omittedepiphanyentry)
                    break
                else:
                    i += 1
            if i == 7:
                omittedepiphanyentry.add("commemoratio")
                omittedepiphanyentry.discard("semiduplex")
                kal.add_entry(septuagesima - timedelta(days=1), omittedepiphanyentry)

        # Transfers
        sjb = kal.match_unique({"nativitas-joannis-baptistae","duplex-i-classis"})
        corpuschristi = kal.match_unique({"corpus-christi","duplex-i-classis"})
        # N.B. Despite the Feast of the Nativity of S.J.B. being translated, its Octave is not adjusted with it, but still is based off the 24th of June.
        if sjb.date == corpuschristi.date:
            kal.transfer_entry(sjb, target=date(year, 6, 25))

        # Candlemas is granted the special privilege of being transferred to the next Monday if impeded by a Sunday II Class, regardless of the feast which falls on that Monday. It is thus included in the exceptions list.
        # Although Candlemas does not have an Octave, I added the "duplex-ii-classis" search tag in case a local kalendar were to assign it an Octave.
        kal.transfer({"purificatio","duplex-ii-classis"}, obstacles={"dominica-ii-classis"})

        excepted = {"dominica-i-classis","dominica-ii-classis","pascha","pentecostes","ascensio","corpus-christi","purificatio","non-translandum","dies-octava","epiphania"}

        standardobstacles = {"dominica-i-classis","dominica-ii-classis","non-concurrentia","epiphania"}

        if date(year, 12, 29).isoweekday() != 7:
            # All days of Christmas Octave (or any Octave for that matter) are semiduplex which is why I used the thomas-cantuariensis tag specifically
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


def kalendar(year: int) -> KalendarRange:
    logging.warning("kalendar(year) is deprecated: use Kalendar(...).gen(year) instead")
    kal_def = Kalendar1888()
    return kal_def.gen(year)


kalendars = {
    "1888": Kalendar1888,
}


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
        "-k",
        "--kalendar",
        choices=kalendars.keys(),
        default="1888",
        help="Kalendar version",
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

    # Load kalendar definition
    kal_def = kalendars[args.kalendar]()

    # Generate kalendar
    ret = dict(sorted(kal_def.gen(args.year).items()))

    # Convert datestrings to strings and sets into lists
    ret = {str(k): [list(ent) for ent in v] for k, v in ret.items()}
    # Write JSON output
    args.output.write(json.dumps(ret) + "\n")
