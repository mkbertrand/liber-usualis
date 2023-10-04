from kalendar import kalendar
import os.path
import json
import pathlib
from datetime import date, datetime, timedelta
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
                return {datetime.strptime(k, "%Y-%m-%d").date() if not re.search('^\d{4}-\d{2}-\d{2}$',k) == None else k: recurse(v) for k, v in obj.items()}
                return {k: recurse(v) for k, v in obj.items()}
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

year_buffer_max_len = 16
year_buffer = {}

for i in range(datetime.now().year + year_buffer_max_len, datetime.now().year - 3, -1):
    year_buffer[i] = kalendar.kalendar(i)
print(year_buffer.keys())
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
        print(year_buffer.keys())
        return kal
    else:
        warnings.warn("Year " + str(year) + " not found in database.  Generating file...")
        kal = kalendar.kalendar(year)
        tofile(kal)
        year_buffer.pop(list(year_buffer.keys())[0])
        year_buffer[year] = kal
        print(year_buffer.keys())
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

def vesperscoincider(day):
    currday = getdate(day)
    nextday = getdate(day + timedelta(days=1))
    ivespers = [i.union({'i-vesperae'}) for i in filter(lambda occ: not occ.isdisjoint(hasivespers) and not 'infra-octavam' in occ, nextday)]
    iivespers = [i.union({'ii-vesperae'}) for i in filter(lambda occ: not occ.isdisjoint(hasiivespers), currday)]
    ivespersprimarycandidates = list(filter(lambda occ: occ.isdisjoint({'commemoratum','temporale','fixum'}), ivespers))
    iivespersprimarycandidates = list(filter(lambda occ: occ.isdisjoint({'commemoratum','temporale','fixum'}), iivespers))
    if len(iivespersprimarycandidates) == 0:
        # Grabs the temporale (ferial) II Vespers
        iivespprim = next(filter(lambda occ: occ.isdisjoint({'commemoratum','fixum'}), iivespers))
        for i in iivespers:
            if i == iivespprim:
                i.add('primarium')
    else:
        for i in iivespers:
            if i == iivespersprimarycandidates[0]:
                i.add('primarium')
    if len(ivespersprimarycandidates) == 0:
        return iivespers
    else:
        for i in ivespers:
            if i == ivespersprimarycandidates[0]:
                i.add('primarium')
        # Final product
        vesperal = iivespers + ivespers
        def cycle():
            for coincidence in coincidencetable:
                for i in vesperal:
                    if coincidence['indices'].issubset(i) and i.isdisjoint({'fixum'}):
                        if not type(coincidence['response']) == list:
                            perform_action(coincidence, day, i)
                        else:
                            for j in coincidence['response']:
                                for k in vesperal:
                                    if not k == i and not 'fixum' in k and j['indices'].issubset(k):
                                        target = i
                                        if 'target' in j and j['target'] == 'b':
                                            target = k
                                        if not (j['response'] == 'commemorandum' and 'commemoratum' in target) and not (j['response'] == 'psalmi' and 'psalmi' in target):
                                            if j['response'] == 'omittendum':
                                                vesperal.remove(target)
                                            elif j['response'] == 'commemorandum':
                                                if 'primarium' in target:
                                                    target.remove('primarium')
                                                target.add('commemoratum')
                                            elif j['response'] == 'psalmi':
                                                if 'primarium' in target:
                                                    target.remove('primarium')
                                                target.add('psalmi')
                                            elif j['response'] == 'errora':
                                                raise RuntimeError(f'Unexpected coincidence between {i} and {k} on day {vesperal}')
                                            else:
                                                raise RuntimeError(f'Unexpected response: {j["response"]}')
                                            return True
            return False
        while cycle() == True:
            ''
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

for i in range(1500, 2200):
    for j in range(0,366):
        vesperscoincider(date(i, 1, 1) + timedelta(days=j))