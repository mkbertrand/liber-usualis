import json
import pathlib
from datetime import date
from dies import latindate

data_root = pathlib.Path(__file__).parent

def load_data(p: str):
    data = json.loads(data_root.joinpath(p).read_text(encoding="utf-8"))
    return data
    
file = load_data('data/kalendar.json')

ret = '[\n'
for day, entries in file.items():
    for entry in entries:
        ret += '\t{\n\t\t"occurrence":"' + latindate(date(2023, int(day.split('-')[0]), int(day.split('-')[1]))) + '",\n\t\t"tags":' + json.dumps(entry) + '\n\t},\n'
    
ret = ret[:-1]
ret += ']'

newkal = open(r'new_kalendar.json','w')

newkal.write(ret)
