import urllib.parse
import re

textlineclass = 'text-line'

def getchant(src, tags):
    if 'http' in src:
        return f'<gabc-chant src="/chant/{urllib.parse.quote(src).replace('/', '%2F')}/{'.'.join(tags)}"></gabc-chant>'
    else:
        return f'<gabc-chant src="/chant/{src}/{'.'.join(tags)}"></gabc-chant>'

def antiphon(antiphon, neumes):
    ret = f'<div class="{textlineclass}">'
    if not neumes:
        return ret + antiphon['datum'] + '</div>'
    elif not 'src' in antiphon:
        return ret + antiphon['datum'] + '</div>'
    else:
        return ret + getchant(antiphon['src'], antiphon['tags']) + '</div>'

def responsoriumbreve(data, neumes):
    if not neumes or not 'src' in data['datum'][0]:
        incipit = data['datum'][0]['datum'] if 'datum' in data['datum'][0] else 'Absens'
        responsum = data['datum'][1]['datum'] if 'datum' in data['datum'][1] else 'Absens'
        versus = data['datum'][4]['datum'] if 'datum' in data['datum'][2] else 'Absens'
        return process([
            f'R. br. {incipit} * {responsum}',
            f'R. {incipit} * {responsum}',
            f'V. {versus}',
            f'R. {responsum}',
            f'V. {data["datum"][6]}',
            f' R. {incipit} * {responsum}'
        ], neumes)
    else:
        return getchant(data['datum'][0]['src'], data['tags'])

def stringhandle(line):
    line = line.replace('/', '<br>').replace('N.','<span class=red>N.</span>').replace('V. ', '<span class=red>&#8483;.</span> ').replace('R. br. ', '<span class=red>&#8479;. br. </span> ').replace('R. ', '<span class=red>&#8479;.</span> ').replace('✠', '<span class=red>✠</span>').replace('✙', '<span class=red>✙</span>').replace('+', '<span class=red>†</span>').replace('*', '<span class=red>*</span>')
    return f'<p class={textlineclass}>{line}</p>'

def chomp(gabc, tags):

    mode = None
    if ('mode:' in gabc):
        mode = gabc[gabc.index('mode:') + 5:gabc.index('\n', gabc.index('mode:'))].strip()
        if mode.endswith(';'):
            mode = mode[:-1]
    gabc = '%%\n' + gabc[re.search('\\([cf]\\d\\)', gabc).span()[0]:]
    gabc = gabc.replace('<sp>V/</sp>', '<v>\\Vbar</v>').replace('<sp>R/</sp>', '<v>\\Rbar</v>')
    if mode:
        gabc = f'mode:{mode};\n{gabc}'
    if 'intonata' in tags:
        gabc = gabc[:gabc.index('*')] + '(::)'
    elif 'repetita' in tags:
        gabc = 'initial-style:0;\n' + gabc.replace('*','')[gabc.index('\n') + 1:]
    elif 'responsorium-breve' in tags:
        clef = gabc[:gabc.index(')') + 1]
        incipit = gabc[gabc.index(')') + 1 : gabc.index('*')].strip()
        response = gabc[gabc.index(')', gabc.index('*')) + 1 : gabc.index('(::)')].strip()
        verseloc = gabc.index('<v>\\Vbar</v>') + len('<v>\\Vbar</v>')
        verse = gabc[verseloc : gabc.index('(::)', verseloc)].strip()
        gloria = gabc[gabc.index('(::)',  verseloc) + 4 : -4].strip()

        gabc = f'{clef} {incipit} *(;) {response} (::) <v>\\Rbar</v> {incipit} (;) {response} (::) <v>\\Vbar</v> {verse} *(;) {response} (::) <v>\\Vbar</v> {gloria} (::) <v>\\Rbar</v> {incipit} (;) {response} (::)'
    return gabc

def process(data, neumes):
    match data:
        case dict():
            if {'formula','responsorium-breve'}.issubset(set(data['tags'])):
                return responsoriumbreve(data, neumes)
            elif 'antiphona' in set(data['tags']):
                return antiphon(data, neumes)
            elif 'src' in data and neumes:
                return getchant(data['src'], data['tags'])
            else:
                return process(data['datum'], neumes)
        case list():
            return ''.join([process(v, neumes) for v in data])
        case str():
            return stringhandle(data)
    return process(data, neumes)
