from bottle import route, run, template

import breviarum
from datetime import date
from datamanage import getyear, getbreviarumfile
@route('/breviarum/<hour>')
def index(hour):
    return breviarum.dump_data(breviarum.hour(hour, date.today()))

@route('/forcereload')
def forcereload():
    getyear.cache_clear()
    getbreviarumfile.cache_clear()
    return 'Successfully dumped data caches.'

run(host='localhost',port=8080)

