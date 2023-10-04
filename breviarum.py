import pathlib
import json
import copy
import os
from datetime import date, datetime, timedelta

from kalendar import kalendar

data_root = pathlib.Path(__file__).parent

def load_data(p: str):
    data = json.loads(data_root.joinpath(p).read_text(encoding="utf-8"))

    # JSON doesn't support sets. Recursively find and replace anything that
    # looks like a list of tags with a set of tags.
    def recurse(obj):
        match obj:
            case dict():
                return {k: recurse(v) for k, v in obj.items()}
            case list():
                if all(type(x) == str for x in obj):
                    return frozenset(obj)
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

year_buffer_max_len = 16
year_buffer = {}

for i in range(datetime.now().year + year_buffer_max_len, datetime.now().year - 3, -1):
    year_buffer[i] = kalendar.kalendar(i)

def getyear(year):
    if year in year_buffer:
        if not list(year_buffer.keys())[year_buffer_max_len - 1] == year:
            kal = year_buffer.pop(year)
            year_buffer[year] = kal
            return kal
        else:
            return year_buffer[year]
    elif hasfile(year):
        kal = load_data("kalendars/1888-" + str(year) + ".json")
        year_buffer.pop(list(year_buffer.keys())[0])
        year_buffer[year] = kal
        return kal
    else:
        warnings.warn("Year " + str(year) + " not found in database.  Generating file...")
        kal = kalendar.kalendar(year)
        tofile(kal)
        year_buffer.pop(list(year_buffer.keys())[0])
        year_buffer[year] = kal
        return kal

def getdate(day):
    year = getyear(day.year)
    return year[day]

psalterium = load_data('breviarum/psalterium.json')
formulae = load_data('breviarum/formulae.json')
psalmi = load_data('breviarum/psalmi.json')

defaultpile = copy.deepcopy(psalterium)
defaultpile.extend(formulae)
defaultpile.extend(psalmi)    

def searchpile(query, pile):
    for i in pile:
        if i['tags'].issubset(query):
            yield i

def singlesearchpile(query, pile):
    result = list(searchpile(query, pile))
    assert len(result) == 1
    return result[0]

def hour(hour: str):
    elementpile = copy.deepcopy(defaultpile)
    
    hourtemplate = singlesearchpile({hour}, elementpile)
    print(hourtemplate)
    
    
    
print(hour('completorium'))