import pathlib
import json
import copy
import os
from datetime import date, datetime, timedelta
import functools

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

@functools.lru_cache(maxsize=16)
def getyear(year):
    return kalendar.kalendar(year)

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