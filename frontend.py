#!/usr/bin/env python3

import sys
from bottle import route, run, template, static_file, error, template, hook
from bottle import post, get
import requests
import pathlib
import json
from datetime import datetime, date

from datamanage import getyear, getbreviariumfile
import breviarium
import datamanage

from frontend import renderer

loadchant = True

@route('/hora/<day>/<hour>')
def office(day, hour):
    defpile = datamanage.getbreviariumfiles(breviarium.defaultpile)
    ret = renderer.render(breviarium.process({'ante-officium'}, None, defpile), loadchant)
    for i in hour.split(' '):
        ret += renderer.render(breviarium.hour(i, datetime.strptime(day, '%Y-%m-%d').date()), loadchant)
        ret += renderer.render(breviarium.process({'post-officium'}, None, defpile), loadchant)
    return template('frontend/index.tpl',office=ret)

@route('/hora/<hour>')
def office(hour):
    ret = ''
    for i in hour.split(' '):
        ret += renderer.render(breviarium.hour(i, date.today()), loadchant)
    return template('frontend/index.tpl',office=ret)

@route('/hora/')
def index():
    hour = None
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
    return office(hour)

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
    return renderer.chomp(response, tags)

@route('/data/<version>/<query:path>:tabe 
@route('/js/<file:path>')
def javascript(file):
    return static_file(file, root='frontend/js/')

@error(404)
def error404(error):
    return 'Error 404'

@route('/forcereload')
def forcereload():
    getyear.cache_clear()
    getbreviariumfile.cache_clear()
    return 'Successfully dumped data caches.'

run(host='localhost', port=8000)
