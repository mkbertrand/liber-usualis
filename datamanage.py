# Copyright 2025-2026 (AGPL-4.0-or-later), Miles K. Bertrand et al.

from pathlib import Path
import json
import functools
import copy
from datetime import datetime, date

import kalendar.display as display
import kalendar.daily_tagger

from composer import Book
from composer import util
from composer import Corpus, ContingentCorpus

DATA_ROOT = Path(__file__).parent.joinpath('data').resolve()

def get_generated_book(title):
    return Book(DATA_ROOT.joinpath('generated').joinpath(title), title)

def get_book(title):
    return Book(DATA_ROOT.joinpath(title), title)

DEFAULT_CORPUS = Corpus(get_book('breviarium-1888'), get_book('martyrologium-1846'))
DEUTSCH_CORPUS = ContingentCorpus(DEFAULT_CORPUS.books, [get_book('breviarium-1888-deutsch')])
ENGLISH_CORPUS = ContingentCorpus(DEFAULT_CORPUS.books, [get_book('breviarium-1888-english')])
CHANT_CORPUS = ContingentCorpus(DEFAULT_CORPUS.books, [get_generated_book('liber-usualis-chant'), get_generated_book('fcc'), get_generated_book('liber-usualis-chant/nocturnale')])

@functools.lru_cache(maxsize=30)
def rite_request(date, item, votives, select, private, translation):
    day = datetime.strptime(date, '%Y-%m-%d').date()
    rite_tags = frozenset(item.replace(' ', '+').split('+'))
    votives = votives.replace(' ', '+').split('+')
    vesperal = not set(rite_tags).isdisjoint({'vesperae', 'completorium', 'pro-coena'})
    tags = copy.deepcopy(kalendar.daily_tagger.get_vespers(DEFAULT_CORPUS, day, votives = votives) if vesperal else kalendar.daily_tagger.get_diurnal(DEFAULT_CORPUS, day, votives = votives))
    if private:
        tags = [i | {'privata'} for i in tags]
    if not any('officium-defunctorum' in tagset for tagset in tags):
        time = [tagset - {'tempus'} for tagset in tags if 'tempus' in tagset][0]
        tags.append({'officium-defunctorum', 'omissum', 'semiduplex'} | time)

    # We could use the cum-opbmv tag to have separate functionality defined in a data-driven way but this is probably cleaner.
    if 'cum-opbmv' in rite_tags:
        tags = [i - {'omissum'} if 'officium-parvum-bmv' in i else i for i in tags]

    used_primary = [i for i in tags if select in i][0]
    tags.remove(used_primary)
    used_primary -= {'omissum'}

    print(rite_tags)
    print(used_primary)
    rite = DEFAULT_CORPUS.compose({'tags':{'ritus'},'datum':[rite_tags]}, used_primary, tags)
    tags.append(used_primary)

    if translation != 'none':
        translated_corpus = None
        if translation == 'deutsch':
            translated_corpus = DEUTSCH_CORPUS
        else:
            translated_corpus = ENGLISH_CORPUS
        rite = rite.superimpose(translated_corpus, 'translation')
    
    rite = rite.superimpose(CHANT_CORPUS, 'cantus')
    lectiocomm = [i for i in tags if 'commemoratio-matutini' in i]
    lectiocomm = lectiocomm[0] if len(lectiocomm) != 0 else None
    return {
        'text' : rite.rite['datum'],
        'used-primary': [DEFAULT_CORPUS.get_name(used_primary), used_primary],
        'used-commemorations': [[DEFAULT_CORPUS.get_name(tagset), tagset] for tagset in sorted(list(filter(lambda a : 'commemoratio' in a, tags)), key=lambda a:DEFAULT_CORPUS.discriminate('rank', a), reverse=True)],
        'commemoratio-matutini': [DEFAULT_CORPUS.get_name(lectiocomm), lectiocomm] if lectiocomm else None
        }

@functools.lru_cache(maxsize=1)
def getdisplaykalendar(context):
    ret = dict(sorted(display.kalendar(context).items()))
    ret = {str(k): [list(ent) for ent in v] for k, v in ret.items()}

    kalendar = display.kalendar2(context)
    for entry in kalendar:
        if type(entry['tags']) is frozenset:
            entry['tags'] = [entry['tags']]
        entry['names'] = [context.get_name(tagset) for tagset in entry['tags']]
        if any(i in entry['occurrence'] for i in ['feria-ii', 'feria-iii', 'feria-iv', 'feria-v', 'feria-vi', 'sabbatum']):
            entry['occurrence'] |= {'feria'}
        entry['occurrence-name'] = context.get_name(entry['occurrence'])
    return util.dump_data({'skeleton': ret, 'kalendar': kalendar})
