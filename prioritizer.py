from kalendar import kalendar
import os.path
import json
import pathlib
import datetime
from datetime import date
from datetime import timedelta
import warnings

data_root = pathlib.Path(__file__).parent.joinpath("kalendars")

def load_data(p):
    data = json.loads(data_root.joinpath(p).read_text(encoding="utf-8"))

    # JSON doesn't support sets. Recursively find and replace anything that
    # looks like a list of tags with a set of tags.
    def recurse(obj):
        match obj:
            case dict():
                return {datetime.datetime.strptime(k, "%Y-%m-%d").date(): recurse(v) for k, v in obj.items()}
            case list():
                if all(type(x) == str for x in obj):
                    return set(obj)
                return [recurse(v) for v in obj]
            case _:
                return obj

    return recurse(data)

def tofile(kal):
    file = open(f"kalendars/1888-{list(kal.kal.keys())[0].year!s}.json", "w")
    file.write(json.dumps({str(k): [list(ent) for ent in v] for k, v in kal.items()}))
    file.close()

def getyear(year):
    try:
        return load_data(f"1888-{year!s}.json")
    except FileNotFoundError:
        warnings.warn(f"Year {year!s} not found in database.  Generating file...")
        kal = kalendar.kalendar(year)
        tofile(kal)
        return kal

def getdate(day):
    year = getyear(day.year)
    return year[day]

def taggedentry(day, tags):
    for i in day:
        if i >= tags:
            return i

hasivespers = {"simplex","semiduplex","duplex","duplex-majus","duplex-ii-classis","duplex-i-classis"}

def prioritize(day):
    daytags = getdate(day)
    daytags = list(filter(lambda occ: not "simplex" in occ, daytags))
    for i in getdate(day + timedelta(days=1)):
        if not i.isdisjoint(hasivespers) and not "infra-octavam" in i:
            daytags.append(i | {"i-vesperae"})
    tagged = taggedentry(daytags, {"pascha", "duplex-i-classis"})
    if tagged:
        return tagged.add("ordinarium")

    print(daytags)

prioritize(date(2021, 1,1))
