# Copyright 2025 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import os.path
import json
import pathlib
from datetime import date, datetime, timedelta
import re
from typing import NamedTuple
import itertools
import copy

from kalendar import kalendar

import kalendar.datamanage
import kalendar.luna as luna

data_root = pathlib.Path(__file__).parent

def load_data(p: str):
	data = json.loads(data_root.joinpath(p).read_text(encoding='utf-8'))

	# JSON doesn't support sets. Recursively find and replace anything that
	# looks like a list of tags with a set of tags.
	def recurse(obj):
		match obj:
			case dict():
				return {datetime.strptime(k, '%Y-%m-%d').date() if re.search(r'^\d{4}-\d{2}-\d{2}$',k) is not None else k: recurse(v) for k, v in obj.items()}
			case list():
				if all(type(x) is str for x in obj):
					return frozenset(obj)
				return [recurse(v) for v in obj]
			case _:
				return obj

	return recurse(data)

vesperalrules = kalendar.datamanage.flatten(load_data('kalendar/data/tabella-vesperalis.json'))
diurnalrules = kalendar.datamanage.flatten(load_data('kalendar/data/tabella-diurnalis.json'))
martyrologyrules = kalendar.datamanage.flatten(load_data('kalendar/data/tabella-martyrologii.json'))

class Job(NamedTuple):
	rule: dict

def guaranteeset(item):
	if type(item) is set or type(item) is frozenset:
		return item
	else:
		return {item}

def prioritize(day, rules):
	day = copy.deepcopy(day)
	queue = [Job(rule) for rule in rules]
	queue.reverse()
	ruleskip = [False] * len(rules)

	def resolvejob(job):

		if ruleskip[job.rule['number']]:
			return
		# If we have reached a rule following a rule which shouldn't be rechecked, mark it off as done
		if not rules[job.rule['number'] - 1]['recheck']:
			ruleskip[job.rule['number'] - 1] = True

		tagsetindices = range(len(day))
		matchset = []
		for restriction in job.rule['restrict']:
			search = [tagsetindex for tagsetindex in tagsetindices if restriction.include <= day[tagsetindex] and not (restriction.exclude and restriction.exclude <= day[tagsetindex])]
			if len(search) == 0:
				return
			else:
				matchset.append(search)

		matches = list(itertools.product(*matchset))

		for match in matches:
			if len(set(match)) == len(job.rule['restrict']):

				# In instructions to add/switch around tags, the mutate response is assumed (as opposed to duplicate to make a modified copy of that tagset)
				if not 'response' in job.rule:
					job.rule['response'] = 'mutate'

				if job.rule['response'] == 'combina':
					day[match[0]] |= day[match[1]]
					day.pop(match[1])
					# We will restart this job from scratch when we've iterated through the more specific jobs
					queue.append(job)
					queue.extend([Job(rules[num]) for num in range(job.rule['number'] - 1, -1, -1)])
				elif job.rule['response'] == 'errora':
					raise RuntimeError(f'Unexpected coincidence in {day} involving {match}')
				else:
					target = match[job.rule['target']]
					if job.rule['response'] == 'dele':
						day.pop(target)
						queue.append(job)
					else:
						newset = copy.deepcopy(day[target])
						if 'remove' in job.rule:
							newset -= guaranteeset(job.rule['remove'])
						if 'adde' in job.rule:
							newset |= guaranteeset(job.rule['adde'])
						if job.rule['response'] == 'duplicate':
							if not newset in day:
								day.append(newset)
						elif job.rule['response'] == 'mutate':
							day[target] = newset
						else:
							raise RuntimeError(f'Unknown instruction {job.rule})')
						if not job.rule['continue']:
							queue.extend([Job(rules[num]) for num in range(job.rule['number'] - 1, -1, -1)])
				if job.rule['continue']:
					return

	while len(queue) != 0:
		resolvejob(queue.pop())

	return day

def getvespers(day):
	assert type(day) is not datetime
	ivespers = [i | {'i-vesperae'} for i in kalendar.datamanage.getdate(day + timedelta(days=1))]
	iivespers = [i | {'ii-vesperae'} for i in kalendar.datamanage.getdate(day)]
	# Final product
	vesperal = iivespers + ivespers
	return prioritize(vesperal, vesperalrules)

def getdiurnal(day):
	assert type(day) is not datetime
	prioritized = prioritize(kalendar.datamanage.getdate(day), diurnalrules)
	martyrology = prioritize(kalendar.datamanage.getdate(day + timedelta(days=1)), martyrologyrules)
	lunarday = luna.lunardate(day + timedelta(days=1))
	lunardaynames = ['prima', 'secunda', 'tertia', 'quarta', 'quinta', 'sexta', 'septima', 'octava', 'nona', 'decima', 'undecima', 'duodecima', 'tertia-decima', 'quarta-decima', 'quinta-decima', 'sexta-decima', 'septima-decima', 'duodevicesima', 'undevicesima', 'vicesima', 'vicesima-prima', 'vicesima-secunda', 'vicesima-tertia', 'vicesima-quarta', 'vicesima-quinta', 'vicesima-sexta', 'vicesima-septima', 'vicesima-octava', 'vicesima-nona', 'tricesima']
	martyrology[0].add('luna-' + lunardaynames[lunarday - 1])
	return prioritized + martyrology

if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser(
		formatter_class=argparse.ArgumentDefaultsHelpFormatter,
		description='Daily Vespers specification generator',
	)

	parser.add_argument(
		'-d',
		'--date',
		type=str,
		default=str(date.today()),
		help='Date to generate',
	)

	parser.add_argument(
		'-t',
		'--time',
		type=str,
		default='vesperale',
		help='Whether to generate vesperale or diurnale'
	)

	args = parser.parse_args()

	# Generate kalendar
	if args.time == 'vesperale':
		print(getvespers(datetime.strptime(args.date, '%Y-%m-%d').date()))
	elif args.time == 'diurnale':
		print(getdiurnal(datetime.strptime(args.date, '%Y-%m-%d').date()))
	else:
		print('Invalid option for -t')
