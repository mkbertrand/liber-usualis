#!/usr/bin/env python3

# Copyright 2024 (AGPL-3.0-or-later), Miles K. Bertrand et al.

from bottle import get, route, request, run, static_file, error, template
import requests
from datetime import datetime, date

import copy

import breviarium
import datamanage
import prioritizer

import chomp

root = 'breviarium-1888'

implicationtable = datamanage.load_data(f'data/{root}/tag-implications.json')

@get('/')
def indexserve():
    return pageserve('index', 'Rite Generator')

@get('/about/')
def aboutserve():
    return pageserve('about', 'About')

@get('/credit/')
def aboutserve():
    return pageserve('credit', 'Credit')

@get('/help/')
def aboutserve():
    return pageserve('help', 'Help the Liber Usualis Project')

def pageserve(page, title):
    return template('frontend/resources/page.tpl', page=page, title=title)

def flattensetlist(sets):
    ret = set()
    for i in sets:
        ret |= i
    return ret

# Returns raw JSON so that frontend can format it as it will
@get('/rite')
def rite():
    parameters = copy.deepcopy(request.query)

    if not 'date' in parameters:
        parameters['date'] = date.today()
    else:
        parameters['date'] = datetime.strptime(parameters['date'], '%Y-%m-%d').date()

    if ' ' in parameters['hour']:
        parameters['hour'] = parameters['hour'].replace(' ', '+')

    defpile = datamanage.getbreviariumfiles(root, breviarium.defaultpile)

    rite = []
    rite.append(breviarium.process(root, {'ante-officium'}, None, None, defpile))

    for hour in parameters['hour'].split('+'):
        tags = copy.deepcopy(prioritizer.getvespers(parameters['date']) if hour == 'vesperae' or hour == 'completorium' else datamanage.getdate(parameters['date']))
        for i in tags:
            for j in implicationtable:
                if j['tags'].issubset(i):
                    i |= j['implies']
        pile = datamanage.getbreviariumfiles(root, breviarium.defaultpile | flattensetlist(tags) | set(parameters['hour'].split('+')))
        tags = [frozenset(i) for i in tags]
        primary = list(filter(lambda i: 'primarium' in i, tags))[0]
        tags.remove(primary)
        rite.append(breviarium.process(root, {'nomen-ritus'}, primary | {hour}, tags, pile))
        rite.append(breviarium.process(root, {hour, 'hora'}, primary | {hour}, tags, pile))

    rite.append(breviarium.process(root, {'post-officium'}, None, None, defpile))

    translation = {}
    if 'translation' in parameters and parameters['translation'] == 'true':
        def gettranslation(tags):
            search = set(tags) | {parameters['translation']} | breviarium.defaultpile
            return breviarium.search(root, search, datamanage.getbreviariumfiles(f'{root}/translations/english', search), rootappendix='/translations/english')

        def traverse(obj):
            if type(obj) is dict and 'tags' in obj:
                tran = gettranslation(obj['tags'])
                if tran:
                    translation['+'.join(obj['tags'])] = tran
            if type(obj) is dict:
                traverse(obj['datum'])
            elif type(obj) is list:
                for v in obj:
                    traverse(v)
        traverse(rite)

    return breviarium.dump_data({'rite' : rite, 'translation' : translation})

@get('/chant/<url:path>')
def chant(url):
    if 'gregobase' in url and not url.endswith('&format=gabc'):
        url = f'https://gregobase.selapa.net/download.php?id={url[url.index('/') + 1:]}&format=gabc&elem=1'
    response = datamanage.getchantfile(url)
    return chomp.chomp(datamanage.getchantfile(url), request.query['tags'].replace(' ', '+').split('+') if 'tags' in request.query else set())

@get('/nomina')
def nomina():
    return datamanage.getnames(root)

@route('/resources/<file:path>')
def resources(file):
    return static_file(file, root='frontend/resources/')

@error(404)
def error404(error):
    return 'Error 404'

@error(500)
def error500(error):
    return error

@route('/reset')
def reset():
    datamanage.getyear.cache_clear()
    datamanage.getbreviariumfile.cache_clear()
    datamanage.getdiscrimina.cache_clear()
    return 'Successfully dumped data caches.'

run(host='localhost', port=8080)
