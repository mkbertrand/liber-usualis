import sys
from bottle import route, run, template, static_file, error, template
import pathlib
import json
from datetime import datetime, date

from datamanage import getyear, getbreviariumfile
import breviarium

data_root = pathlib.Path(__file__).parent

def load(p):
    data_root.joinpath(p).read_text(encoding='utf-8')

def stringhandle(line):
    line = line.replace('/', '<br>').replace('N.','<span class=red>N.</span>').replace('V. ', '<span class=red>&#8483;.</span> ').replace('R. br. ', '<span class=red>&#8479;. br. </span> ').replace('R. ', '<span class=red>&#8479;.</span> ').replace('✠', '<span class=red>✠</span>').replace('✙', '<span class=red>✙</span>').replace('+', '<span class=red>†</span>').replace('*', '<span class=red>*</span>')
    return f'<p class=text-line>{line}</p>'

def jsoninterp(j):
    def recurse(obj):
        match obj:
            case dict():
                if {'formula','responsorium-breve'}.issubset(set(obj['tags'])):
                    incipit = obj['datum'][0]['datum'] if 'datum' in obj['datum'][0] else 'Absens'
                    responsum = obj['datum'][1]['datum'] if 'datum' in obj['datum'][1] else 'Absens'
                    versus = obj['datum'][4]['datum'] if 'datum' in obj['datum'][2] else 'Absens'
                    return recurse([
                        f'R. br. {incipit} * {responsum}',
                        f'R. {incipit} * {responsum}',
                        f'V. {versus}',
                        f'R. {responsum}',
                        f'V. {obj["datum"][6]}',
                        f' R. {incipit} * {responsum}'
                    ])
                else:
                    return recurse(obj['datum'])
            case list():
                return ''.join([recurse(v) for v in obj])
            case str():
                return stringhandle(obj) 
    return recurse(j)

@route('/<hour>')
def office(hour):
    ret = ''
    for i in hour.split(' '):
        ret += jsoninterp(breviarium.hour(i, date.today()))
    return template('frontend/index.tpl',office=ret)

@route('/')
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

@route('/js/<file>')
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
