from datetime import datetime, date, timedelta

menses = ['januarius','februarius','martius','aprilis','majus','junius','julius','augustus','september','october','november','december']
mensum = ['januarii','februarii','martii','aprilis','maji','junii','julii','augusti','septembris','octobris','novembris','decembris']
numerals = ['i','ii','iii','iv','v','vi','vii','viii','ix','x','xi','xii','xiii','xiv','xv','xvi','xvii','xviii','xix','xx']

def leapyear(year):
    return year % 4 == 0 and (year % 400 == 0 or year % 100 != 0)

def getnones(month):
    if (month == 3 or month == 5 or month == 7 or month == 10):
        return 7
    else:
        return 5

def getides(month):
    if (month == 3 or month == 5 or month == 7 or month == 10):
        return 15
    else:
        return 13

def latindate(date0):
    nones = getnones(date0.month)
    ides = getides(date0.month)
    ret = ''
    if (date0.day == 1):
        ret = 'kalendae'
    elif (date0.day < nones - 1):
        ret = 'ad-' + numerals[nones - date0.day] + '-nonas'
    elif (date0.day == nones - 1):
        ret = 'pridie-nonas'
    elif (date0.day == nones):
        ret = 'nonae'
    elif (date0.day < ides - 1):
        ret = 'ad-' + numerals[ides - date0.day] + '-idus'
    elif (date0.day == ides - 1):
        ret = 'pridie-idus'
    elif (date0.day == ides):
        ret = 'idus'

    if (ret != ''):
        return ret + '-' + mensum[date0.month - 1]

    dif = ((date(date0.year + 1, 1, 1) - date0) if date0.month == 12 else (date(date0.year, date0.month + 1, 1) - date0)).days
    if (dif == 1):
        ret = 'pridie-kalendas'
    else:
        if leapyear(date0.year) and date0.month == 2 and date0.day == 24:
            return 'intercalaris'
        elif leapyear(date0.year) and date0.month == 2 and date0.day < 24:
            ret = 'ad-' + numerals[dif - 1] + '-kalendas'
        else:
            ret = 'ad-' + numerals[dif] + '-kalendas'

    return ret + '-' + mensum[date0.month % 12]

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Latin date generator',
    )

    parser.add_argument(
        '-y',
        '--year',
        type=int,
        default=None,
        help='Year to generate',
    )

    parser.add_argument(
        '-d',
        '--date',
        type=str,
        default=str(date.today()),
        help='Date to generate',
    )

    args = parser.parse_args()
    if not args.year is None:
        for i in range(0, 366 if leapyear(args.year) else 365):
            print(latindate(date(args.year, 1, 1) + timedelta(days=i)))
    else:
        print(latindate(datetime.strptime(args.date, '%Y-%m-%d').date()))

