# Copyright 2024 (AGPL-3.0-or-later), Miles K. Bertrand et al.

from datetime import date, timedelta
from typing import List


def nextsunday(date0: date, *, weeks: int = 0) -> date:
    """
    Return the Sunday on or after the given date, +/- the given number of weeks
    """
    return date0 + timedelta(weeks=weeks + 1, days=-date0.isoweekday())


def geteaster_bede(year: int) -> date:
    """
    Mostly as described at https://www.calendarbede.com/book/calculation-gregorian-easter-sunday
    """
    goldennumber = year % 19
    century = year // 100 + 1
    correction_lunar = 8*(century - 15) // 25
    correction_solar = 3*(century - 16) // 4
    epact = (11 * goldennumber + 11 + (correction_lunar - correction_solar - 10)) % 30
    if 0 <= epact <= 23:
        full_moon_march = 44 - epact
    elif epact == 24:
        full_moon_march = 49
    elif epact == 25 and goldennumber < 11:
        full_moon_march = 49
    elif epact == 25 and goldennumber >= 11:
        full_moon_march = 48
    elif 26 <= epact <= 29:
        full_moon_march = 74 - epact
    else:
        raise AssertionError(f"Invalid: epact={epact}, goldennumber={goldennumber}")

    # Actual date of the full moon
    full_moon_date = date(year, 3, 1) + timedelta(days=full_moon_march - 1)
    # Sunday after the full moon
    return nextsunday(full_moon_date + timedelta(days=1))


def geteaster_gauss(year: int) -> date:
    """
    Literal translation of https://en.wikipedia.org/wiki/Date_of_Easter#Gauss's_Easter_algorithm
    """
    a = year % 19
    b = year % 4
    c = year % 7
    k = year // 100
    p = (13 + 8 * k) // 25
    q = k // 4
    M = (15 - p + k - q) % 30
    N = (4 + k - q) % 7
    d = (19 * a + M) % 30
    e = (2 * b + 4 * c + 6 * d + N) % 7
    m30 = (11 * M + 11) % 30
    if d == 28 and e == 6 and m30 < 19:
        return date(year, 4, 18)
    elif d == 29 and e == 6:
        return date(year, 4, 19)
    else:
        return date(year, 3, 1) + timedelta(days=22 + d + e - 1)


def geteaster_assert(year: int) -> date:
    """
    Call each function and make sure they all agree and return something reasonable
    """
    easter_bede = geteaster_bede(year)
    easter_gauss = geteaster_gauss(year)
    easter = easter_bede

    assert easter == easter_bede
    assert easter == easter_gauss

    # Ensure Easter falls on a reasonable date
    assert easter.isoweekday() == 7, "Easter must fall on a Sunday!"
    assert date(year, 3, 22) <= easter <= date(year, 4, 25)

    return easter


# Default geteaster implementation
geteaster = geteaster_bede


if __name__ == "__main__":
    import argparse
    from datetime import datetime
    import sys

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Easter calculator",
    )

    parser.add_argument(
        "-f",
        "--format",
        default="%Y-%m-%d",
        help="Output format (strftime)",
    )

    parser.add_argument(
        "-y",
        "--year",
        type=int,
        default=datetime.now().year,
        help="Year to generate",
    )

    args = parser.parse_args()

    easter = geteaster(args.year)

    sys.stdout.write(easter.strftime(args.format) + "\n")
