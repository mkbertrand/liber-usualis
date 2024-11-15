#!/usr/bin/env python3

# Copyright 2024 (AGPL-3.0-or-later), Miles K. Bertrand et al.

from bottle import route, run, template

import breviarium
from datetime import date
from datamanage import getyear, getbreviariumfile
@route('/breviarium/<hour>')
def index(hour):
    return breviarium.dump_data(breviarium.hour(hour, date.today()))

@route('/forcereload')
def forcereload():
    getyear.cache_clear()
    getbreviariumfile.cache_clear()
    return 'Successfully dumped data caches.'

run(host='localhost',port=8080)

