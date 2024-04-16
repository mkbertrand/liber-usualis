import sys
import pathlib
import commonresources

path = str(pathlib.Path(__file__).parent.absolute())

def psalm_line(line):
    line = commonresources.text_line(line)
    if (line[0].isdigit()):
        line = '<span class="verse-number">' + line.split(' ')[0] + '</span> ' + ' '.join(line.split(' ')[1:])
    return line

def get_and_html(file):
    return list(map(lambda line: psalm_line(line), open(file, 'r', encoding = 'utf-8').readlines()))

def psalmget(number, section, psalmversion):
    return get_and_html(path + '\\content\\' + str(psalmversion) + '\\psalter\\' + str(number) + '.txt')

psalms = sys.argv[1]
version = sys.argv[2]
doxology = 'gloria'
if (len(sys.argv) > 3):
    doxology = sys.argv[3]

ret = ''

for i in psalms.split(','):
    chunk = ''
    for j in i.split('+'):
        psalm = ''
        #handle excerpted / split Psalms (format is 1:1-2;3-4 &c)
        if (':' in j):
            psalm = '\n'.join(psalmget(j.split(':')[0], '', version))
            excerpts = []
            for k in j.split(':')[1].split('/'):
                bounds = k.split('-')
                start = int(bounds[0])
                end = 0
                #if only one number is provided (EG 1:1)
                if (len(bounds) == 1):
                    end = start
                else:
                    end = int(bounds[1])

                if (str(end + 1) in psalm):
                    excerpts += psalm[psalm.index('<span class="verse-number">' + str(start)) : psalm.index('<span class="verse-number">' + str(end + 1)) - 1].split('\n')
                else:
                    excerpts += psalm[psalm.index('<span class="verse-number">' + str(start)):].split('\n')
            psalm = excerpts
        else:
            psalm = psalmget(j, '', version)

        chunk += '</div><div class="psalm-wrapper"><h3 class="psalm-head">Psalmus ' + j + '</h3>'
        for line in psalm:
            chunk += line + '<br/>'

    if (doxology != 'none'):
        dox = get_and_html(path + '\\content\\' + str(version) + '\\ordinary\\' + doxology + '.txt')
        chunk += dox[0] + '<br/>' + dox[1] + '<br/>'

    ret += chunk

ret = ret[6:] + '</div>'

print(ret)
