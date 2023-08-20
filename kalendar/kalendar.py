#!/usr/bin/env python3

from collections import defaultdict
from datetime import datetime
from datetime import date
from datetime import timedelta
import logging
import pathlib
import json
import copy
from kalendar import pascha


data_root = pathlib.Path(__file__).parent.joinpath("data")

def load_data(p):
    data = json.loads(data_root.joinpath(p).read_text(encoding="utf-8"))

    # JSON doesn't support sets. Recursively find and replace anything that
    # looks like a list of tags with a set of tags.
    def recurse(obj):
        match obj:
            case dict():
                obj2 = {}
                for k, v in obj.items():
                    if type(v) == list and all(type(x) == str for x in v):
                        v = set(v)
                    obj2[k] = recurse(v)
                return obj2
            case list():
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

threenocturnes = {"semiduplex","duplex","duplex-majus","duplex-ii-classis","duplex-i-classis"}
ranks = {"feria","commemoratio","simplex"} | threenocturnes
octavevigiltags = {"habens-octavam","has-special-octave","habens-vigiliam","vigilia-excepta","incipit-libri"}
numerals = ['II','III','IV','V','VI','VII']


class SearchResult:
    def __init__(self, date, feast):
        self.date = date
        self.feast = feast

    def __str__(self):
        return str(self.date) + ":" + str(self.feast)


def datestring(date0):
    return str(date0.month).zfill(2) + '-' + str(date0.day).zfill(2)


class Kalendar:
    def __init__(self, year, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.kal = defaultdict(list)
        self.year = year

    def add_entry(self, date, entry):
        assert type(entry) == set
        self.kal[date].append(entry)

    def __ior__(self, other):
        for date0, entries in other.kal.items():
            self.kal[date0] += entries
        return self

    def items(self):
        return self.kal.items()

    def __getitem__(self, key):
        return self.kal[key]

    def match(self, include=set(), exclude=set()):
        for date0, entries in self.kal.items():
            for entry in entries:
                if entry >= include and entry.isdisjoint(exclude):
                    yield SearchResult(date0, entry)

    def match_unique(self, include=set(), exclude=set(), none_ok=False):
        # Get the first match from kal.match
        it = self.match(include, exclude)
        match = next(it, None)
        if match is None:
            if none_ok:
                return None
            # Fail if zero matches
            raise RuntimeError(f"{self.year}: match_unique({include!r}, {exclude!r}) got no matches!")
        else:
            # Fail if multiple matches
            try:
                next(it)
            except StopIteration:
                pass
            else:
                raise RuntimeError(f"{self.year}: match_unique({include!r}, {exclude!r}) got more than one match!")
        return match

    def tagsindate(self, date):
        ret = set()
        for entry in self.kal.get(date, []):
            ret |= entry
        return ret


def kalendar(year):
    kal = Kalendar(year=year)

    def sundayafter(date0):
        return date0 + timedelta(days=6-date0.weekday()) if date0.weekday() != 6 else date0 + timedelta(days=7)
    def todate(text, year0):
        return date(year0, int(text[:2]), int(text[3:]))

    # Will not work as intended if multiple matches are found for the tags
    # If match is False there will be no mention that there was a feast in the original pre-tranfer date
    def transfer(tags, target, mention):
        match = kal.match_unique(tags)
        newfeast = copy.deepcopy(match.feast)
        newfeast.add("translatus")
        kal.add_entry(target, newfeast)
        for i in range(0,len(kal[match.date])):
            if kal[match.date][i] >= tags:
                if mention:
                    oldfeast = copy.deepcopy(kal[match.date][i])
                    oldfeast.add("translatus-originalis")
                    oldfeast -= ranks
                    oldfeast -= octavevigiltags
                    kal[match.date][i] = oldfeast
                else:
                    kal[match.date].remove(i)
                break
    # Automatically decide the suitable date whither the feast should be transferred
    def autotransfer(tags, mention, obstacles):
        match = kal.match_unique(tags)
        newfeast = copy.deepcopy(match.feast)
        newfeast.add("translatus")
        newdate = match.date
        while not kal.tagsindate(newdate).isdisjoint(obstacles):
            newdate = newdate + timedelta(days=1)

        kal.add_entry(newdate, newfeast)
        for i in range(0,len(kal[match.date])):
            if kal[match.date][i] >= tags:
                if mention:
                    oldfeast = copy.deepcopy(kal[match.date][i])
                    oldfeast.add("translatus-originalis")
                    oldfeast -= ranks
                    oldfeast -= octavevigiltags
                    kal[match.date][i] = oldfeast
                else:
                    kal[match.date].remove(i)
                break


    easter = pascha.geteaster(year)
    christmas = date(year, 12, 25)
    adventstart = christmas - timedelta(days = 22 + christmas.weekday())
    xxiiipentecost = easter + timedelta(days=210)
    xxivpentecost = adventstart - timedelta(days=7)

    epiphanysunday = sundayafter(date(year, 1, 6))

    psundayomission = False
    xxiiipentecostentry = set()
    esundayomission = False
    omittedepiphanyentry = set()

    # Advent Cycle
    for entry in adventcycle:
        entry = copy.deepcopy(entry)
        date0 = adventstart + timedelta(days=entry.pop("difference"))
        # Christmas Eve is its own liturgical day that outranks whatever Advent day it's on but most of Matins comes from the day so Advent count is only stopped at Christmas
        if date0 == christmas:
            break
        kal.add_entry(date0, entry["tags"])

    # Paschal Cycle
    for entry in paschalcycle:
        entry = copy.deepcopy(entry)
        date0 = easter + timedelta(days=entry.pop("difference"))
        if date0 == xxivpentecost:
            psundayomission = True
            xxiiipentecostentry = entry["tags"]
            break
        kal.add_entry(date0, entry["tags"])

    # Epiphany Sundays
    epiphanyweek = 0
    while epiphanysunday + timedelta(days=epiphanyweek * 7) != easter - timedelta(days=63):
        for i in range(0,7):
            kal.add_entry(epiphanysunday + timedelta(days=epiphanyweek * 7 + i), epiphanycycle[epiphanyweek][i]["tags"])
        epiphanyweek += 1
    for i in range(0, 6 - epiphanyweek):
        sunday = xxivpentecost - timedelta(days=7 * (i + 1))
        if sunday != xxiiipentecost:
            for j in range(0,7):
                kal.add_entry(sunday + timedelta(days=j), epiphanycycle[5 - i][j]["tags"])
        else:
            esundayomission = True
            omittedepiphanyentry = epiphanycycle[5 - i][0]["tags"]

    # Nativity & Epiphany
    for entry in nativitycycle:
        entry = copy.deepcopy(entry)
        date0 = todate(entry.pop("date"), year)
        kal.add_entry(date0, entry["tags"])
    kal.add_entry(christmas + timedelta(days=6-christmas.weekday()), movables["dominica-nativitatis"]["tags"])
    if date(year, 1, 6).weekday() == 6:
        transfer({"epiphania","dominica"}, date(year, 1, 12), True)
        epiphanysunday = date(year, 1, 12)

    currday = 2
    for i in range(0, 6):
        if not date(year, 1, 7 + i) == epiphanysunday:
            kal.add_entry(date(year, 1, 7 + i), {"epiphania","semiduplex","infra-octavam","dies-" + numerals[currday - 2].lower()})
            currday += 1
    kal.add_entry(date(year, 1, 13), {"epiphania","dies-octava","duplex"})

    # Autumnal Weeks
    def nearsunday(kalends):
        if kalends.weekday() < 3:
            return kalends - timedelta(days=1+kalends.weekday())
        else:
            return kalends + timedelta(days=6-kalends.weekday())
    for i in range(8, 11):
        kalends = nearsunday(date(year, i, 1))
        # Also works for November - December since Advent begins on the nearest Sunday to the Kalends of December
        nextkalends = nearsunday(date(year, i + 1, 1))
        month = months[["augustus","september","october","november"][i - 8]]
        j = 0
        while kalends + timedelta(days=j*7) != nextkalends:
            for k in range(0,7):
                kal.add_entry(kalends + timedelta(days=j*7+k), month[j][k]["tags"])
            j += 1
    kalends = nearsunday(date(year, 11, 1))
    # Also works for November - December since Advent begins on the nearest Sunday to the Kalends of December
    j = 0
    while kalends + timedelta(days=j*7) != adventstart:
        for k in range(0,7):
            kal.add_entry(kalends + timedelta(days=j*7+k), months["november"][j][k]["tags"])
        j += 1

    # Saints, and also handles leap years
    leapyear = year % 4 == 0 and (year % 400 == 0 or year % 100 != 0)
    for i in sanctoral:
        date0 = todate(i, year)
        if leapyear and date0.month == 2 and date0.day > 23:
            date0 = date0 + timedelta(days=1)
        for j in sanctoral[i]:
            kal.add_entry(date0, set(j))

    # List of inferred feasts that get merged in later
    buffer = Kalendar(year=year)

    # Movable feasts with occurrence attribute
    for i, movable in movables.items():
        movable = copy.deepcopy(movable)
        if "occurrence" in movable:
            matches = kal.match(movable.pop("occurrence"))
            if "excluded" in movable:
                excluded = movable.pop("excluded")
                matches = (j for j in matches if j.feast.isdisjoint(excluded))
            for match in matches:
                buffer.add_entry(match.date, movable["tags"])

    kal |= buffer
    buffer.kal.clear()

    # Irregular movables
    assumption = date(year, 8, 15)
    if assumption.weekday() == 6:
        kal.add_entry(assumption + timedelta(days=1), movables["joachim"]["tags"])
    else:
        kal.add_entry(assumption + timedelta(days=6-assumption.weekday()), movables["joachim"]["tags"])
    # First Sunday of July
    kal.add_entry(nearsunday(date(year,7,1)), movables["pretiosissimi-sanguinis"]["tags"])
    assumption = date(year, 9, 8)
    if assumption.weekday() == 6:
        kal.add_entry(assumption + timedelta(days=1), movables["nominis-bmv"]["tags"])
    else:
        kal.add_entry(assumption + timedelta(days=6-assumption.weekday()), movables["nominis-bmv"]["tags"])

    # Octave and Vigil Processing
    for i, entries in kal.items():
        for entry in entries:
            if "habens-octavam" in entry and not "octava-excepta" in entry:
                for k in range(1,7):
                    date0 = i + timedelta(days=k)
                    if "quadragesima" in kal.tagsindate(date0):
                        break
                    entrystripped = copy.deepcopy(entry)
                    entrystripped -= octavevigiltags
                    entrystripped -= ranks
                    entrystripped |= {"semiduplex","infra-octavam","dies-" + numerals[k - 1].lower()}
                    #If a certain day within an Octave is manually entered, do not create one automatically
                    if kal.match_unique(entrystripped, none_ok=True) == None:
                        buffer.add_entry(date0, entrystripped)
                date0 = i + timedelta(days=7)
                if "quadragesima" in kal.tagsindate(date0):
                    continue
                entrystripped = copy.deepcopy(entry)
                entrystripped -= octavevigiltags
                entrystripped -= ranks
                entrystripped |= {"duplex", "dies-octava"}
                #If a certain day within an Octave is manually entered, do not create one automatically
                if kal.match_unique(entrystripped, none_ok=True) == None:
                    buffer.add_entry(date0, entrystripped)
            if "habens-vigiliam" in entry and not "vigilia-excepta" in entry:
                entrystripped = copy.deepcopy(entry)
                entrystripped -= octavevigiltags
                entrystripped -= ranks
                entrystripped |= {"vigilia","poenitentialis","feria"}
                buffer.add_entry(i - timedelta(days=1), entrystripped)

    kal |= buffer
    buffer.kal.clear()

    # 23rd Sunday Pentecost, 5th Sunday Epiphany Saturday transfer
    if psundayomission:
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
    if esundayomission:
        omittedepiphanyentry.add("translatus")
        septuagesima = easter - timedelta(days=63)
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
    sjb = kal.match_unique({"nativitas-joannis-baptistae","duplex-i-classis"})
    corpuschristi = kal.match_unique({"corpus-christi","duplex-i-classis"})
    # Although Candlemas does not have an Octave, I added the "duplex-ii-classis" search tag in case a local Kalendar were to assign it an Octave.
    candlemas = kal.match_unique({"purificatio","duplex-ii-classis"})
    # N.B. Despite the Feast of the Nativity of S.J.B. being translated, its Octave is not adjusted with it, but still is based off the 24th of June.
    if sjb.date == corpuschristi.date:
        transfer({"nativitas-joannis-baptistae","duplex-i-classis"}, date(year, 6, 25), True)
    # Candlemas is granted the special privilege of being transferred to the next Monday if impeded by a Sunday II Class, regardless of the feast which falls on that Monday. It is thus included in the exceptions list.
    if candlemas.date in (i.date for i in kal.match({"dominica-ii-classis"})):
        transfer({"purificatio","duplex-ii-classis"}, candlemas.date + timedelta(days=1), True)

    excepted = {"dominica-i-classis","dominica-ii-classis","pascha","pentecostes","ascensio","corpus-christi","purificatio","non-translandus","dies-octava","epiphania"}

    def transfer_all(target, obstacles):
        for i in kal.match(target):
            if not i.feast.isdisjoint(excepted):
                continue
            for j in kal[i.date]:
                if not j.isdisjoint(obstacles):
                    autotransfer(i.feast, True, obstacles)
    obstacles = {"dominica-i-classis","dominica-ii-classis","non-concurrentia","epiphania"}

    if christmas + timedelta(days=6-christmas.weekday()) != date(year, 12, 29):
        # All days of Christmas Octave (or any Octave for that matter) are semiduplex which is why I used the thomas-becket tag specifically
        autotransfer({"nativitas","dominica-infra-octavam"}, True, {"duplex-i-classis","duplex-ii-classis","thomas-becket"})
    else:
        transfer({"thomas-becket"}, date(year, 12, 29), True)
    transfer_all({"duplex-i-classis"}, obstacles)
    obstacles |= {"duplex-i-classis"}
    transfer_all({"duplex-ii-classis"}, obstacles)
    obstacles |= {"duplex-ii-classis","dies-octava"}
    transfer_all({"duplex-majus"}, obstacles)
    obstacles |= {"duplex-majus"}
    transfer_all({"doctor","duplex"}, obstacles)

    for i in kal.match({"vigilia"}):
        if "non-translandus" in i.feast:
            continue
        if "dominica" in kal.tagsindate(i.date):
            transfer(i.feast, i.date - timedelta(days=1), True)

    fidelesdefuncti = kal.match_unique({"fideles-defuncti"})
    if "dominica" in kal.tagsindate(fidelesdefuncti.date):
        transfer({"fideles-defuncti"}, fidelesdefuncti.date + timedelta(days=1), True)

    return kal


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Liturgical calendar generator",
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

    # Generate kalendar
    ret = dict(sorted(kalendar(args.year).items()))

    # Convert datestrings to strings and sets into list
    ret = {str(k): [list(ent) for ent in v] for k, v in ret.items()}
    # Write JSON output
    args.output.write(json.dumps(ret) + "\n")
