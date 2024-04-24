import sys
import pathlib
import re

path = str(pathlib.Path(__file__).parent.parent.absolute())

def psalm_line(line):
    return line

def get_and_html(file):
    return '\n'.join(list(map(lambda line: psalm_line(line), open(file, 'r', encoding = 'utf-8').readlines())))

def psalmget(psalm):
    return get_and_html(f'{path}/data/breviarium-1888/untagged/psalmi/{psalm}.txt')

def render(query):
    ret = ''
    for i in query.split(','):
        if ':' in i:
            psalm = i.split(':')[0]
            psalmtext = psalmget(psalm)
            for j in i.split(':')[1].split(';'):
                bounds = j.split('-')
                if len(bounds) == 1:
                    bounds[1] = str(int(bounds[0]) + 1)
                else:
                    bounds[1] = str(int(bounds[1]) + 1)
                if not bounds[1] in psalmtext:
                    ret += re.search(f'{bounds[0]}(.|\\n)+$', psalmtext).group()
                else:
                    ret += re.search(f'{bounds[0]}(.|\\n)+\\n{bounds[1]}', psalmtext).group()[:-len(bounds[1])]
        else:
            ret += psalmget(i)
    return ret
