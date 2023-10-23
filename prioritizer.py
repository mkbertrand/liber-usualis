from kalendar import kalendar
import datamanage
import os.path
import json
import pathlib
from datetime import date, datetime, timedelta
import re

data_root = pathlib.Path(__file__).parent

def load_data(p: str):
    data = json.loads(data_root.joinpath(p).read_text(encoding='utf-8'))

    # JSON doesn't support sets. Recursively find and replace anything that
    # looks like a list of tags with a set of tags.
    def recurse(obj):
        match obj:
            case dict():
                return {datetime.strptime(k, '%Y-%m-%d').date() if not re.search('^\d{4}-\d{2}-\d{2}$',k) == None else k: recurse(v) for k, v in obj.items()}
                return {k: recurse(v) for k, v in obj.items()}
            case list():
                if all(type(x) == str for x in obj):
                    return set(obj)
                return [recurse(v) for v in obj]
            case _:
                return obj

    return recurse(data)

def taggedentry(day, tags):
    for i in day:
        if i >= tags:
            return i

coincidencetable = load_data('vesperal-coincidence.json')
hasivespers = {'simplex','semiduplex','duplex','duplex-majus','duplex-ii-classis','duplex-i-classis','antiphona-bmv'}
hasiivespers = {'feria','semiduplex','duplex','duplex-majus','duplex-ii-classis','duplex-i-classis'}

def getvespers(day):
    currday = datamanage.getdate(day)
    nextday = datamanage.getdate(day + timedelta(days=1))
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
    if not len(ivespersprimarycandidates) == 0:
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
    while cycle():
        pass
    return vesperal

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Daily Vespers specification generator',
    )

    parser.add_argument(
        '-d',
        '--date',
        type=str,
        default=str(date.today()),
        help='Date to generate',
    )

    args = parser.parse_args()

    # Generate kalendar
    ret = getvespers(datetime.strptime(args.date, '%Y-%m-%d').date())

    print(ret)
