# Copyright 2024 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import sys
import pathlib
import re

path = str(pathlib.Path(__file__).parent.absolute())

def psalm_line(line):
    return line

def get_and_html(file):
    return ''.join(list(map(lambda line: psalm_line(line), open(file, 'r', encoding = 'utf-8').readlines())))

def psalmget(root, psalm):
    return get_and_html(f'{path}/data/{root}/untagged{psalm}.txt').strip() + '\n'

def get(root, query):
    pathsplit = query.rfind('/')
    querypath = query[:pathsplit + 1]
    query = query[pathsplit + 1:]
    ret = ''
    for i in query.split(','):
        if ':' in i:
            psalm = i.split(':')[0]
            psalmtext = psalmget(root, querypath + psalm)
            for j in i.split(':')[1].split(';'):
                bounds = j.split('-')
                if len(bounds) == 1:
                    bounds[1] = str(int(bounds[0]) + 1)
                else:
                    bounds[1] = str(int(bounds[1]) + 1)
                if not bounds[1] in psalmtext:
                    ret += re.search(f'{bounds[0]}(.|\\n)+$', psalmtext).group()
                else:
                    ret += re.search(f'{bounds[0]}(.|\\n)+\\n{bounds[1]} ', psalmtext).group()[:-(len(bounds[1]) + 1)]
        else:
            ret += psalmget(root, querypath + i)
    return ret.strip()
