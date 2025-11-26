#!/usr/bin/env python3

# Copyright 2025 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import bottle
from bottle import get, route, request, static_file, error, template, redirect, abort
import requests
from datetime import datetime, date
import waitress
import logging

from logging.handlers import TimedRotatingFileHandler

import copy
import argparse
import re
import os
import json
import traceback

import breviarium
import datamanage
import prioritizer

import kalendar.datamanage
import kalendar.display as display

root = 'breviarium-1888'

def localehunt(acceptlanguage):
	# Get preferred locales
	acla = acceptlanguage.replace(', ', ',')
	langs = []
	index = 0
	for la in acla.split(','):
		match = re.search(r';q=([\d\.]+?)(,|$)', acla[acla.index(la):])
		# index is used to slightly devalue locales that are listed later but don't come with a q value (or have an equal q value with something else)
		if match is None:
			langs.append([la, index * -0.001])
		else:
			langs.append([la.split(';')[0], float(match.groups()[0]) - index * 0.001])
		index += 1

	# Sort locales to decide what user wants
	langs = [l[0] for l in sorted(langs, key=lambda l : l[1], reverse=True)]

	return langs

titles = {
	'pray': 'Rite Generator',
	'about': 'About',
	'help': 'Help the Liber Usualis Project',
	'donate': 'Donate',
	'credit': 'Credit'
}

definedlocales = ['en', 'de', 'la']
owntemplate = ['index']

@get('/')
def index():
	return redirect('/index')

@get('/index')
@get('/pray')
@get('/kalendar')
@get('/about')
@get('/credit')
@get('/donate')
@get('/help')
def bouncetolocale():
	page = request.route.rule[1:]
	locales = ['en']
	try:
		locales = localehunt(request.headers.get('Accept-Language'))
		locales.append('en')
	finally:
		return redirect(f'/{[loc for loc in locales if loc in definedlocales][0]}/{page}')

@get('/en/<page>')
@get('/de/<page>')
@get('/la/<page>')
def localpage(page):
	preferredlocale = request.route.rule[1:-7]
	title = titles[page] if page in titles else ''
	locales = [preferredlocale]
	try:
		locales.extend(localehunt(request.headers.get('Accept-Language')))
	finally:
		if not 'en' in locales:
			locales.append('en')
		for locale in locales:
			if page in owntemplate:
				if os.path.exists(f'web/locales/{locale}/pages/{page}.json'):
					return template('web/pages/index.tpl', locale=locale, preferredlocale=preferredlocale, text=json.load(open(f'web/locales/{locale}/pages/{page}.json')))
			else:
				if os.path.exists(f'web/locales/{locale}/pages/{page}.html') or os.path.exists(f'web/locales/{locale}/pages/{page}.json'):
					return template('web/resources/page.tpl', page=page, title=title, locale=locale, preferredlocale=preferredlocale)

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

def error500tpl(error):
	return template('web/resources/error500.tpl', error=error)

@get('/day')
def daytags(vesperal = False):
	parameters = copy.deepcopy(request.query)

	day = datetime.strptime(parameters['date'], '%Y-%m-%d').date()

	tags = copy.deepcopy(prioritizer.getvespers(day) if parameters['time'] == 'vesperale' else prioritizer.getdiurnal(day))

	pile = datamanage.getpile(root, flattensetlist(tags) | {'formulae'})

	primary = [i for i in tags if 'primarium' in i][0]
	commemorations = [[getname(tagset, pile), tagset] for tagset in sorted(list(filter(lambda a : 'commemoratio' in a, tags)), key=lambda a:breviarium.discriminate(root, 'rank', a), reverse=True)]
	omissions = [[getname(tagset, pile), tagset] for tagset in sorted(list(filter(lambda a : 'omissum' in a and not 'officium-parvum-bmv' in a, tags)), key=lambda a:breviarium.discriminate(root, 'rank', a), reverse=True)]
	votives = [['Officium Parvum B.M.V.', {'officium-parvum-bmv'}]]
	return datamanage.dump_data({
			'tags': tags,
			'primary': [getname(primary, pile), primary],
			'commemorations': commemorations,
			'omissions': omissions,
			'votives': votives
		})

# Returns raw JSON so that frontend can format it as it will
@get('/rite')
def rite():
	try:
		parameters = copy.deepcopy(request.query)

		# Generate the actual liturgical text. Didn't use breviarium.generate because of votive office handling
		day = datetime.strptime(parameters['date'], '%Y-%m-%d').date()
		hours = parameters['hour'].replace(' ', '+').split('+')
		assert set(hours).isdisjoint({'vesperae', 'completorium'}) or set(hours).isdisjoint({'matutinum', 'laudes', 'tertia', 'sexta', 'nona'})
		vesperal = not set(hours).isdisjoint({'vesperae', 'completorium'}) or ('time' in parameters and parameters['time'] == 'vesperale')

		tags = copy.deepcopy(prioritizer.getvespers(day) if vesperal else prioritizer.getdiurnal(day))

		# Handle the Little Office of the BVM and the Office of the Dead (temporary code)
		if 'select' in parameters:
			if parameters['select'] == 'officium-parvum-bmv':
				def votivize(i):
					if 'votiva' in i:
						return i | {'officium-parvum-bmv', 'maria', 'semiduplex', 'primarium'}
					else:
						return i - {'primarium', 'commemoratio', 'psalmi'}
				tags = [votivize(i) for i in tags]
				tags.append({'pro-sanctis','commemoratio'})
			elif parameters['select'] == 'officium-defunctorum':
				def votivize(i):
					if 'officium-defunctorum' in i:
						if 'duplex-minus' in i:
							return i | {'officium-defunctorum', 'primarium'}
						else:
							return i | {'officium-defunctorum', 'semiduplex', 'primarium'}
					else:
						return i - {'primarium', 'commemoratio', 'psalmi'}
				tags = [votivize(i) for i in tags]
				if not any('officium-defunctorum' in i for i in tags):
					tags.append({'officium-defunctorum','semiduplex','primarium'})
			elif parameters['select'] == 'antiphona-bmv-temporis':
				tags = list(filter(lambda i: 'antiphona-bmv-temporis' in i, tags))
				tags[0] |= {'primarium'}

		private = (parameters['privata'] == 'privata') if 'privata' in parameters else False
		if private:
			tags = [i | {'privata'} for i in tags]
		primary = [i for i in tags if 'primarium' in i][0]
		tags.remove(primary)
		pile = datamanage.getpile(root, breviarium.defaultpile | primary | set(hours))

		noending = (parameters['noending'] == 'true') if 'noending' in parameters else False
		if noending and not 'antiphona-bmv' in primary:
			tags.append({'fidelium-animae', 'hoc-omissum'} | set(hours))
			tags.append({'pater-noster-secreta-post-officium', 'hoc-omissum'} | set(hours))
		lit = []
		for hour in hours:
			lit.append({'ritus', hour})

		rite = breviarium.process(root, {'tags':{'ritus'},'datum':lit}, primary, tags, pile)
		tags.append(primary)

		translation = {}

	except Exception as e:
		traceback.print_exc()
		print(e)
		abort(500, error500tpl('Error incognitus.'))

	try:
		if 'translation' in parameters and parameters['translation'] != 'none':
			def gettranslation(tags):
				translation = parameters['translation']
				search = set(tags) | {translation}
				transroot = f'{root}/translations/{translation}'
				return breviarium.search(root, search, datamanage.getpile(transroot, primary | set(hours) | search | breviarium.defaultpile), rootappendix=f'/translations/{translation}')

			def traverse(obj):
				if type(obj) is dict and 'tags' in obj:
					tran = gettranslation(obj['tags'])
					if tran:
						translation['+'.join(sorted(obj['tags']))] = tran
				if type(obj) is dict:
					traverse(obj['datum'])
				elif type(obj) is list:
					for v in obj:
						traverse(v)
			traverse(rite['datum'])
	except Exception as e:
		traceback.print_exc()
		print(e)
		abort(500, error500tpl('Error de interpretatione.'))

	try:
		pile = datamanage.getpile(root, flattensetlist(tags) | {'formulae'})
		usednames = [getname(tagset, pile) for tagset in sorted(list(filter(lambda a : 'commemoratio' in a, tags)), key=lambda a:breviarium.discriminate(root, 'rank', a), reverse=True)]
		usednames.insert(0, getname(primary, pile))

		return datamanage.dump_data({
			'rite' : rite['datum'],
			'translation' : translation,
			'usedprimary': primary,
			'usednames': usednames
			})
	except Exception as e:
		traceback.print_exc()
		print(e)
		abort(500, error500tpl('Error incognitus.'))

@get('/kalendar')
def kal():
	return datamanage.getdisplaykalendar()

@get('/chant/<url:path>')
def chant(url):
	return datamanage.getchantfile(url)

@get('/resources/<file:path>')
def resources(file):
	return static_file(file, root='web/resources/')

@get('/logs/internal_requests')
def internal_requests():
	return static_file('internal_requests.log', root='../logs/')

@get('/favicon.ico')
def favicon():
	return static_file('agnus-dei.png', root='web/resources/')

@get('/robots.txt')
def robots():
	return static_file('robots.txt', root='web/resources/')

@error(404)
def error404(error):
	return 'Error 404'

@error(500)
def error500(error):
	return error.body

parser = argparse.ArgumentParser(description='Server')
parser.add_argument('-o', '--output', action='store_true', help='Display output in command line instead of in log file')
parser.add_argument('-a', '--addr', default='localhost', help='Set host address (only applies when -o is set)')
args = parser.parse_args()

if args.output:
	from bottle import run
	run(host=args.addr, port=8080)
else:
	from requestlogger import WSGILogger, ApacheFormatter
	waitress.serve(WSGILogger(
		bottle.default_app(), [TimedRotatingFileHandler('../logs/internal_requests.log', 'd', 7)],
		ApacheFormatter(), propagate=False
	))
