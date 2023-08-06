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
    pascha = geteaster(2023)
    
    def addentry(date, entry):
        kal[date.month - 1][date.day - 1] = str((date - pascha).days) + ' ' + entry

    #kal = [''] * (366 if leapyear else 365)
    ashwednesday = pascha - timedelta(days=46)
    passionsunday = pascha - timedelta(days=14)
    septuagesima = pascha - timedelta(days=63)
    ascension = pascha + timedelta(days=39)
    #Pre-Lent
    addentry(septuagesima, 'SD2 Dominica Septuagesima')
    infra = ' infra Hebdomadam Septuagesimæ'
    for j in range(1, 6):
        addentry(septuagesima + timedelta(days=j), 'SM0 Feria ' + getnumerals(j + 1) + infra)
    addentry(septuagesima + timedelta(days=6), 'SM0 Sabbato' + infra)
    addentry(septuagesima + timedelta(days=7), 'SD2 Dominica Sexagesima')
    infra = ' infra Hebdomadam Sexagesimæ'
    for j in range(1, 6):
        addentry(septuagesima + timedelta(days=j + 7), 'SM0 Feria ' + getnumerals(j + 1) + infra)
    addentry(septuagesima + timedelta(days=13), 'SM0 Sabbato' + infra)
    
    #Quinquasesima
    addentry(septuagesima + timedelta(days=14), 'SD2 Dominica Quinquasesima')
    addentry(ashwednesday - timedelta(days=2), 'SM0 Feria II infra Hebdomadam Quinquasesimæ')
    addentry(ashwednesday - timedelta(days=1), 'SM0 Feria III infra Hebdomadam Quinquasesimæ')
    addentry(ashwednesday, 'FR1 Feria IV Cinerum')
    addentry(ashwednesday + timedelta(days=1), 'FRP Feria V post Cineres')
    addentry(ashwednesday + timedelta(days=2), 'SM0 Feria VI post Cineres')
    addentry(ashwednesday + timedelta(days=3), 'SM0 Sabbato post Cineres')
    
    #Lent
    for i in range(0, 4):
        sunday = ashwednesday + timedelta(days=4 + 7 * i)
        addentry(sunday, 'SD1 Dominica ' + getnumerals(i + 1) + ' in Quadragesima')
        infra = ' infra Hebdomadam ' + getnumerals(i + 1) + ' in Quadragesima'
        for j in range(1, 6):
            addentry(sunday + timedelta(days=j), 'SM0 Feria ' + getnumerals(j + 1) + infra)
        addentry(sunday + timedelta(days=6), 'SM0 Sabbato' + infra)

    #Passiontide
    addentry(passionsunday, 'SD1 Dominica de Passione')
    infra = ' infra Hebdomadam Passionis'
    for j in range(1, 6):
        addentry(passionsunday + timedelta(days=j), 'FRM Feria ' + getnumerals(j + 1) + infra)
    addentry(passionsunday + timedelta(days=6), 'FRM Sabbato' + infra)
    addentry(passionsunday + timedelta(days=7), 'SD1 Dominica in Palmis')
    infra = ' Majoris Hebdomadæ'
    for j in range(1, 4):
        addentry(passionsunday + timedelta(days=j + 7), 'FRP Feria ' + getnumerals(j + 1) + infra)
    #Triduum
    addentry(passionsunday + timedelta(days=11), 'FRP Feria V in Cena Domini')
    addentry(passionsunday + timedelta(days=12), 'FRP Feria VI in Parasceve')
    addentry(passionsunday + timedelta(days=13), 'FRP Sabbato Sancto')
    
    #Paschal Octave
    addentry(pascha, 'DB1 Dominica Resurrectionis')
    addentry(pascha + timedelta(days=1), 'DB1 Die II infra Octavam Paschæ')
    addentry(pascha + timedelta(days=2), 'DB1 Die III infra Octavam Paschæ')
    addentry(pascha + timedelta(days=3), 'SD0 Die IV infra Octavam Paschæ')
    addentry(pascha + timedelta(days=4), 'SD0 Die V infra Octavam Paschæ')
    addentry(pascha + timedelta(days=5), 'SD0 Die VI infra Octavam Paschæ')
    addentry(pascha + timedelta(days=6), 'SD0 Sabbato in Albis')
    
    #Paschal Weeks
    for i in range(1, 6):
        sunday = pascha + timedelta(days=7 * i)
        addentry(sunday, 'DMm Dominica ' + getnumerals(i) + ' post Octavam Paschæ')
        infra = ' infra Hebdomadam ' + getnumerals(i) + ' post Octavam Paschæ'
        for j in range(1, 6):
            addentry(sunday + timedelta(days=j), 'FR0 Feria ' + getnumerals(j + 1) + infra)
        addentry(sunday + timedelta(days=6), 'FR0 Sabbato' + infra)
    addentry(pascha + timedelta(days=7), 'DB1 Dominica in Albis in Octava Paschæ')
    
    #Ascensiontide & Octave of Pentecost
    addentry(ascension, 'DB1 In Ascensione Domini')
    addentry(ascension + timedelta(days=1), 'FR0 Feria VI infra Octavam Ascensionis')
    addentry(ascension + timedelta(days=2), 'FR0 Sabbato infra Octavam Ascensionis')
    addentry(ascension + timedelta(days=3), 'DMm Dominica infra Octavam Ascensionis')
    addentry(ascension + timedelta(days=4), 'FR0 Feria II infra Octavam Ascensionis')
    addentry(ascension + timedelta(days=5), 'FR0 Feria III infra Octavam Ascensionis')
    addentry(ascension + timedelta(days=6), 'FR0 Feria IV infra Octavam Ascensionis')
    addentry(ascension + timedelta(days=7), 'DBM Octavæ Ascensionis')
    addentry(ascension + timedelta(days=8), 'FR0 Feria VI post Octavam Ascensionis')
    addentry(ascension + timedelta(days=9), 'FRP Sabbato in Vigilia Pentecostes')
    addentry(ascension + timedelta(days=10), 'DB1 Dominica Pentecostes')
    addentry(ascension + timedelta(days=11), 'DB1 Die II infra Octavam Pentecostes')
    addentry(ascension + timedelta(days=12), 'DB1 Die III infra Octavam Pentecostes')
    addentry(ascension + timedelta(days=13), 'SD0 Feria IV infra Octavam Pentecostes')
    addentry(ascension + timedelta(days=14), 'SD0 Feria V infra Octavam Pentecostes')
    addentry(ascension + timedelta(days=15), 'SD0 Feria VI infra Octavam Pentecostes')
    addentry(ascension + timedelta(days=16), 'SD0 Sabbato infra Octavam Pentecostes')
    
    #Pentecost Season
    for i in range(1, 24):
        sunday = pascha + timedelta(days=49 + 7 * i)
        addentry(sunday, 'DMm Dominica ' + getnumerals(i) + ' post Octavam Pentecostes')
        infra = ' infra Hebdomadam ' + getnumerals(i) + ' post Octavam Pentecostes'
        for j in range(1, 6):
            addentry(sunday + timedelta(days=j), 'FR0 Feria ' + getnumerals(j + 1) + infra)
        addentry(sunday + timedelta(days=6), 'FR0 Sabbato' + infra)
    addentry(ascension + timedelta(days=17), 'DB1 Octavæ Pentecostes')
    
    for i in kal:
        for j in i:
            print(j)
    
kalendar(2023)