#!/usr/bin/env python3

# Copyright 2025-2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import bottle
from bottle import get, route, request, static_file, error, template, redirect, abort
import requests
from datetime import datetime, date
import waitress
import logging
import warnings
import traceback

from logging.handlers import TimedRotatingFileHandler

import copy
import argparse
import os
import json

import functools

import datamanage
import kalendar.daily_tagger
from composer import util

import version_management

LOG_PATH = os.getenv("LOG_PATH", '../logs/internal_requests.log')

toplevelpages = [
    'index',
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
    elif page in ['index']:
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

@get(f'/<preferredlocale:re:{'|'.join(version_management.definedlocales)}>/<page:re:pray>/<date>/<time>')
def pray(preferredlocale, page, date, time):
    return localpage(preferredlocale, page)

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

    tags = copy.deepcopy(kalendar.daily_tagger.get_vespers(datamanage.DEFAULT_CORPUS, day, votives) if parameters['time'] == 'vesperale' else kalendar.daily_tagger.get_diurnal(datamanage.DEFAULT_CORPUS, day, votives))

    primary = [i for i in tags if 'primarium' in i][0]
    commemorations = [[datamanage.DEFAULT_CORPUS.get_name(tagset), tagset] for tagset in sorted(list(filter(lambda a : 'commemoratio' in a, tags)), key=lambda a:datamanage.DEFAULT_CORPUS.discriminate('rank', a), reverse=True)]
    omissions = [[datamanage.DEFAULT_CORPUS.get_name(tagset), tagset] for tagset in sorted(list(filter(lambda a : 'omissum' in a and not 'officium-parvum-bmv' in a, tags)), key=lambda a:datamanage.DEFAULT_CORPUS.discriminate('rank', a), reverse=True)]
    lectiocomm = [i for i in tags if 'commemoratio-matutini' in i]
    lectiocomm = lectiocomm[0] if len(lectiocomm) != 0 else None
    return util.dump_data({
            'tags': tags,
            'primary': [datamanage.DEFAULT_CORPUS.get_name(primary), primary],
            'commemorations': commemorations,
            'omissions': omissions,
            'commemoratio-matutini': [datamanage.DEFAULT_CORPUS.get_name(lectiocomm), lectiocomm] if lectiocomm else None
        })

@get('/title')
def title():
    parameters = copy.deepcopy(request.query)
    votives = parameters['votives'].replace(' ', '+').split('+')
    try:
        day = datetime.strptime(parameters['date'], '%Y-%m-%d').date()
        hours = parameters['hour'].replace(' ', '+').split('+')
        tags = datamanage.adjust_tags(day, not set(hours).isdisjoint({'vesperae', 'completorium', 'pro-coena'}), parameters['select'] if 'select' in parameters else 'diei', votives)
        primary = [i for i in tags if 'primarium' in i][0]
        return util.dump_data([datamanage.DEFAULT_CORPUS.get_name(primary), primary])
    except Exception as e:
        print(e)
        abort(400, text='Necesse est tibi reinitializare paginam. Error hoc datus est tibi propter versionem nimis veterem.')

expected_version = f'{version_management.get_resource_version('/pray/js/ritegen.js')}-{version_management.get_resource_version('/pray/css/pray.css')}'

# Returns raw JSON so that frontend can format it as it will
@get('/rite')
def rite():
    # Ensure requests were made by an up-to-date client
    try:
        assert request.query.get('version', expected_version) == expected_version
    except Exception as e:
        print(e)
        abort(400, text='Necesse est tibi reinitializare paginam. Error hoc datus est tibi propter versionem nimis veterem.')

    try:
        rites = request.query.get('rites', None)
        if rites:
            ret = []
            rites = rites.split('_')
            for rite in rites:
                ritesplit = rite.split('.')
                ret.append(datamanage.rite_request(
                    request.query.get('date'),
                    ritesplit[0],
                    request.query.get('votives', ''),
                    ritesplit[2],
                    request.query.get('privata', '') == 'privata',
                    ritesplit[1],
                    request.query.get('translation', 'none'),
                    request.query.get('chant', 'false') == 'true'
                ))
            return util.dump_data(ret)
        return util.dump_data(datamanage.rite_request(
            request.query.get('date'),
            request.query.get('hour'),
            request.query.get('votives', ''),
            request.query.get('select', 'diei'),
            request.query.get('privata', '') == 'privata',
            request.query.get('noending', 'false') == 'true',
            request.query.get('translation', 'none'),
            request.query.get('chant', 'false') == 'true'
        ))
    except Exception as e:
        traceback.print_exc()
        print(e)
        abort(500, error500tpl('Error incognitus.'))

@get('/kalendar')
def kal():
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return datamanage.getdisplaykalendar(datamanage.DEFAULT_CORPUS)

@get('/chant/<file:path>')
def chant(file):
    return static_file(file, root=datamanage.DATA_ROOT.joinpath('generated'))

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
