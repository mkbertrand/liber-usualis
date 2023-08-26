from datetime import date, timedelta

# 1 lower than golden number, April date (0 for 30 March and -1 for 31 March)
paschatable = [14, 3, 22, 11, 0, 19, 8, 27, 16, 5, 24, 13, 2, 21, 10, -1, 18, 7, 26]

# Corrects the Pascha table for leap years and other corrections
def correctedpaschatable(year):
    correction = 0
    for i in range(0, int((year - 2000) / 100)):
        yr = i * 100 + 2000
        if yr % 400 != 0:
            correction -= 1
        if (yr % 2500) in [200, 500, 800, 1100, 1400, 1800, 2100, 2400]:
            correction += 1
    newpaschatable = paschatable
    while (correction > 0):
        correction -= 1
        for i in range(0, 19):
            newpaschatable[i] += 1
            if newpaschatable[i] == 28:
                newpaschatable[i] = -1
    while (correction < 0):
        correction += 1
        for i in range(0, 19):
            newpaschatable[i] -= 1
            if newpaschatable[i] == -2:
                newpaschatable[i] = 27

    return newpaschatable

# If the date number is negative or zero, create a date in the previous month
def safenegdatecreate(year, month, date0):
    if date0 < 1:
        return date(year, month, 1) - timedelta(days = 1 - date0)
    else:
        return date(year, month, date0)

def geteaster(year):
    goldennumber = (year + 1) % 19
    if goldennumber == 0:
        goldennumber = 19
    ptable = correctedpaschatable(year)
    adjbbound = 18 if 18 in ptable and 19 in ptable else 19
    date0 = ptable[goldennumber - 1]
    group = ""
    if date0 < adjbbound:
        matcheddate = safenegdatecreate(year, 4, date0)
        return matcheddate + timedelta(days = (7 if matcheddate.weekday() == 6 else 6 - matcheddate.weekday()))
    elif date0 < 20:
        matcheddate = safenegdatecreate(year, 4, date0)
        return matcheddate + timedelta(days = (6 - matcheddate.weekday()))
    else:
        matcheddate = safenegdatecreate(year, 3, date0)
        if matcheddate.weekday() == 5:
            return matcheddate + timedelta(days = 8)
        elif matcheddate.weekday() == 6:
            return matcheddate + timedelta(days = 7)
        else:
            return matcheddate + timedelta(days = (6 - matcheddate.weekday()))
