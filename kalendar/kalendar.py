from datetime import datetime
from datetime import date
from datetime import timedelta
import math
import pathlib
import html.entities
import json

def getnumerals(num):
    res = ''
    while (num >= 10):
        res += 'X'
        num -= 10
    
    return res + { 0:'', 1:'I', 2:'II', 3:'III', 4:'IV', 5:'V', 6:'VI', 7:'VII', 8:'VIII', 9:'IX' }.get(num, 'ERROR')

def abmnumber(num):
    return { 3:'tertio', 4:'quarto', 5:'quinto', 6:'sexto', 7:'septimo', 8:'octavo', 9:'nono', 10:'decimo', 11:'undecimo', 12:'duodecimo', 13:'tertiodecimo', 14: 'quarto decimo', 15:'quinto decimo', 16:'sexto decimo', 17:'decimo septimo', 18:'decimo octavo', 19:'decimo nono'}.get(num, 'ERROR')  

def abfnumber(num):
    return { 1:'prima', 2:'secunda', 3:'tertia', 4:'quarta', 5:'quinta', 6:'sexta', 7:'septima', 8:'octava', 9:'nona', 10:'decima', 11:'undecima', 12:'duodecima', 13:'tertiadecima', 14: 'quarta decima', 15:'quinta decima', 16:'sexta decima', 17:'decima septima', 18:'duodevicesima', 19:'undevicesima', 20:'vicesima', 21:'vicesima prima', 22:'vicesima secunda', 23:'vicesima tertia', 24:'vicesima quarta', 25:'vicesima quinta', 26:'vicesima sexta', 27:'vicesima septima', 28:'vicesima octava', 29:'vicesima nona', 30:'tricesima'}.get(num, 'ERROR')  

def get_wide_ordinal(char):
    if len(char) != 2:
        return ord(char)
    return 0x10000 + (ord(char[0]) - 0xD800) * 0x400 + (ord(char[1]) - 0xDC00)

table = {get_wide_ordinal(v): '&{}'.format(k) for k, v in html.entities.html5.items()}

epiphanycycle = json.loads(''.join(open(str(pathlib.Path(__file__).parent.absolute()) + '\\data\\epiphany.json', 'r', encoding = ' utf-8').readlines()))
paschalcycle = json.loads(''.join(open(str(pathlib.Path(__file__).parent.absolute()) + '\\data\\paschal.json', 'r', encoding = ' utf-8').readlines()))
adventcycle = json.loads(''.join(open(str(pathlib.Path(__file__).parent.absolute()) + '\\data\\advent.json', 'r', encoding = ' utf-8').readlines()))
nativitycycle = json.loads(''.join(open(str(pathlib.Path(__file__).parent.absolute()) + '\\data\\nativity.json', 'r', encoding = ' utf-8').readlines()))
movables = json.loads(''.join(open(str(pathlib.Path(__file__).parent.absolute()) + '\\data\\movables.json', 'r', encoding = ' utf-8').readlines()))
months = json.loads(''.join(open(str(pathlib.Path(__file__).parent.absolute()) + '\\data\\summer-autumn.json', 'r', encoding = ' utf-8').readlines()))


nativitytable = ''.join(open(str(pathlib.Path(__file__).parent.absolute()) + '\\nativity.txt', 'r', encoding = ' utf-8').readlines()).split('\n')
sanctoral = ''.join(open(str(pathlib.Path(__file__).parent.absolute()) + '\\sanctoral.txt', 'r', encoding = ' utf-8').readlines()).split('\n')

kalendar = open(str(pathlib.Path(__file__).parent.absolute()) + '\\data\\kalendar.json', 'r', encoding = ' utf-8').readlines()

#1 lower than golden number, April date (0 for 30 March and -1 for 31 March)
paschatable = [14, 3, 22, 11, 0, 19, 8, 27, 16, 5, 24, 13, 2, 21, 10, -1, 18, 7, 26] 

#Corrects the Pascha table for leap years and other corrections
def correctedpaschatable(year):
    correction = 0
    for i in range(0, int((year - 2000) / 100)):
        yr = i * 100 + 2000
        if (yr % 400 != 0):
            correction -= 1
        if ((yr % 2500) in [200, 500, 800, 1100, 1400, 1800, 2100, 2400]):
            correction += 1
    newpaschatable = paschatable
    while (correction > 0):
        correction -= 1
        for i in range(0, 19):
            newpaschatable[i] += 1
            if (newpaschatable[i] == 28):
                newpaschatable[i] = -1
    while (correction < 0):
        correction += 1
        for i in range(0, 19):
            newpaschatable[i] -= 1
            if (newpaschatable[i] == -2):
                newpaschatable[i] = 27
                
    return newpaschatable

#If the date number is negative or zero, create a date in the previous month
def safenegdatecreate(year, month, date0):
    if (date0 < 1):
        return date(year, month, 1) - timedelta(days = 1 - date0)
    else:
        return date(year, month, date0)
          
def geteaster(year):
    goldennumber = (year + 1) % 19
    if (goldennumber == 0):
        goldennumber = 19
    ptable = correctedpaschatable(year)
    adjbbound = 18 if 18 in ptable and 19 in ptable else 19
    date0 = ptable[goldennumber - 1]
    group = ""
    if (date0 < adjbbound):
        matcheddate = safenegdatecreate(year, 4, date0)
        return matcheddate + timedelta(days = (7 if matcheddate.weekday() == 6 else 6 - matcheddate.weekday())) 
    elif (date0 < 20):
        matcheddate = safenegdatecreate(year, 4, date0)
        return matcheddate + timedelta(days = (6 - matcheddate.weekday())) 
    else:
        matcheddate = safenegdatecreate(year, 3, date0)
        if (matcheddate.weekday() == 5):
            return matcheddate + timedelta(days = 8)
        elif (matcheddate.weekday() == 6):
            return matcheddate + timedelta(days = 7)
        else:
            return matcheddate + timedelta(days = (6 - matcheddate.weekday()))         

def kalendar(year):
    leapyear = year % 4 == 0 and (year % 400 == 0 or year % 100 != 0)
    kal = {}
    
    def datestring(date0):
        return str(date0.month).zfill(2) + '-' + str(date0.day).zfill(2)
    def sundayafter(date0):
        return date0 + timedelta(days=6-date0.weekday()) if date0.weekday() != 6 else date0 + timedelta(days=6)
    def todate(text):
        return date(year, int(text[:2]), int(text[3:]))
    def addentry(date0, entry):
        if (date0 in kal):
            kal[date0].append(entry)
        else:
            kal[date0] = [entry]
    def exclusiveentry(date0, entry):
        kal[date0] = [entry]
    def entry(date0):
        return kal[date0]
    def removelabel(entry, label):
        labelindex = entry.index('[')
        labels = entry[labelindex + 1:-1].split(',')
        labels.remove(label)
        if (len(labels) == 0):
            return entry[:labelindex]
        else:
            return entry[:labelindex] + '[' + ','.join(labels) + ']'
    
    pascha = geteaster(year)
    christmas = date(year, 12, 25)
    adventstart = christmas - timedelta(days = 22 + christmas.weekday())
    xxiiipentecost = pascha + timedelta(days=210)
    xxivpentecost = adventstart - timedelta(days=7)
    epiphany = date(year, 1, 6)
    
    epiphanysunday = sundayafter(epiphany)
    
    #Advent Cycle
    for i in adventcycle:
        entry = i
        date0 = adventstart + timedelta(days=i["difference"])
        
        #Christmas Eve is its own liturgical day that outranks whatever Advent day it's on but most of Matins comes from the day so Advent count is only stopped at Christmas
        if (date0 == christmas):
            break
        del entry["difference"]
        entry["date"] = datestring(date0)
        addentry(date0, entry)
    
    #Apply Paschal Cycle
    for i in paschalcycle:
        entry = i
        date0 = pascha + timedelta(days=i["difference"])
        
        if (date0 == xxivpentecost):
            break
        del entry["difference"]
        entry["date"] = datestring(date0)
        addentry(date0, entry)
    
    #Epiphany Sundays 
    epiphanyweek = 0
    while epiphanysunday + timedelta(days=epiphanyweek * 7) != pascha - timedelta(days=63):
        for i in range(0,7):
            addentry(epiphanysunday + timedelta(days=epiphanyweek * 7 + i), epiphanycycle[epiphanyweek][i])
        epiphanyweek += 1
    
    esundayomission = False
    
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
    
    

    #TODO Implement transfers AFTER Sanctorals for Pentecost & Epiphany
    
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
    
    print(dict(sorted(kal.items())))
    for i in sanctoral:
        date0 = todate(i[:6])
        addentry(date0, i[6:])
        if ('[' in i):
            if ('OC' in i[i.index('['):]):
                for j in range(1, 7):
                    addentry(date0 + timedelta(days=j),removelabel( 'SD0 Dies ' + getnumerals(j + 1) + ' infra Octavam ' + i[10:], 'OC'))
                addentry(date0 + timedelta(days=7),removelabel( 'DB0 Octava ' + i[10:], 'OC'))
                
    
    ret = ''
    for i in dict(sorted(kal.items())):
        for j in kal[i]:
            ret += str(i)[5:] + ' ' + j + '\n'
        
    return ret

year = 2023
ret = kalendar(year)
outputfilename = 'year-' + str(year) + '.txt'
with open('kalendars\\' + outputfilename, 'w') as fp:
    fp.write(ret)
print(outputfilename)