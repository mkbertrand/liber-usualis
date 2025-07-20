#!/usr/bin/env python3

# Copyright 2025 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import bottle
from bottle import get, route, request, static_file, error, template
import requests
from datetime import datetime, date
from requestlogger import WSGILogger, ApacheFormatter
import waitress
import logging

from logging.handlers import TimedRotatingFileHandler

import copy

import breviarium
import datamanage
import prioritizer

import kalendar.datamanage

root = 'breviarium-1888'

implicationtable = datamanage.load_data(f'data/{root}/tag-implications.json')

@get('/')
def indexserve():
	return static_file('index.html', root='frontend/pages/')

@get('/pray/')
def prayserve():
	return pageserve('pray', 'Rite Generator')

@get('/about/')
def aboutserve():
	return pageserve('about', 'About')

@get('/credit/')
def aboutserve():
	return pageserve('credit', 'Credit')

@get('/donate/')
def donateserve():
	return pageserve('donate', 'Donate')

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

def getname(tagset, pile):
	resp = breviarium.process(root, {'nomen'}, tagset, [], pile)
	name = resp['datum'] if 'datum' in resp else '+'.join(tagset)
	if type(name) is list:
		name = (name[0] + name[1]['datum']) if 'datum' in name[1] else '+'.join(tagset)
	return name

def daytags(vesperal = False):
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

	pile = datamanage.getpile(root, flattensetlist(tags) | {'formulae'})

	primary = list(filter(lambda i: 'primarium' in i, tags))[0]
	commemorations = [[getname(tagset, pile), tagset] for tagset in sorted(list(filter(lambda a : 'commemoratio' in a, tags)), key=lambda a:breviarium.discriminate(root, 'rank', a), reverse=True)]
	omissions = [[getname(tagset, pile), tagset] for tagset in sorted(list(filter(lambda a : 'omissum' in a, tags)), key=lambda a:breviarium.discriminate(root, 'rank', a), reverse=True)]
	votives = [['Officium Parvum B.M.V.', {'officium-parvum-bmv'}]]
	return {
			'tags': tags,
			'primary': [getname(primary, pile), primary],
			'commemorations': commemorations,
			'omissions': omissions,
			'votives': votives
		}

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

	# Generate the actual liturgical text. Didn't use breviarium.generate because of votive office handling
	day = parameters['date']
	hour = parameters['hour']
	hours = hour.split('+')
	assert set(hours).isdisjoint({'vesperae', 'completorium'}) or set(hours).isdisjoint({'matutinum', 'laudes', 'tertia', 'sexta', 'nona'})

	vesperal = not set(hours).isdisjoint({'vesperae', 'completorium'})

	tags = copy.deepcopy(prioritizer.getvespers(day) if vesperal else prioritizer.getdiurnal(day))
	for i in tags:
		for j in implicationtable:
			if j['tags'].issubset(i):
				i |= j['implies']

	tags = [frozenset(i) for i in tags]

	# Handle the Little Office of the BVM
	if 'select' in parameters and parameters['select'] == 'officium-parvum-bmv':
		def votivize(i):
			if 'votiva' in i:
				return i | {'officium-parvum-bmv', 'maria', 'semiduplex', 'primarium'}
			else:
				return i - {'primarium', 'commemoratio', 'psalmi'}
		tags = [votivize(i) for i in tags]
		tags.append({'pro-sanctis','commemoratio'})

	primary = list(filter(lambda i: 'primarium' in i, tags))[0]
	tags.remove(primary)
	pile = datamanage.getpile(root, breviarium.defaultpile | primary | set(hours))

	lit = []
	for hour in hours:
		lit.append({'hora', hour})
	rite = breviarium.process(root, {'tags':{'ritus'},'datum':lit}, primary, tags, pile)
	tags.append(primary)

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

	pile = datamanage.getpile(root, flattensetlist(tags) | {'formulae'})
	usednames = [getname(tagset, pile) for tagset in sorted(list(filter(lambda a : 'commemoratio' in a, tags)), key=lambda a:breviarium.discriminate(root, 'rank', a), reverse=True)]
	usednames.insert(0, getname(primary, pile))

	return datamanage.dump_data({
		'rite' : rite['datum'],
		'translation' : translation,
		'day': daytags(vesperal = vesperal),
		'usedprimary': primary,
		'usednames': usednames
		})

@get('/chant/<url:path>')
def chant(url):
	return datamanage.getchantfile(url)

@get('/resources/<file:path>')
def resources(file):
	return static_file(file, root='frontend/resources/')

@get('/logs/internal_requests')
def internal_requests():
	return static_file('internal_requests.log', root='../logs/')

@get('/favicon.ico')
def favicon():
	return static_file('agnus-dei.png', root='frontend/resources/')

@get('/robots.txt')
def robots():
	return static_file('robots.txt', root='frontend/resources/')

@error(404)
def error404(error):
	return 'Error 404'

@error(500)
def error500(error):
	return error

waitress.serve(WSGILogger(
	bottle.default_app(), [TimedRotatingFileHandler('../logs/internal_requests.log', 'd', 7)],
	ApacheFormatter(), propagate=False
))
