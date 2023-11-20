from bottle import route, run, template

import breviarum
from datetime import date

@route('/breviarum/<hour>')
def index(hour):
    return breviarum.dump_data(breviarum.hour(hour, date.today()))

run(host='localhost',port=8080)

