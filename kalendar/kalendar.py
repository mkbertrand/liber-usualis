from datetime import datetime
from datetime import date
from datetime import timedelta
import math
import pathlib
import html.entities
import json
import copy
from kalendar import pascha

epiphanycycle = json.loads(''.join(open(str(pathlib.Path(__file__).parent.absolute()) + '/data/epiphany.json', 'r', encoding = ' utf-8').readlines()))
paschalcycle = json.loads(''.join(open(str(pathlib.Path(__file__).parent.absolute()) + '/data/paschal.json', 'r', encoding = ' utf-8').readlines()))
adventcycle = json.loads(''.join(open(str(pathlib.Path(__file__).parent.absolute()) + '/data/advent.json', 'r', encoding = ' utf-8').readlines()))
nativitycycle = json.loads(''.join(open(str(pathlib.Path(__file__).parent.absolute()) + '/data/nativity.json', 'r', encoding = ' utf-8').readlines()))
movables = json.loads(''.join(open(str(pathlib.Path(__file__).parent.absolute()) + '/data/movables.json', 'r', encoding = ' utf-8').readlines()))
months = json.loads(''.join(open(str(pathlib.Path(__file__).parent.absolute()) + '/data/summer-autumn.json', 'r', encoding = ' utf-8').readlines()))
sanctoral = json.loads(''.join(open(str(pathlib.Path(__file__).parent.absolute()) + '/data/kalendar.json', 'r', encoding = ' utf-8').readlines()))

ranks = ["ferial","simple","semidouble","double","greater-double","double-ii-class","double-i-class"]

class SearchResult:
    def __init__(self, date, feast):
        self.date = date
        self.feast = feast
    def __str__(self):
        return str(self.date) + ":" + str(self.feast)

def datestring(date0):
    return str(date0.month).zfill(2) + '-' + str(date0.day).zfill(2)

def matches(kal, condition):
    ret = []
    for i in kal:
        for j in kal[i]:
            if condition(j["tags"]):
                ret.append(SearchResult(i, j))
    return ret

def all_tags(kal,tags):
    ret = []
    for i in kal:
        for j in kal[i]:
            if all(k in j["tags"] for k in tags):
                ret.append(SearchResult(i, j))
    return ret

def unique_search(kal,tags):
    for i in kal:
        for j in kal[i]:
            if all(k in j["tags"] for k in tags):
                return SearchResult(i, j)
    return None

def kalendar(year):
    leapyear = year % 4 == 0 and (year % 400 == 0 or year % 100 != 0)
    kal = {}
    
    def sundayafter(date0):
        return date0 + timedelta(days=6-date0.weekday()) if date0.weekday() != 6 else date0 + timedelta(days=6)
    def todate(text, year0):
        return date(year0, int(text[:2]), int(text[3:]))
    def addentry(date0, entry):
        if (date0 in kal):
            kal[date0].append(entry)
        else:
            kal[date0] = [entry]
    #Will not work as intended if multiple matches are found for the tags
    #If match is False there will be no mention that there was a feast in the original pre-tranfer date
    def transfer(tags, target, mention):
        match = unique_search(kal,tags)
        newfeast = copy.deepcopy(match.feast)
        newfeast["tags"].append("transfer")
        addentry(target, newfeast)
        for i in range(0,len(kal[match.date])):
            if all(j in kal[match.date][i]["tags"] for j in tags):
                if (mention):
                    oldfeast = copy.deepcopy(kal[match.date][i])
                    oldfeast["tags"].append("transfer-original")
                    oldfeast["tags"] = list(filter(lambda item:(not item in ranks and not item in octavevigiltags), oldfeast["tags"]))
                    kal[match.date] = oldfeast
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
    
    #Advent Cycle
    for i in adventcycle:
        entry = i
        date0 = adventstart + timedelta(days=i["difference"])
        #Christmas Eve is its own liturgical day that outranks whatever Advent day it's on but most of Matins comes from the day so Advent count is only stopped at Christmas
        if (date0 == christmas):
            break
        del entry["difference"]
        #entry["date"] = datestring(date0)
        addentry(date0, entry)
    
    #Paschal Cycle
    for i in paschalcycle:
        entry = i
        date0 = easter + timedelta(days=i["difference"])
        del entry["difference"]
        if (date0 == xxivpentecost):
            psundayomission = True
            xxiiipentecostentry = entry
            break
        #entry["date"] = datestring(date0)
        addentry(date0, entry)
    
    #Epiphany Sundays 
    epiphanyweek = 0
    while epiphanysunday + timedelta(days=epiphanyweek * 7) != easter - timedelta(days=63):
        for i in range(0,7):
            addentry(epiphanysunday + timedelta(days=epiphanyweek * 7 + i), epiphanycycle[epiphanyweek][i])
        epiphanyweek += 1
    for i in range(0, 6 - epiphanyweek):
        sunday = xxivpentecost - timedelta(days=7 * (i + 1))
        if (sunday != xxiiipentecost):
            for j in range(0,7):
                addentry(sunday + timedelta(days=j), epiphanycycle[5 - i][j])
        else:
            esundayomission = True
            omittedepiphanyentry = epiphanycycle[5 - i][j]

    #Nativity & Epiphany
    for i in nativitycycle:
        addentry(todate(i["date"], year), i)
    if (christmas.weekday() < 3):
        addentry(christmas + timedelta(days=6-christmas.weekday()), movables["nativity-sunday"])
    else:
        addentry(date(year, 12, 30), movables["nativity-sunday"])
    if (christmas.weekday() == 2):
        addentry(date(year, 12, 30), movables["thomas-becket"])
    else:
        addentry(date(year, 12, 29), movables["thomas-becket"])
     
    #Autumnal Weeks
    def nearsunday(kalends):
        if(kalends.weekday() < 3):
            return kalends - timedelta(days=1+kalends.weekday())
        else:
            return kalends + timedelta(days=6-kalends.weekday())
    for i in range(8, 12):
        kalends = nearsunday(date(year, i, 1))
        #Also works for November - December since Advent begins on the nearest Sunday to the Kalends of December
        nextkalends = nearsunday(date(year, i + 1, 1))
        month = months[["august","september","october","november"][i - 8]]
        j = 0
        while kalends + timedelta(days=j*7) != nextkalends:
            for k in range(0,7):
                addentry(kalends + timedelta(days=j*7+k), month[j][k])
            j+=1
    
    #Saints
    for i in sanctoral:
        addentry(todate(i["date"], year), i)
    
    buffer = {}
    def addbufferentry(date0, entry):
        if (date0 in buffer):
            buffer[date0].append(entry)
        else:
            buffer[date0] = [entry]
    
    #Movable feasts with occurrence attribute
    for i in movables:
        if "occurrence" in movables[i].keys():
            match = unique_search(kal, movables[i]["occurrence"])
            addentry(match.date,movables[i])
    
    #Octave and Vigil Processing
    octavevigiltags = ["has-octave","has-special-octave","has-vigil","has-special-vigil"]
    numerals = ['II','III','IV','V','VI','VII']
    for i in kal:
        for j in kal[i]:
            if "has-octave" in j["tags"] and not "has-special-octave" in j["tags"]:
                for k in range(1,7):
                    entrystripped = copy.deepcopy(j)
                    entrystripped["tags"] = list(filter(lambda item:(not item in ranks and not item in octavevigiltags), entrystripped["tags"]))
                    entrystripped["tags"].append("semidouble")
                    entrystripped["tags"].append("day-" + str(k+1))
                    entrystripped["date"] = datestring(i + timedelta(days=k))
                    entrystripped["day"] = "Dies " + numerals[k - 1] + " infra Octavam " + entrystripped["genitive-day"]
                    del entrystripped["genitive-day"]
                    addbufferentry(i + timedelta(days=k), entrystripped)
                entrystripped = copy.deepcopy(j)
                entrystripped["tags"] = list(filter(lambda item:(not item in ranks and not item in octavevigiltags), entrystripped["tags"]))
                entrystripped["tags"].append("double")
                entrystripped["tags"].append("octave-day")
                entrystripped["date"] = datestring(i + timedelta(days=7))
                entrystripped["day"] = "In Octava " + entrystripped["genitive-day"]
                del entrystripped["genitive-day"]
                addbufferentry(i + timedelta(days=7), entrystripped)
            if "has-vigil" in j["tags"] and not "has-special-vigil" in j["tags"]:
                entrystripped = copy.deepcopy(j)
                entrystripped["tags"] = list(filter(lambda item:(not item in ranks and not item in octavevigiltags), entrystripped["tags"]))
                entrystripped["tags"].extend(["vigil","penitential","ferial"])
                entrystripped["date"] = datestring(i - timedelta(days=1))
                entrystripped["day"] = "Vigilia " + entrystripped["genitive-day"]
                del entrystripped["genitive-day"]
                addbufferentry(i - timedelta(days=1), entrystripped)
    
    for i in buffer:
        for j in buffer[i]:
            addentry(i, j)
    
    #23rd Sunday Pentecost, 5th Sunday Epiphany Saturday transfer
    if psundayomission:
        xxiiipentecostentry["tags"].append("transfer")
        i = 1
        while i < 7:
            if (not any(any(j in i["tags"] for j in ranks[2:]) for i in kal[xxivpentecost - timedelta(days=i)])):
                addentry(xxivpentecost - timedelta(days=i), xxiiipentecostentry)
                break
            else:
                i += 1
        if (i == 7):
            xxiiipentecostentry["tags"].append("commemoration")
            addentry(xxivpentecost - timedelta(days=1), xxiiipentecostentry)
    if esundayomission:
        omittedepiphanyentry["tags"].append("transfer")
        septuagesima = easter - timedelta(days=63)
        i = 1
        while i < 7:
            if (not any(any(j in i["tags"] for j in ranks[2:]) for i in kal[septuagesima - timedelta(days=i)])):
                addentry(septuagesima - timedelta(days=i), omittedepiphanyentry)
                break
            else:
                i += 1
        if (i == 7):
            omittedepiphanyentry["tags"].append("commemoration")
            addentry(septuagesima - timedelta(days=1), omittedepiphanyentry)
    
    #Transfers
    sjb = unique_search(kal, ["nativitas-joannis-baptistae","double-i-class"])
    corpuschristi = unique_search(kal, ["corpus-christi","double-i-class"])
    #N.B. Despite the Feast of the Nativity of S.J.B. being translated, its Octave is not adjusted with it, but still is based off the 24th of June.
    if sjb.date == corpuschristi.date:
        transfer(["nativitas-joannis-baptistae","double-i-class"], date(year, 6, 25), True)
        
    #todo Finish kalendar.json, pascha.json
    #todo Translation Processing
    
    return kal.items()