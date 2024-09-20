#!/usr/bin/env python3

import sys
from bottle import route, request, run, template, static_file, error, template, hook
from bottle import post, get
import requests
import pathlib
import json
from datetime import datetime, date

import copy
import warnings

from datamanage import getyear, getbreviariumfile, getdiscrimina
import breviarium
import datamanage

from frontend import chomp, renderer

@get('/json/tags')
def tag():
    parameters = copy.deepcopy(request.query)
    root = 'breviarium-1888'
    search = set(parameters['tags'].split('+')) | {'english'} | breviarium.defaultpile
    return breviarium.dump_data(breviarium.search(root, search, datamanage.getbreviariumfiles(root + '/translations/english', search), rootappendix='/translations/english'))

@get('/')
def index():
    return static_file('index.html', 'frontend/')

# Returns raw JSON so that frontend can format it as it will
@get('/ritual')
def ritual():
    parameters = copy.deepcopy(request.query)
    if not 'date' in parameters:
        parameters['date'] = date.today()
    else:
        parameters['date'] = datetime.strptime(parameters['date'], '%Y-%m-%d').date()

    if not 'hour' in parameters:
        match datetime.now().hour:
            case 0 | 1 | 2 | 3 | 4 | 5:
                parameters['hour'] = 'matutinum+laudes'
            case 6 | 7:
                parameters['hour'] = 'prima'
            case 8 | 9 | 10:
                parameters['hour'] = 'tertia'
            case 11 | 12 | 13:
                parameters['hour'] = 'sexta'
            case 14 | 15:
                parameters['hour'] = 'nona'
            case 16 | 17 | 18 | 19:
                parameters['hour'] = 'vesperae'
            case 20 | 21 | 22 | 23:
                parameters['hour'] = 'completorium'

    if ' ' in parameters['hour']:
        parameters['hour'] = parameters['hour'].replace(' ', '+')

    defpile = datamanage.getbreviariumfiles('breviarium-1888', breviarium.defaultpile)
    parameters['hour'] = 'ante-officium+' + parameters['hour'] + '+post-officium'
    ritual = [breviarium.hour('breviarium-1888', i, parameters['date'],
        forcedprimary=set(parameters['conditions'].split('+')) if 'conditions' in parameters else None) for i in parameters['hour'].split('+')]

    translation = {}
    if 'translation' in parameters:
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
        traverse(ritual)

    chant = {}
    if 'chant' in parameters:
        def traverse(obj):
            if type(obj) is dict and 'src' in obj:
                src = obj['src']
                tags = obj['tags'] if 'tags' in obj else ''
                if 'gregobase' in src and not src.endswith('&format=gabc'):
                    src = f'https://gregobase.selapa.net/download.php?id={src[src.index('/') + 1:]}&format=gabc&elem=1'
                gabc = chomp.chomp(datamanage.getchantfile(src), tags)
                assert not "\"" in gabc
                chant[obj['src'] + ';' + '+'.join(tags)] = gabc
            if type(obj) is dict:
                traverse(obj['datum'])
            elif type(obj) is list:
                for v in obj:
                    traverse(v)
        traverse(ritual)

    return breviarium.dump_data({'translation' : translation, 'chant': chant, 'ritual' : ritual})

@route('/styles/<file>')
def styles(file):
    return static_file(file, root='frontend/styles/')

@get('/chant/<url:path>')
def chant(url):
    if 'gregobase' in url and not url.endswith('&format=gabc'):
        url = f'https://gregobase.selapa.net/download.php?id={url[url.index('/') + 1:]}&format=gabc&elem=1'
    response = datamanage.getchantfile(url)
    return chomp.chomp(response, request.query['tags'].replace(' ', '+') if 'tags' in request.query else '')

@route('/js/<file:path>')
def javascript(file):
    return static_file(file, root='frontend/js/')

@route('/resources/<file:path>')
def resources(file):
    return static_file(file, root='frontend/resources/')

@error(404)
def error404(error):
    return 'Error 404'

@route('/reset')
def reset():
    getyear.cache_clear()
    getbreviariumfile.cache_clear()
    getdiscrimina.cache_clear()
    return 'Successfully dumped data caches.'

run(host='localhost', port=8080)
