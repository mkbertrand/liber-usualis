# Copyright 2025-2026 (AGPL-4.0-or-later), Miles K. Bertrand et al.

from pathlib import Path
import json
import functools
import copy
import traceback
import warnings
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

def adjust_tags(day, vesperal, select, votives):
    # Votives are simply a list of which votives the user wishes to be said if applicable. Providing a votive does not force its usage on inapplicable days.
    tags = copy.deepcopy(kalendar.daily_tagger.get_vespers(DEFAULT_CORPUS, day, votives = votives) if vesperal else kalendar.daily_tagger.get_diurnal(DEFAULT_CORPUS, day, votives = votives))

    # Handle the Little Office of the BVM and the Office of the Dead (temporary code)
    if select == 'officium-parvum-bmv':
        templ = list(filter(lambda i: 'pro-aliis-officiis' in i, tags))[0]
        ofp = list(filter(lambda i: 'officium-parvum-bmv' in i, tags))[0]
        tags = [ofp - {'omissum'} | {'primarium'}, templ | {'pro-sanctis', 'commemoratio'}, list(filter(lambda i: 'antiphona-bmv-temporis' in i, tags))[0]]
    elif select == 'officium-defunctorum':
        def votivize(i):
            if 'officium-defunctorum' in i:
                if 'duplex-minus' in i:
                    return i | {'officium-defunctorum', 'primarium'}
                else:
                    return i | {'officium-defunctorum', 'semiduplex', 'primarium'}
            else:
                return i - {'primarium', 'commemoratio', 'psalmi'}
        tags = [votivize(i) for i in tags]
        if not any('officium-defunctorum' in i for i in tags):
            tags.append({'officium-defunctorum','semiduplex','primarium'})
    elif select == 'antiphona-bmv-temporis':
        tags = list(filter(lambda i: 'antiphona-bmv-temporis' in i, tags))
        tags[0] |= {'primarium'}

    return tags

@functools.lru_cache(maxsize=30)
def rite_request(date, rites, votives, select, private, noending, translation):
    day = datetime.strptime(date, '%Y-%m-%d').date()
    hours = rites.replace(' ', '+').split('+')
    votives = votives.replace(' ', '+').split('+')
    tags = adjust_tags(day, not set(hours).isdisjoint({'vesperae', 'completorium', 'pro-coena'}), select, votives)
    if private:
        tags = [i | {'privata'} for i in tags]
    primary = [i for i in tags if 'primarium' in i][0]
    tags.remove(primary)

    if noending and not 'antiphona-bmv' in primary:
        tags.append({'fidelium-animae', 'hoc-omissum'} | set(hours))
        tags.append({'pater-noster-secreta-post-officium', 'hoc-omissum'} | set(hours))
    lit = []
    for hour in hours:
        lit.append({'ritus', hour})

    rite = DEFAULT_CORPUS.compose({'tags':{'ritus'},'datum':lit}, primary, tags)
    tags.append(primary)

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
        'rite' : rite.rite['datum'],
        'used-primary': [DEFAULT_CORPUS.get_name(primary), primary],
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
