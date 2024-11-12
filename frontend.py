#!/usr/bin/env python3

from bottle import get, route, request, run, static_file, error
import requests
from datetime import datetime, date

import copy

import breviarium
import datamanage
import prioritizer

from frontend import chomp

implicationtable = datamanage.load_data('data/breviarium-1888/tag-implications.json')

@get('/')
def index():
    return static_file('index.html', 'frontend/')

def flattensetlist(sets):
    ret = set()
    for i in sets:
        ret |= i
    return ret

# Returns raw JSON so that frontend can format it as it will
@get('/rite')
def rite():
    parameters = copy.deepcopy(request.query)
    root = 'breviarium-1888'

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
        rite.append(breviarium.process(root, {hour, 'hora'}, primary | {hour}, tags, pile))

    rite.append(breviarium.process(root, {'post-officium'}, None, None, defpile))

    translation = {}
    if 'translation' in parameters and parameters['translation'] == 'true':
        def gettranslation(tags):
            search = set(tags) | {parameters['translation']} | breviarium.defaultpile
            return breviarium.search('breviarium-1888', search, datamanage.getbreviariumfiles('breviarium-1888/translations/english', search), rootappendix='/translations/english')

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

    tags = copy.deepcopy(prioritizer.getvespers(parameters['date']) if 'vesperae' in parameters['hour'] or 'completorium' in parameters['hour']  else datamanage.getdate(parameters['date']))
    nomina = datamanage.getnames(root)
    name = ' et '.join([i.capitalize() for i in parameters['hour'].split('+')])
    return breviarium.dump_data({'rite' : rite, 'translation' : translation, 'name': name})

@route('/styles/<file>')
def styles(file):
    return static_file(file, root='frontend/styles/')

@get('/chant/<url:path>')
def chant(url):
    if 'gregobase' in url and not url.endswith('&format=gabc'):
        url = f'https://gregobase.selapa.net/download.php?id={url[url.index('/') + 1:]}&format=gabc&elem=1'
    response = datamanage.getchantfile(url)
    return chomp.chomp(datamanage.getchantfile(url), request.query['tags'].replace(' ', '+').split('+') if 'tags' in request.query else set())

@route('/js/<file:path>')
def javascript(file):
    return static_file(file, root='frontend/js/')

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
