import os
import re
import hashlib

DEFINED_LOCALES = os.listdir('web/locales/')

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

# Accepts a file path (relative to /web/locales/{locale}/) and a list of locales in order of preference and returns the first locale that has the file. Basically needed for places where there's an English-only resource requested by a German user.
def bestlocalized(file, locales):
	for l in locales:
		if os.path.exists(f'web/locales/{l}{file}'):
			return f'web/locales/{l}{file}'


def get_resource_version(path):
	with open('web/resources' + path) as f:
		return hashlib.md5(f.read().encode('utf-8')).hexdigest()

def get_versioned_resource(path):
	if os.path.exists(f'web/resources{path}'):
		return f'/resources{path}?v={get_resource_version(path)}'
	else:
		return f'/resources{path}'
