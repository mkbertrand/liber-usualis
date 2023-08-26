from datetime import date, timedelta

# Zero-indexed golden number, April date (-1 for 30 March and 0 for 31 March)
paschatable = [14, 3, 22, 11, 0, 19, 8, 27, 16, 5, 24, 13, 2, 21, 10, -1, 18, 7, 26]

# Correct the Pascha table for leap years and other corrections
def correctedpaschatable(year):
    correction = 0
    for i in range(0, int((year - 2000) / 100)):
        yr = i * 100 + 2000
        # Solar correction
        if yr % 400 != 0:
            correction -= 1
        # Lunar correction
        if (yr % 2500) in [200, 500, 800, 1100, 1400, 1800, 2100, 2400]:
            correction += 1
    return [(e+correction + 30) % 29 - 1 for e in paschatable]

# If the date number is negative or zero, create a date in the previous month
def safenegdatecreate(year, month, date0):
    return date(year, month, 1) + timedelta(days = date0 - 1)

def geteaster(year):
    # Zero-indexed golden number
    goldennumber = year % 19
    ptable = correctedpaschatable(year)
    adjbbound = 18 if 18 in ptable and 19 in ptable else 19
    date0 = ptable[goldennumber]
    if date0 < adjbbound:
        matcheddate = safenegdatecreate(year, 4, date0+1)
    elif date0 < 20:
        matcheddate = safenegdatecreate(year, 4, date0)
    else:
        matcheddate = safenegdatecreate(year, 3, date0+2)
    return matcheddate + timedelta(days = 7 - matcheddate.isoweekday())
