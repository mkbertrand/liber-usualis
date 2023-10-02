from kalendar import kalendar
import os.path
import json
import pathlib
import datetime
from datetime import date
from datetime import timedelta
import warnings
import re

data_root = pathlib.Path(__file__).parent

def load_data(p: str):
    data = json.loads(data_root.joinpath(p).read_text(encoding="utf-8"))

    # JSON doesn't support sets. Recursively find and replace anything that
    # looks like a list of tags with a set of tags.
    def recurse(obj):
        match obj:
            case dict():
                return {datetime.datetime.strptime(k, "%Y-%m-%d").date() if not re.search('^\d{4}-\d{2}-\d{2}$',k) == None else k: recurse(v) for k, v in obj.items()}
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

def getyear(year):
    if hasfile(year):
        return load_data("kalendars/1888-" + str(year) + ".json")
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

coincidencetable = load_data('vesperal-coincidence.json')
hasivespers = {"simplex","semiduplex","duplex","duplex-majus","duplex-ii-classis","duplex-i-classis"}
hasiivespers = {"feria","semiduplex","duplex","duplex-majus","duplex-ii-classis","duplex-i-classis"}

def resolve(day):
    currday = getdate(day)
    nextday = getdate(day + timedelta(days=1))
    ivespers = list(filter(lambda occ: not occ.isdisjoint(hasivespers) and not 'infra-octavam' in occ, nextday))
    iivespers = list(filter(lambda occ: not occ.isdisjoint(hasiivespers) and not 'dies-vii' in occ, currday))

    ivespersprimary = next(filter(lambda occ: occ.isdisjoint({'commemoratum','temporale','fixum'}), ivespers))
    iivespersprimary = next(filter(lambda occ: occ.isdisjoint({'commemoratum','temporale','fixum'}), iivespers))
    if iivespersprimary == None:
        next(filter(lambda occ: occ.isdisjoint({'commemoratum','fixum'}), iivespers))
    if ivespersprimary == None:
        return iivespers
    else:
        # Final product
        vesperal = []

        def primaryresolve():
            for coincidence in coincidencetable:
                if coincidence['indices'].issubset(ivespersprimary):
                    for i in coincidence['response']:
                        if i['indices'].issubset(iivespersprimary):
                            if i['response'] == 'omittendum':
                                vesperal.append(ivespersprimary.union({'i-vesperae'}) if i['target'] == 'b' else iivespersprimary.union({'ii-vesperae'}))
                            elif i['response'] == 'commemorandum':
                                vesperal.append(ivespersprimary.union({'i-vesperae'}) if i['target'] == 'b' else iivespersprimary.union({'ii-vesperae'}))
                                vesperal.append(iivespersprimary.union({'ii-vesperae','commemoratum'}) if i['target'] == 'b' else ivespersprimary.union({'i-vesperae','commemoratum'}))
                            elif i['reponse'] == 'psalmi':
                                vesperal.append(ivespersprimary.union({'i-vesperae'}) if i['target'] == 'b' else iivespersprimary.union({'ii-vesperae'}))
                                vesperal.append(iivespersprimary.union({'ii-vesperae','psalmi'}) if i['target'] == 'b' else ivespersprimary.union({'i-vesperae','psalmi'}))
                            elif instruction['response'] == 'errora':
                                raise RuntimeError(f'Unexpected coincidence on day {day}')
                            else:
                                raise RuntimeError(f'Unexpected response: {instruction["response"]}')
                            return
        primaryresolve()

        ivespersremove = []
        iivespersremove = []
        for coincidence in coincidencetable:
            for i in ivespers:
                if coincidence['indices'].issubset(i):
                    for j in coincidence['response']:
                        for k in iivespers:
                            if j['indices'].issubset(k) and j['response'] == 'omittendum':
                                if j['target'] == 'a':
                                    ivespersremove.append(i)
                                else:
                                    iivespersremove.append(j)

        for i in ivespersremove:
            if i in ivespers:
                ivespers.remove(i)
        for i in iivespersremove:
            if i in iivespers:
                iivespers.remove(i)

        for i in ivespers:
            vesperal.append(i.union({'i-vesperae','commemoratum'}))
        for i in iivespers:
            vesperal.append(i.union({'ii-vesperae','commemoratum'}))
            
        return vesperal
def prioritize(day):
    diurnal = getdate(day)
    vesperal = list(filter(lambda occ: occ.isdisjoint(noiivespers), diurnal))
    for i in getdate(day + timedelta(days=1)):
        if not i.isdisjoint(hasivespers) and not "infra-octavam" in i:
            vesperal.append(i | {"i-vesperae"})
    tagged = taggedentry(diurnal, {"pascha", "duplex-i-classis"})
    if tagged:
        return tagged.add("ordinarium")
    print(diurnal)
    prioritizevespers(vesperal)
    
resolve(date(2021, 1,1))