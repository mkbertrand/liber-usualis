# Copyright 2024 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import os.path
import json
import pathlib
from datetime import date, datetime, timedelta
import re
from typing import NamedTuple
import itertools

from kalendar import kalendar
import kalendar.datamanage

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

diurnalrules = kalendar.datamanage.flatten(load_data('kalendar/data/diurnal-coincidence.json'))
vesperalrules = kalendar.datamanage.flatten(load_data('kalendar/data/vesperal-coincidence.json'))

roletagsordered = ['primarium', 'commemoratio', 'omissum', 'tempus']
roletags = set(roletagsordered)

class Job(NamedTuple):
	rule: dict

def getvespers(day):
	assert type(day) is not datetime
	ivespers = [i | {'i-vesperae'} for i in kalendar.datamanage.getdate(day + timedelta(days=1))]
	iivespers = [i | {'ii-vesperae'} for i in kalendar.datamanage.getdate(day)]
	# Final product
	vesperal = iivespers + ivespers

	queue = [Job(rule) for rule in vesperalrules]
	queue.reverse()
	ruleskip = [False] * len(vesperalrules)

	def resolvejob(job):

		if ruleskip[job.rule['number']]:
			return
		# If we have reached a rule following a rule which shouldn't be rechecked, mark it off as done
		if not vesperalrules[job.rule['number'] - 1]['recheck']:
			ruleskip[job.rule['number'] - 1] = True

		tagsetindices = range(len(vesperal))
		matchset = []
		for restriction in job.rule['restrict']:
			search = [tagsetindex for tagsetindex in tagsetindices if restriction.include <= vesperal[tagsetindex] and not (restriction.exclude and restriction.exclude <= vesperal[tagsetindex])]
			if len(search) == 0:
				return
			else:
				matchset.append(search)

		matches = list(itertools.product(*matchset))

		for match in matches:
			if len(set(match)) == len(job.rule['restrict']):
				if job.rule['response'] == 'combina':
					vesperal[match[0]] |= vesperal[match[1]]
					if len(vesperal[match[0]] & roletags) > 1:
						for i in roletagsordered:
							if i in vesperal[match[0]]:
								vesperal[match[0]] -= roletags
								vesperal[match[0]].add(i)
								break
					vesperal.pop(match[1])
					# We will restart this job from scratch when we've iterated through the more specific jobs
					queue.append(job)
					queue.extend([Job(vesperalrules[num]) for num in range(job.rule['number'] - 1, -1, -1)])
				elif job.rule['response'] == 'errora':
					raise RuntimeError(f'Unexpected coincidence in {vesperal} involving {match}')
				else:
					target = match[job.rule['target']]
					if job.rule['response'] == 'dele':
						vesperal.pop(target)
						queue.append(job)
					elif type(job.rule['response']) is frozenset:
						if job.rule['response'] <= vesperal[target]:
							continue
						if job.rule['response'] & roletags:
							vesperal[target] -= roletags
						vesperal[target] |= job.rule['response']
						queue.append(job)
						if not job.rule['continue']:
							queue.extend([Job(vesperalrules[num]) for num in range(job.rule['number'] - 1, -1, -1)])
					elif not type(job.rule['response']) is str:
						raise RuntimeError(type(job.rule['response']))
					else:
						if job.rule['response'] in vesperal[target]:
							continue
						if job.rule['response'] in roletags:
							vesperal[target] -= roletags
						vesperal[target].add(job.rule['response'])
						queue.append(job)
						if not job.rule['continue']:
							queue.extend([Job(vesperalrules[num]) for num in range(job.rule['number'] - 1, -1, -1)])
				return

	while len(queue) != 0:
		resolvejob(queue.pop())

	return vesperal

def getdiurnal(day):
	assert type(day) is not datetime
	day = kalendar.datamanage.getdate(day)

	queue = [Job(rule) for rule in diurnalrules]
	queue.reverse()
	ruleskip = [False] * len(diurnalrules)

	def resolvejob(job):

		if ruleskip[job.rule['number']]:
			return
		# If we have reached a rule following a rule which shouldn't be rechecked, mark it off as done
		if not diurnalrules[job.rule['number'] - 1]['recheck']:
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
				if job.rule['response'] == 'combina':
					day[match[0]] |= day[match[1]]
					if len(day[match[0]] & roletags) > 1:
						for i in roletagsordered:
							if i in day[match[0]]:
								day[match[0]] -= roletags
								day[match[0]].add(i)
								break
					day.pop(match[1])
					# We will restart this job from scratch when we've iterated through the more specific jobs
					queue.append(job)
					queue.extend([Job(diurnalrules[num]) for num in range(job.rule['number'] - 1, -1, -1)])
				elif job.rule['response'] == 'errora':
					raise RuntimeError(f'Unexpected coincidence in {day} involving {match}')
				else:
					target = match[job.rule['target']]
					if job.rule['response'] == 'dele':
						day.pop(target)
						queue.append(job)
					elif type(job.rule['response']) is frozenset:
						if job.rule['response'] <= day[target]:
							continue
						if job.rule['response'] & roletags:
							day[target] -= roletags
						day[target] |= job.rule['response']
						queue.append(job)
						if not job.rule['continue']:
							queue.extend([Job(diurnalrules[num]) for num in range(job.rule['number'] - 1, -1, -1)])
					elif not type(job.rule['response']) is str:
						raise RuntimeError(type(job.rule['response']))
					else:
						if job.rule['response'] in day[target]:
							continue
						if job.rule['response'] in roletags:
							day[target] -= roletags
						day[target].add(job.rule['response'])
						queue.append(job)
						if not job.rule['continue']:
							queue.extend([Job(diurnalrules[num]) for num in range(job.rule['number'] - 1, -1, -1)])
				return

	while len(queue) != 0:
		resolvejob(queue.pop())

	return day

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

	args = parser.parse_args()

	# Generate kalendar
	ret = getvespers(datetime.strptime(args.date, '%Y-%m-%d').date())

	print(ret)
