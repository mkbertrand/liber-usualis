#!/usr/bin/env python3

# Copyright 2025-2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import bottle
from bottle import get, route, request, static_file, error, template, redirect, abort
import requests
from datetime import datetime, date
import waitress
import logging
import warnings

from logging.handlers import TimedRotatingFileHandler

import copy
import argparse
import os
import json
import traceback

import breviarium
import datamanage
import kalendar.daily_tagger

import version_management

LOG_PATH = os.getenv("LOG_PATH", '../logs/internal_requests.log')

DEFAULT_CONTEXT = datamanage.LiturgicalContext(datamanage.get_book('breviarium-1888'), datamanage.get_book('martyrologium-1846'))

toplevelpages = [
    'index',
    'breviarium',
    'de-anno',
    'kalendar',
    'rubricae',
    'pray',
    'about',
    'credit',
    'donate',
    'help',
    'resources'
]

def findmytemplate(page):
    if page == 'pray':
        return 'web/templates/pray.tpl'
    elif page in ['index', 'breviarium']:
        return 'web/templates/menu.tpl'
    elif page in ['de-anno', 'kalendar', 'rubricae', 'resources']:
        return 'web/templates/latin-generic.tpl'
    else:
        return 'web/templates/generic.tpl'

@get('/')
def index():
    return redirect('/index')

@get(f'/<page:re:{'|'.join(toplevelpages)}>')
def bouncetolocale(page):
    locales = ['en']
    try:
        locales = version_management.localehunt(request.headers.get('Accept-Language'))
        if not 'en' in locales:
            locales.append('en')
    finally:
        return redirect(f'/{[loc for loc in locales if loc in version_management.definedlocales][0]}/{page}')

@get(f'/<preferredlocale:re:{'|'.join(version_management.definedlocales)}>/<page:re:{'|'.join(toplevelpages)}>')
def localpage(preferredlocale, page):
    locales = [preferredlocale]
    try:
        locales.extend(version_management.localehunt(request.headers.get('Accept-Language')))
    finally:
        if not 'en' in locales:
            locales.append('en')

        titles = ''
        for locale in locales:
            if os.path.exists(f'web/locales/{locale}/resources/page-titles.json'):
                titles = json.load(open(f'web/locales/{locale}/resources/page-titles.json'))
        title = titles[page] if page in titles else ''

        return template(findmytemplate(page), title=title, page=page, locales=locales, mobile=any(k in request.headers.get('User-Agent', '').lower() for k in ['mobile', 'android', 'iphone', 'ipad']))

def error500tpl(error):
    return template('web/resources/error500.tpl', error=error)

@get('/day')
def daytags(vesperal = False):
    parameters = copy.deepcopy(request.query)

    day = datetime.strptime(parameters['date'], '%Y-%m-%d').date()

    votives = parameters['votives'].replace(' ', '+').split('+')

    tags = copy.deepcopy(kalendar.daily_tagger.get_vespers(DEFAULT_CONTEXT, day, votives) if parameters['time'] == 'vesperale' else kalendar.daily_tagger.get_diurnal(DEFAULT_CONTEXT, day, votives))

    primary = [i for i in tags if 'primarium' in i][0]
    commemorations = [[datamanage.get_name(DEFAULT_CONTEXT, tagset), tagset] for tagset in sorted(list(filter(lambda a : 'commemoratio' in a, tags)), key=lambda a:breviarium.discriminate(DEFAULT_CONTEXT, 'rank', a), reverse=True)]
    omissions = [[datamanage.get_name(DEFAULT_CONTEXT, tagset), tagset] for tagset in sorted(list(filter(lambda a : 'omissum' in a and not 'officium-parvum-bmv' in a, tags)), key=lambda a:breviarium.discriminate(DEFAULT_CONTEXT, 'rank', a), reverse=True)]
    lectiocomm = [i for i in tags if 'commemoratio-matutini' in i]
    lectiocomm = lectiocomm[0] if len(lectiocomm) != 0 else None
    return datamanage.dump_data({
            'tags': tags,
            'primary': [datamanage.get_name(DEFAULT_CONTEXT, primary), primary],
            'commemorations': commemorations,
            'omissions': omissions,
            'commemoratio-matutini': [datamanage.get_name(DEFAULT_CONTEXT, lectiocomm), lectiocomm] if lectiocomm else None
        })

def adjust_tags(day, vesperal, select, votives):
    # Votives are simply a list of which votives the user wishes to be said if applicable. Providing a votive does not force its usage on inapplicable days.
    tags = copy.deepcopy(kalendar.daily_tagger.get_vespers(DEFAULT_CONTEXT, day, votives = votives) if vesperal else kalendar.daily_tagger.get_diurnal(DEFAULT_CONTEXT, day, votives = votives))

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

@get('/title')
def title():
    parameters = copy.deepcopy(request.query)
    votives = parameters['votives'].replace(' ', '+').split('+')
    try:
        day = datetime.strptime(parameters['date'], '%Y-%m-%d').date()
        hours = parameters['hour'].replace(' ', '+').split('+')
        tags = adjust_tags(day, not set(hours).isdisjoint({'vesperae', 'completorium', 'pro-coena'}), parameters['select'] if 'select' in parameters else 'diei', votives)
        primary = [i for i in tags if 'primarium' in i][0]
        return datamanage.dump_data([datamanage.get_name(DEFAULT_CONTEXT, primary), primary])
    except Exception as e:
        print(e)
        abort(400, text='Necesse est tibi reinitializare paginam. Error hoc datus est tibi propter versionem nimis veterem.')

expected_version = f'{version_management.get_resource_version('/js/ritegen.js')}-{version_management.get_resource_version('/styles/pray.css')}'
# Returns raw JSON so that frontend can format it as it will
@get('/rite')
def rite():
    parameters = copy.deepcopy(request.query)

    # Ensure requests were made by an up-to-date client
    try:
        assert parameters['version'] == expected_version
    except Exception as e:
        print(e)
        abort(400, text='Necesse est tibi reinitializare paginam. Error hoc datus est tibi propter versionem nimis veterem.')

    try:
        day = datetime.strptime(parameters['date'], '%Y-%m-%d').date()
        hours = parameters['hour'].replace(' ', '+').split('+')
        votives = parameters['votives'].replace(' ', '+').split('+')
        tags = adjust_tags(day, not set(hours).isdisjoint({'vesperae', 'completorium', 'pro-coena'}), parameters['select'] if 'select' in parameters else 'diei', votives)
        private = (parameters['privata'] == 'privata') if 'privata' in parameters else False
        if private:
            tags = [i | {'privata'} for i in tags]
        primary = [i for i in tags if 'primarium' in i][0]
        tags.remove(primary)

        noending = (parameters['noending'] == 'true') if 'noending' in parameters else False
        if noending and not 'antiphona-bmv' in primary:
            tags.append({'fidelium-animae', 'hoc-omissum'} | set(hours))
            tags.append({'pater-noster-secreta-post-officium', 'hoc-omissum'} | set(hours))
        lit = []
        for hour in hours:
            lit.append({'ritus', hour})

        rite = breviarium.process(DEFAULT_CONTEXT, {'tags':{'ritus'},'datum':lit}, primary, tags)
        tags.append(primary)

    except Exception as e:
        traceback.print_exc()
        print(e)
        abort(500, error500tpl('Error incognitus.'))

    try:
        if 'translation' in parameters and parameters['translation'] != 'none':
            def gettranslation(tags):
                translation = parameters['translation']
                search = set(tags) | {translation}
                translatedbooks = []
                for book in DEFAULT_CONTEXT.books:
                    if datamanage.data_root.joinpath('data').joinpath(f'{book.title}-{translation}').exists():
                        translatedbooks.append(datamanage.get_book(f'{book.title}-{translation}'))
                translated_context = datamanage.SecondaryLiturgicalContext(DEFAULT_CONTEXT.books, translatedbooks)
                return breviarium.search(translated_context, search)

            def traverse(obj):
                if type(obj) is dict and 'tags' in obj:
                    tran = gettranslation(obj['tags'])
                    if tran:
                        obj['translation'] = tran
                if type(obj) is dict:
                    traverse(obj['datum'])
                elif type(obj) is list:
                    for v in obj:
                        traverse(v)
            rite['datum'] = copy.deepcopy(rite['datum'])
            traverse(rite['datum'])
        
        def get_chant(tagset):
            chant_context = datamanage.SecondaryLiturgicalContext(DEFAULT_CONTEXT.books, [datamanage.LiturgicalBook(datamanage.data_root.joinpath('data-chant/gregobase'), 'gregobase')])
            warnings.simplefilter('ignore')
            return breviarium.search(chant_context, tagset)

        def traverse_chant(obj):
            if type(obj) is dict and 'quaesitum' in obj:
                tran = get_chant(obj['quaesitum'])
                if tran:
                    obj['cantus'] = tran
            if type(obj) is dict:
                traverse_chant(obj['datum'])
            elif type(obj) is list:
                for v in obj:
                    traverse_chant(v)
        rite['datum'] = copy.deepcopy(rite['datum'])
        traverse_chant(rite['datum'])
            
    except Exception as e:
        traceback.print_exc()
        print(e)
        abort(500, error500tpl('Error de interpretatione.'))

    try:
        lectiocomm = [i for i in tags if 'commemoratio-matutini' in i]
        lectiocomm = lectiocomm[0] if len(lectiocomm) != 0 else None
        return datamanage.dump_data({
            'rite' : rite['datum'],
            'used-primary': [datamanage.get_name(DEFAULT_CONTEXT, primary), primary],
            'used-commemorations': [[datamanage.get_name(DEFAULT_CONTEXT, tagset), tagset] for tagset in sorted(list(filter(lambda a : 'commemoratio' in a, tags)), key=lambda a:breviarium.discriminate(DEFAULT_CONTEXT, 'rank', a), reverse=True)],
            'commemoratio-matutini': [datamanage.get_name(DEFAULT_CONTEXT, lectiocomm), lectiocomm] if lectiocomm else None
            })
    except Exception as e:
        traceback.print_exc()
        print(e)
        abort(500, error500tpl('Error incognitus.'))

@get('/kalendar')
def kal():
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return datamanage.getdisplaykalendar(DEFAULT_CONTEXT)

@get('/chant/gregobase/euouae.json')
def euouae():
    return static_file('gregobase/untagged/euouae.json', root='data-chant/')

@get('/chant/<url:path>')
def chant(url):
    return datamanage.getchantfile(url)

@get('/resources/<file:path>')
def resources(file):
    return static_file(file, root='web/resources/')

@get('/logs/internal_requests')
def internal_requests():
    return static_file('internal_requests.log', root='../logs/')

@get('/favicon.ico')
def favicon():
    return static_file('agnus-dei.png', root='web/resources/')

@get('/robots.txt')
def robots():
    return static_file('robots.txt', root='web/resources/')

@error(404)
def error404(error):
    return 'Error 404'

@error(500)
def error500(error):
    return error.body

parser = argparse.ArgumentParser(description='Server')
parser.add_argument('-o', '--output', action='store_true', help='Display output in command line instead of in log file')
parser.add_argument('-a', '--addr', default='localhost', help='Set host address (only applies when -o is set)')
args = parser.parse_args()

if args.output:
    from bottle import run
    run(host=args.addr, port=8080)
else:
    from requestlogger import WSGILogger, ApacheFormatter
    waitress.serve(WSGILogger(
        bottle.default_app(), [TimedRotatingFileHandler(LOG_PATH, 'd', 7)],
        ApacheFormatter(), propagate=False
    ))
