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

def hasfile(year):
    return os.path.isfile("kalendars/1888-" + str(year) + ".json")

def tofile(kal):
    file = open("kalendars/1888-" + str(list(kal.kal.keys())[0].year) + ".json", "w")
    file.write(json.dumps({str(k): [list(ent) for ent in v] for k, v in kal.items()}))
    file.close()

def getyear(year):
    if hasfile(year):
        return load_data("1888-" + str(year) + ".json")
    else:
        warnings.warn("Year " + str(year) + " not found in database.  Generating file...")
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