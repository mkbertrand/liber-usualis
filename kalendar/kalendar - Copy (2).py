from datetime import datetime
from datetime import date
from datetime import timedelta
import math
import pathlib
import html.entities

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

paschalcycle = ''.join(open(str(pathlib.Path(__file__).parent.absolute()) + '\\paschalcycle.txt', 'r', encoding = ' utf-8').readlines()).split('\n')

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
    kal = [[''] * 31, [''] * (29 if leapyear else 28), [''] * 31, [''] * 30, [''] * 31, [''] * 30, [''] * 31, [''] * 31, [''] * 30, [''] * 31, [''] * 30, [''] * 31]
    
    
    def addentry(date, entry):
        kal[date.month - 1][date.day - 1] = str(date.month) + '/' + str(date.day) + ' ' + entry
    def entry(date):
        return kal[date.month - 1][date.day - 1]
        
    pascha = geteaster(year)
    christmas = date(year, 12, 25)
    adventstart = christmas - timedelta(days = 22 + christmas.weekday())
    epiphany = date(year, 1, 6)
    
    epiphanysunday = epiphany + timedelta(days = 6 - epiphany.weekday()) if epiphany.weekday() != 6 else epiphany + timedelta(days=6)
    
    #Apply Paschal Cycle
    for i in paschalcycle:
        splitentry = i.split(' ')
        addentry(pascha + timedelta(days=int(splitentry[0])), ' '.join(splitentry[1:]))
    
    #Advent
    for i in range(0, 4):
        sunday = adventstart + timedelta(days=7 * i)
        if (sunday + timedelta(days=1) < christmas):
            addentry(sunday, 'SD2 Dominica ' + getnumerals(i + 1) + ' Adventus')
        infra = ' infra Hebdomadam ' + getnumerals(i + 1) + ' Adventus'
        for j in range(1, 6):
            if (sunday + timedelta(days=j + 1) < christmas):
                addentry(sunday + timedelta(days=j), 'SM0 Feria ' + getnumerals(j + 1) + infra)
        if (sunday + timedelta(days=j + 1) < christmas):
            addentry(sunday + timedelta(days=6), 'SM0 Sabbato' + infra)
    addentry(adventstart, 'SD1 Dominica I Adventus')
    
    #Epiphany 
    epiphanyweek = 0
    while epiphanysunday + timedelta(days=epiphanyweek * 7) != pascha - timedelta(days=63):
        addentry(epiphanysunday + timedelta(days=epiphanyweek * 7), 'DMm Dominica ' + getnumerals(epiphanyweek + 1) + ' post Epiphaniam')
        infra = ' infra Hebdomadam ' + getnumerals(epiphanyweek + 1) + ' post Epiphaniam'
        for i in range(1, 6):
            addentry(epiphanysunday + timedelta(days=epiphanyweek * 7 + i), 'FR0 Feria ' + getnumerals(i + 1) + infra)
        addentry(epiphanysunday + timedelta(days=epiphanyweek * 7 + 6), 'FR0 Sabbato' + infra)
        epiphanyweek += 1
    epiphanyweek2 = 0
    if (epiphanyweek != 6):
        epiphanyweek2 = 0
        currentday = adventstart - timedelta(days=14 + 7 * epiphanyweek2)
        while not 'Dominica' in entry(currentday):
            addentry(currentday, 'DMm Dominica ' + getnumerals(6 - epiphanyweek2) + ' post Epiphaniam')
            infra = ' infra Hebdomadam ' + getnumerals(6 - epiphanyweek2) + ' post Epiphaniam'
            for i in range(1, 6):
                addentry(currentday + timedelta(days=i), 'FR0 Feria ' + getnumerals(i + 1) + infra)
            addentry(currentday + timedelta(days=6), 'FR0 Sabbato' + infra)
            epiphanyweek2 += 1
            currentday = adventstart - timedelta(days=14 + 7 * epiphanyweek2)
    if (epiphanyweek + epiphanyweek2 != 6):
        ''
    #XXIV Week after Pentecost
    #TODO Implement transfers AFTER Sanctorals for Pentecost & Epiphany
    
    pentecostxxiv = adventstart - timedelta(days=7)
    addentry(pentecostxxiv, 'DMm Dominica XXIV post Octavam Pentecostes')
    infra = ' infra Hebdomadam XXIV post Octavam Pentecostes'
    for i in range(1, 6):
        addentry(pentecostxxiv + timedelta(days=i), 'FR0 Feria ' + getnumerals(i + 1) + infra)
    addentry(pentecostxxiv + timedelta(days=6), 'FR0 Sabbato' + infra)
    
    
    #Autumnal Weeks
    
    for i in range(8, 12):
        kalends = date(year, i, 1)
        if (kalends.weekday in [0, 1, 2, 6]):
            ''
    
    for i in kal:
        for j in i:
            print(j)
kalendar(2023)