#!/usr/bin/env python3

# Copyright 2024 (AGPL-3.0-or-later), Miles K. Bertrand et al.

from bottle import get, route, request, run, static_file, error, template
import requests
from datetime import datetime, date

import copy

import breviarium
import datamanage
import prioritizer

import kalendar.datamanage

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

@get('/day')
def kalendar():
	parameters = copy.deepcopy(request.query)

	if not 'date' in parameters:
		parameters['date'] = date.today()
	else:
		parameters['date'] = datetime.strptime(parameters['date'], '%Y-%m-%d').date()

	tags = copy.deepcopy(prioritizer.getvespers(parameters['date']) if 'vesperae' in parameters['hour'] or 'completorium' in parameters['hour'] else prioritizer.getdiurnal(parameters['date']))

	for i in tags:
		for j in implicationtable:
			if j['tags'].issubset(i):
				i |= j['implies']
	return datamanage.dump_data(tags)

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

	rite = breviarium.generate(root, parameters['date'], parameters['hour'])
	translation = {}

	if 'translation' in parameters and parameters['translation'] == 'true':
		def gettranslation(tags):
			search = set(tags) | {parameters['translation']} | breviarium.defaultpile
			return breviarium.search(root, search, datamanage.getpile(f'{root}/translations/english', search), rootappendix='/translations/english')

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
		traverse(rite['datum'])

	tags = copy.deepcopy(prioritizer.getvespers(parameters['date']) if 'vesperae' in parameters['hour'] or 'completorium' in parameters['hour'] else prioritizer.getdiurnal(parameters['date']))
	commemorations = sorted(list(filter(lambda a : 'commemoratio' in a, tags)), key=lambda a:breviarium.discriminate(root, 'rank', a), reverse=True)
	noncomm = filter(lambda a : not a in commemorations, tags)
	tags = commemorations
	tags.extend(noncomm)
	pile = datamanage.getpile(root, flattensetlist(tags))
	names = []
	for i in tags:
		if not {'tempus','antiphona-bmv','psalmi'}.isdisjoint(i):
			names.append('')
		else:
			resp = breviarium.process(root, {'nomen'}, i, [], pile)
			name = resp['datum'] if 'datum' in resp else '+'.join(i)
			if type(name) is list:
				name = (name[0] + name[1]['datum']) if 'datum' in name[1] else '+'.join(i)
			names.append(name)

	return datamanage.dump_data({'rite' : rite['datum'], 'translation' : translation, 'day': tags, 'names': names})

@get('/chant/<url:path>')
def chant(url):
	return datamanage.getchantfile(url)

@get('/nomina')
def nomina():
	return datamanage.getnames(root)

@get('/resources/<file:path>')
def resources(file):
	return static_file(file, root='frontend/resources/')

@error(404)
def error404(error):
	return 'Error 404'

@error(500)
def error500(error):
	return error

@get('/reset')
def reset():
	datamanage.getyear.cache_clear()
	datamanage.getbreviariumfile.cache_clear()
	datamanage.getdiscrimina.cache_clear()
	return 'Successfully dumped data caches.'

run(host='localhost', port=8080)
