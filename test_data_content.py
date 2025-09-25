# Copyright 2025 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import pytest
import re

import datamanage

files = []
for name, file in datamanage.getwalk('breviarium-1888'):
    files.append(file)

@pytest.mark.parametrize('file', files)
def test_data(file) -> None:
    pile = datamanage.load_data(file)
    for entry in pile:
        tags = entry['tags']
        for k, v in entry.items():
            assert re.search('^[a-z-]+$', k), entry
            assert k != 'forwards-to', entry
            if k == 'tags':
                if type(v) is list:
                    assert all(all(re.search('^[a-z-]+$', y) for y in x) for x in v), entry
                else:
                    assert all(re.search('^[a-z-]+$', x) for x in v), entry
            assert all(not x in v for x in list('`ẃŕṕśǵḱĺźćǘńḿ')), entry
        if 'collecta' in entry['tags']:
            assert 'terminatio' in entry, entry


oes = set()

def idoes(txt):
    txt = txt.replace('\u0301', '&')
    fd = re.findall('[a-zA-ZáéíóúýÁÉÍÓÚÝæœÆŒǽǼ&]+', txt)
    for f in fd:
        if ('œ' in f or 'Œ' in f) and not any(x in f for x in list('&áéíóúýÁÉÍÓÚÝ')):
            oes.add(f)

for file in files:
    pile = datamanage.load_data(file)
    for entry in pile:
        for k, v in entry.items():
            if type(v) is list:
                for i in v:
                    if type(i) is str:
                        idoes(i)
            elif type(v) is str:
                idoes(v)

print(oes)
