# Copyright 2024-2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import pytest
from datetime import date, timedelta
import warnings
import copy
import re
import os

import pathlib
import diff_match_patch

import breviarium
import datamanage

from composer import Corpus
import composer.util

year = 2001
corpus = Corpus(datamanage.get_book('breviarium-1888'))
changes = dict()


dmp = diff_match_patch.diff_match_patch()

# Basically a copy of util#dump_data but removes tags since these are liable to change without affecting the content being tested
def striptags(j):

    def recurse(obj, key=None):
        match obj:
            case dict():
                return str({k: recurse(v, key=k) for k, v in obj.items()})
            case list():
                return ''.join([recurse(v) for v in obj])
            case set() | frozenset():
                return ''
            case _:
                return str(obj)

    return recurse(j)

@pytest.fixture
def update_golden(request):
    return request.config.getoption('--update-golden')

@pytest.mark.parametrize('day', [date(year, 1, 1) + timedelta(days=i) for i in range(365)])
def test_match(day, update_golden) -> None:

    warnings.filterwarnings('ignore')

    if not os.path.isdir('testresults'):
        os.makedirs('testresults')
    if not os.path.isdir('testdata'):
        os.makedirs('testdata')

    for j in [['matutinum'], ['laudes', 'prima', 'tertia', 'sexta', 'nona'], ['vesperae', 'completorium']]:
        current = breviarium.generate(corpus, day, j).rite

        if update_golden:
            with open(f'testdata/{day}-{'-'.join(j)}.json', 'w') as f:
                f.write(composer.util.dump_data(current))
            pytest.skip('Updated file')
        else:
            old = re.sub(r'\[.+?\]', '[]', str(striptags(composer.util.load_data(f'testdata/{day}-{'-'.join(j)}.json', pathlib.Path(__file__).parent))))
            new = re.sub(r'\[.+?\]', '[]', str(striptags(current)))

            diffs = dmp.diff_main(old, new)
            dmp.diff_cleanupSemantic(diffs)

            change = False
            changelog = ''
            for (op, item) in diffs:
                if op == dmp.DIFF_DELETE:
                    changelog += f'- {item.replace('\\', '')}\n\n'
                    change = True
                elif op == dmp.DIFF_INSERT:
                    changelog += f'+ {item.replace('\\', '')}\n'
                    change = True
                # Don't print if there's an equal section since this is superfluous

            if change:
                print(changelog)
                if hash(changelog) in changes:
                    print(f'{day}-{'-'.join(j)} has the same changes as {changes[hash(changelog)]}')
                else:
                    changes[hash(changelog)] = f'{day}-{'-'.join(j)}'
                    print(changes)
                    with open(f'testresults/{day}-{'-'.join(j)}.txt', 'w') as fileout:
                        fileout.write(changelog)

            assert not change

