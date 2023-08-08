from datetime import datetime
from datetime import date
from datetime import timedelta
import math
import pathlib
import html.entities
import json
import copy
import pascha

epiphanycycle = json.loads(''.join(open(str(pathlib.Path(__file__).parent.absolute()) + '\\data\\epiphany.json', 'r', encoding = ' utf-8').readlines()))
paschalcycle = json.loads(''.join(open(str(pathlib.Path(__file__).parent.absolute()) + '\\data\\paschal.json', 'r', encoding = ' utf-8').readlines()))
adventcycle = json.loads(''.join(open(str(pathlib.Path(__file__).parent.absolute()) + '\\data\\advent.json', 'r', encoding = ' utf-8').readlines()))
nativitycycle = json.loads(''.join(open(str(pathlib.Path(__file__).parent.absolute()) + '\\data\\nativity.json', 'r', encoding = ' utf-8').readlines()))
movables = json.loads(''.join(open(str(pathlib.Path(__file__).parent.absolute()) + '\\data\\movables.json', 'r', encoding = ' utf-8').readlines()))
months = json.loads(''.join(open(str(pathlib.Path(__file__).parent.absolute()) + '\\data\\summer-autumn.json', 'r', encoding = ' utf-8').readlines()))
sanctoral = json.loads(''.join(open(str(pathlib.Path(__file__).parent.absolute()) + '\\data\\kalendar.json', 'r', encoding = ' utf-8').readlines()))

def datestring(date0):
    return str(date0.month).zfill(2) + '-' + str(date0.day).zfill(2)

def kalendar(year):
    leapyear = year % 4 == 0 and (year % 400 == 0 or year % 100 != 0)
    kal = {}
    
    def sundayafter(date0):
        return date0 + timedelta(days=6-date0.weekday()) if date0.weekday() != 6 else date0 + timedelta(days=6)
    def todate(text):
        return date(year, int(text[:2]), int(text[3:]))
    def addentry(date0, entry):
        if "octave" in entry["tags"] and not "special-octave" in entry["tags"]:
            for k in range(1,7):
                entrystripped = copy.deepcopy(entry)
                entrystripped["tags"].remove("octave")
                if ("double-i-class" in entrystripped["tags"]):
                    entrystripped["tags"].remove("double-i-class")
                elif ("double-ii-class" in entrystripped["tags"]):
                    entrystripped["tags"].remove("double-ii-class")
                entrystripped["tags"].append("semidouble")
                entrystripped["tags"].append("day-" + str(k+1))
                print(entrystripped)
                addentry(date0 + timedelta(days=k), entrystripped)
        if (date0 in kal):
            kal[date0].append(entry)
        else:
            kal[date0] = [entry]
    
    easter = pascha.geteaster(year)
    christmas = date(year, 12, 25)
    adventstart = christmas - timedelta(days = 22 + christmas.weekday())
    xxiiipentecost = easter + timedelta(days=210)
    xxivpentecost = adventstart - timedelta(days=7)
    
    epiphanysunday = sundayafter(date(year, 1, 6))
    
    psundayomission = False
    esundayomission = False
    
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
        if (date0 == xxivpentecost):
            psundayomission = True
            break
        del entry["difference"]
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

    #Nativity & Epiphany
    for i in nativitycycle:
        addentry(todate(i["date"]), i)
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
        addentry(todate(i["date"]), i)
        
    return dict(sorted(kal.items()))

year = 2023
ret = kalendar(year)
ret0 = {}

for i in ret:
    ret0[datestring(i)] = ret[i]

outputfilename = 'year-' + str(year) + '.json'
with open('kalendars\\' + outputfilename, 'w') as fp:
    fp.write(json.dumps(ret0))
print(outputfilename)