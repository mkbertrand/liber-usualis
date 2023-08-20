#!/usr/bin/env python3

from collections import defaultdict
from datetime import datetime
from datetime import date
from datetime import timedelta
import pathlib
import json
import copy
from kalendar import pascha


data_root = pathlib.Path(__file__).parent.joinpath("data")

def load_data(p):
    return json.loads(data_root.joinpath(p).read_text(encoding="utf-8"))

epiphanycycle = load_data('epiphany.json')
paschalcycle = load_data('paschal.json')
adventcycle = load_data('advent.json')
nativitycycle = load_data('nativity.json')
movables = load_data('movables.json')
months = load_data('summer-autumn.json')
sanctoral = load_data('kalendar.json')

ranks = ["feria","commemoratio","simplex","semiduplex","duplex","duplex-majus","duplex-ii-classis","duplex-i-classis"]
octavevigiltags = ["habens-octavam","has-special-octave","habens-vigiliam","vigilia-excepta","date"]
numerals = ['II','III','IV','V','VI','VII']


class SearchResult:
    def __init__(self, date, feast):
        self.date = date
        self.feast = feast

    def __str__(self):
        return str(self.date) + ":" + str(self.feast)


def datestring(date0):
    return str(date0.month).zfill(2) + '-' + str(date0.day).zfill(2)


def kalendar(year):
    kal = defaultdict(list)

    def all_tags(tags):
        ret = []
        for date0, entries in kal.items():
            for entry in entries:
                if all(k in entry["tags"] for k in tags):
                    ret.append(SearchResult(date0, entry))
        return ret

    def unique_search(tags):
        for date0, entries in kal.items():
            for entry in entries:
                if all(k in entry["tags"] for k in tags):
                    return SearchResult(date0, entry)
        return None

    def tagsindate(date0):
        ret = set()
        if not date0 in kal:
            return ret
        for entry in kal[date0]:
            ret.update(entry["tags"])
        return ret

    def sundayafter(date0):
        return date0 + timedelta(days=6-date0.weekday()) if date0.weekday() != 6 else date0 + timedelta(days=7)
    def todate(text, year0):
        return date(year0, int(text[:2]), int(text[3:]))
    def addentry(date0, entry):
        entry["tags"] = set(entry["tags"])
        kal[date0].append(entry)

    # Will not work as intended if multiple matches are found for the tags
    # If match is False there will be no mention that there was a feast in the original pre-tranfer date
    def transfer(tags, target, mention):
        match = unique_search(tags)
        newfeast = copy.deepcopy(match.feast)
        newfeast["tags"].add("translatus")
        addentry(target, newfeast)
        for i in range(0,len(kal[match.date])):
            if all(j in kal[match.date][i]["tags"] for j in tags):
                if mention:
                    oldfeast = copy.deepcopy(kal[match.date][i])
                    oldfeast["tags"].add("translatus-originalis")

                    oldfeast["tags"] = [item for item in oldfeast["tags"] if not item in ranks and not item in octavevigiltags]
                    kal[match.date][i] = oldfeast
                else:
                    kal[match.date].remove(i)
                break
    # Automatically decide the suitable date whither the feast should be transferred
    def autotransfer(tags, mention, obstacles):
        match = unique_search(tags)
        newfeast = copy.deepcopy(match.feast)
        newfeast["tags"].add("translatus")
        newdate = match.date
        def issuitable(date0):
            for entry in kal[date0]:
                if any(j in entry["tags"] for j in obstacles):
                    return False
            return True
        while not issuitable(newdate):
            newdate = newdate + timedelta(days=1)

        addentry(newdate, newfeast)
        for i in range(0,len(kal[match.date])):
            if all(j in kal[match.date][i]["tags"] for j in tags):
                if mention:
                    oldfeast = copy.deepcopy(kal[match.date][i])
                    oldfeast["tags"].add("translatus-originalis")
                    for j in ranks:
                        oldfeast["tags"].discard(j)
                    for j in octavevigiltags:
                        oldfeast["tags"].discard(j)
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
    xxiiipentecostentry = {}
    esundayomission = False
    omittedepiphanyentry = {}

    # Advent Cycle
    for entry in adventcycle:
        date0 = adventstart + timedelta(days=entry["difference"])
        # Christmas Eve is its own liturgical day that outranks whatever Advent day it's on but most of Matins comes from the day so Advent count is only stopped at Christmas
        if date0 == christmas:
            break
        del entry["difference"]
        addentry(date0, entry)

    # Paschal Cycle
    for entry in paschalcycle:
        date0 = easter + timedelta(days=entry["difference"])
        del entry["difference"]
        if date0 == xxivpentecost:
            psundayomission = True
            xxiiipentecostentry = entry
            xxiiipentecostentry["tags"] = set(xxiiipentecostentry["tags"])
            break
        addentry(date0, entry)

    # Epiphany Sundays
    epiphanyweek = 0
    while epiphanysunday + timedelta(days=epiphanyweek * 7) != easter - timedelta(days=63):
        for i in range(0,7):
            addentry(epiphanysunday + timedelta(days=epiphanyweek * 7 + i), epiphanycycle[epiphanyweek][i])
        epiphanyweek += 1
    for i in range(0, 6 - epiphanyweek):
        sunday = xxivpentecost - timedelta(days=7 * (i + 1))
        if sunday != xxiiipentecost:
            for j in range(0,7):
                addentry(sunday + timedelta(days=j), epiphanycycle[5 - i][j])
        else:
            esundayomission = True
            omittedepiphanyentry = epiphanycycle[5 - i][0]
            omittedepiphanyentry["tags"] = set(omittedepiphanyentry["tags"])

    # Nativity & Epiphany
    for entry in nativitycycle:
        date0 = todate(entry["date"], year)
        del entry["date"]
        addentry(date0, entry)
    addentry(christmas + timedelta(days=6-christmas.weekday()), movables["dominica-nativitatis"])
    if date(year, 1, 6).weekday() == 6:
        transfer(["epiphania","dominica"], date(year, 1, 12), True)
        epiphanysunday = date(year, 1, 12)

    currday = 2
    for i in range(0, 6):
        if not date(year, 1, 7 + i) == epiphanysunday:
            addentry(date(year, 1, 7 + i), {"day":"Dies " + numerals[currday - 2] + " infra Octavam Epiphaniæ","tags":{"epiphania","semiduplex","infra-octavam","dies-" + numerals[currday - 2].lower()}})
            currday += 1
    addentry(date(year, 1, 13), {"day":"Octava Epiphaniæ","tags":{"epiphania","dies-octava","duplex"}})

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
                addentry(kalends + timedelta(days=j*7+k), month[j][k])
            j += 1
    kalends = nearsunday(date(year, 11, 1))
    # Also works for November - December since Advent begins on the nearest Sunday to the Kalends of December
    j = 0
    while kalends + timedelta(days=j*7) != adventstart:
        for k in range(0,7):
            addentry(kalends + timedelta(days=j*7+k), months["november"][j][k])
        j += 1

    # Saints, and also handles leap years
    if year % 4 == 0 and (year % 400 == 0 or year % 100 != 0):
        for entry in sanctoral:
            date0 = todate(entry["date"], year)
            del entry["date"]
            if date0.month == 2 and date0.day > 23:
                addentry(date0 + timedelta(days=1), entry)
            else:
                addentry(date0, entry)
    else:
        for entry in sanctoral:
            date0 = todate(entry["date"], year)
            del entry["date"]
            addentry(date0, entry)

    buffer = defaultdict(list)
    def addbufferentry(date0, entry):
        buffer[date0].append(entry)

    # Movable feasts with occurrence attribute
    for i, movable in movables.items():
        if "occurrence" in movable:
            matches = all_tags(movable["occurrence"])
            if "excluded" in movable:
                excluded = movable.pop("excluded")
                matches = (j for j in matches if not any(k in j.feast["tags"] for k in excluded))
            movables[i].pop("occurrence")
            for match in matches:
                addentry(match.date, movable)

    # Irregular movables
    assumption = date(year, 8, 15)
    if assumption.weekday() == 6:
        addentry(assumption + timedelta(days=1), movables["joachim"])
    else:
        addentry(assumption + timedelta(days=6-assumption.weekday()), movables["joachim"])
    # First Sunday of July
    addentry(nearsunday(date(year,7,1)), movables["pretiosissimi-sanguinis"])
    assumption = date(year, 9, 8)
    if assumption.weekday() == 6:
        addentry(assumption + timedelta(days=1), movables["nominis-bmv"])
    else:
        addentry(assumption + timedelta(days=6-assumption.weekday()), movables["nominis-bmv"])

    # Octave and Vigil Processing
    for i, entries in kal.items():
        for entry in entries:
            if "habens-octavam" in entry["tags"] and not "octava-excepta" in entry["tags"]:
                for k in range(1,7):
                    date0 = i + timedelta(days=k)
                    if "quadragesima" in tagsindate(date0):
                        break
                    entrystripped = copy.deepcopy(entry)
                    for l in octavevigiltags:
                        entrystripped["tags"].discard(l)
                    for l in ranks:
                        entrystripped["tags"].discard(l)
                    entrystripped["tags"].update(["semiduplex","infra-octavam","dies-" + numerals[k - 1].lower()])
                    entrystripped["day"] = "Dies " + numerals[k - 1] + " infra Octavam " + entrystripped["genitive-day"]
                    del entrystripped["genitive-day"]
                    addbufferentry(date0, entrystripped)
                date0 = i + timedelta(days=7)
                if "quadragesima" in tagsindate(date0):
                    continue
                entrystripped = copy.deepcopy(entry)
                for l in octavevigiltags:
                    entrystripped["tags"].discard(l)
                for l in ranks:
                    entrystripped["tags"].discard(l)
                entrystripped["tags"].add("duplex")
                entrystripped["tags"].add("dies-octava")
                entrystripped["day"] = "In Octava " + entrystripped["genitive-day"]
                del entrystripped["genitive-day"]
                addbufferentry(date0, entrystripped)
            if "habens-vigiliam" in entry["tags"] and not "vigilia-excepta" in entry["tags"]:
                entrystripped = copy.deepcopy(entry)
                for l in octavevigiltags:
                    entrystripped["tags"].discard(l)
                for l in ranks:
                    entrystripped["tags"].discard(l)
                entrystripped["tags"].update(["vigilia","poenitentialis","feria"])
                entrystripped["day"] = "Vigilia " + entrystripped["genitive-day"]
                del entrystripped["genitive-day"]
                addbufferentry(i - timedelta(days=1), entrystripped)

    for date0, entries in buffer.items():
        kal[date0] += entries

    # 23rd Sunday Pentecost, 5th Sunday Epiphany Saturday transfer
    if psundayomission:
        xxiiipentecostentry["tags"].add("translatus")
        i = 1
        while i < 7:
            if not any(any(j in i["tags"] for j in ranks[3:]) for i in kal[xxivpentecost - timedelta(days=i)]):
                addentry(xxivpentecost - timedelta(days=i), xxiiipentecostentry)
                break
            else:
                i += 1
        if i == 7:
            xxiiipentecostentry["tags"].add("commemoratio")
            xxiiipentecostentry["tags"].add("translatus")
            addentry(xxivpentecost - timedelta(days=1), xxiiipentecostentry)
    if esundayomission:
        omittedepiphanyentry["tags"].add("translatus")
        septuagesima = easter - timedelta(days=63)
        i = 1
        while i < 7:
            if not any(any(j in i["tags"] for j in ranks[3:]) for i in kal[septuagesima - timedelta(days=i)]):
                addentry(septuagesima - timedelta(days=i), omittedepiphanyentry)
                break
            else:
                i += 1
        if i == 7:
            omittedepiphanyentry["tags"].add("commemoratio")
            omittedepiphanyentry["tags"].add("translatus")
            addentry(septuagesima - timedelta(days=1), omittedepiphanyentry)

    # Transfers
    sjb = unique_search(["nativitas-joannis-baptistae","duplex-i-classis"])
    corpuschristi = unique_search(["corpus-christi","duplex-i-classis"])
    # Although Candlemas does not have an Octave, I added the "duplex-ii-classis" search tag in case a local Kalendar were to assign it an Octave.
    candlemas = unique_search(["purificatio","duplex-ii-classis"])
    # N.B. Despite the Feast of the Nativity of S.J.B. being translated, its Octave is not adjusted with it, but still is based off the 24th of June.
    if sjb.date == corpuschristi.date:
        transfer(["nativitas-joannis-baptistae","duplex-i-classis"], date(year, 6, 25), True)
    # Candlemas is granted the special privilege of being transferred to the next Monday if impeded by a Sunday II Class, regardless of the feast which falls on that Monday. It is thus included in the exceptions list.
    if candlemas.date in (i.date for i in all_tags(["dominica-ii-classis"])):
        transfer(["purificatio","duplex-ii-classis"], candlemas.date + timedelta(days=1), True)

    excepted = ["dominica-i-classis","dominica-ii-classis","pascha","pentecostes","ascensio","corpus-christi","purificatio","non-translandus","dies-octava","epiphania"]

    def transfer_all(target, obstacles):
        for i in all_tags(target):
            if any(j in i.feast["tags"] for j in excepted):
                continue
            for j in kal[i.date]:
                if any(k in j["tags"] for k in obstacles):
                    autotransfer(i.feast["tags"], True, obstacles)
    obstacles = ["dominica-i-classis","dominica-ii-classis","non-concurrentia","epiphania"]

    if christmas + timedelta(days=6-christmas.weekday()) != date(year, 12, 29):
        # All days of Christmas Octave (or any Octave for that matter) are semiduplex which is why I used the thomas-becket tag specifically
        autotransfer(["nativitas","dominica-infra-octavam"], True, ["duplex-i-classis","duplex-ii-classis","thomas-becket"])
    else:
        transfer(["thomas-becket"], date(year, 12, 29), True)
    transfer_all(["duplex-i-classis"], obstacles)
    obstacles.append("duplex-i-classis")
    transfer_all(["duplex-ii-classis"], obstacles)
    obstacles.extend(["duplex-ii-classis","dies-octava"])
    transfer_all(["duplex-majus"], obstacles)
    obstacles.append("duplex-majus")
    transfer_all(["doctor","duplex"], obstacles)

    for i in all_tags(["vigilia"]):
        if "non-translandus" in i.feast["tags"]:
            continue
        if "dominica" in tagsindate(i.date):
            transfer(i.feast["tags"], i.date - timedelta(days=1), True)

    fidelesdefuncti = unique_search(["fideles-defuncti"])
    if "dominica" in tagsindate(fidelesdefuncti.date):
        transfer(["fideles-defuncti"], fidelesdefuncti.date + timedelta(days=1), True)

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

    # Convert datestrings to strings
    ret = {str(k): v for k, v in ret.items()}
    # Convert tag set into list
    for i in ret:
        for j in ret[i]:
            j["tags"] = list(j["tags"])
    # Write JSON output
    args.output.write(json.dumps(ret) + "\n")
