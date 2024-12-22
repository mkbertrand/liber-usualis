import functools
import copy
from typing import NamedTuple

import kalendar.kalendar as kalendar

class Restriction(NamedTuple):
	include: set
	exclude: set

def flatten(table):
	rules = []
	rulenumber = 0
	for i in copy.deepcopy(table):
		if not 'exclude' in i:
			i['exclude'] = None
		if not 'recheck' in i:
			i['recheck'] = True
		if not 'continue' in i:
			i['continue'] = True
		i['restrict'] = [Restriction(i['include'], i['exclude'])]
		if type(i['response']) is str:
			i['target'] = 0
			i['number'] = rulenumber
			rules.append(i)
			rulenumber += 1
		else:
			for j in i['response']:
				if not 'exclude' in j:
					j['exclude'] = None
				j['restrict'] = [i['restrict'][0], Restriction(j['include'], j['exclude'])]
				j['number'] = rulenumber
				if not 'recheck' in j:
					j['recheck'] = i['recheck']
				if not 'continue' in j:
					j['continue'] = i['continue']
				rules.append(j)
				rulenumber += 1
	return rules

@functools.lru_cache(maxsize=16)
def getyear(year):
    return kalendar.kalendar(year)

def getdate(day):
    year = getyear(day.year)
    return year[day]
