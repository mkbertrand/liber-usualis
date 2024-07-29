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

from datamanage import getyear, getbreviariumfile
import breviarium
import datamanage

from frontend import chomp, renderer

@get('/json/tags')
def tag():
    parameters = copy.deepcopy(request.query)
    root = 'breviarium-1888/translations/english'
    search = set(parameters['tags'].split(' ')) | {'english'} | breviarium.defaultpile
    return breviarium.dump_data(breviarium.search(root, search, datamanage.getbreviariumfiles(root, search)))

@get('/breviarium')
def breviary():
    parameters = copy.deepcopy(request.query)
    if not 'date' in parameters:
        parameters['date'] = date.today()
    else:
        parameters['date'] = datetime.strptime(parameters['date'], '%Y-%m-%d').date()

    if not 'hour' in parameters:
        match datetime.now().hour:
            case 0 | 1 | 2 | 3 | 4 | 5:
                hour = 'matutinum laudes'
            case 6 | 7:
                hour = 'prima'
            case 8 | 9 | 10:
                hour = 'tertia'
            case 11 | 12 | 13:
                hour = 'sexta'
            case 14 | 15:
                hour = 'nona'
            case 16 | 17 | 18 | 19:
                hour = 'vesperae'
            case 20 | 21 | 22 | 23:
                hour = 'completorium'

    parameters['chant'] = parameters['chant'] == 'true' if 'chant' in parameters else False

    defpile = datamanage.getbreviariumfiles('breviarium-1888', breviarium.defaultpile)
    parameters['hour'] = 'ante-officium ' + parameters['hour'] + ' post-officium'
    ret = ''
    for i in parameters['hour'].split(' '):
        ret += renderer.render(
                breviarium.hour('breviarium-1888', i, parameters['date'], forcedprimary=set(parameters['conditions'].split(' ')) if 'conditions' in parameters else None),
                parameters)
    return template('frontend/index.tpl',office=ret)

@route('/styles/<file>')
def styles(file):
    return static_file(file, root='frontend/styles/')

@get('/chant/gregobase/<id>/<tags>')
def gregobase(id, tags= ''):
    return chant(f'https://gregobase.selapa.net/download.php?id={id}&format=gabc&elem=1', tags)

@get('/chant/<url:path>/<tags>')
def chant(url, tags = ''):
    if 'gregobase' in url and not url.endswith('&format=gabc'):
        url = f'https://gregobase.selapa.net/download.php?id={url[url.index('id=') + 3:]}&format=gabc&elem=1'
    response = requests.get(url, stream=True).text
    return chomp.chomp(response, tags)

@route('/js/<file:path>')
def javascript(file):
    return static_file(file, root='frontend/js/')

@route('/resources/<file:path>')
def resources(file):
    return static_file(file, root='frontend/resources/')

@error(404)
def error404(error):
    return 'Error 404'

@route('/forcereload')
def forcereload():
    getyear.cache_clear()
    getbreviariumfile.cache_clear()
    return 'Successfully dumped data caches.'

run(host='localhost', port=8080)
