from bottle import template
import urllib.parse
import re

textlineclass = 'text-line'

def getchant(src, tags) -> str:
    if 'http' in src:
        return f'<gabc-chant src="/chant/{urllib.parse.quote(src).replace("/", "%2F")}/{".".join(tags)}"></gabc-chant>'
    else:
        return f'<gabc-chant src="/chant/{src}/{".".join(tags)}"></gabc-chant>'

def antiphon(antiphon: dict, neumes: bool) -> str:
    match antiphon:
        case {"src": src, "tags": tags} if neumes:
            content = getchant(src, tags)
        case {"datum": datum}:
            content = datum
        case _:
            raise ValueError(f"Unhandled case: {antiphon!r}")

    return f'<div class="{textlineclass}">{content}</div>'

def responsoriumbreve(data: dict, neumes: bool) -> str:
    datum = data['datum']
    if neumes and 'src' in datum[0]:
        return getchant(datum[0]['src'], data['tags'])
    else:
        incipit = datum[0].get('datum', 'Absens')
        response = datum[1].get('datum', 'Absens')
        verse = datum[4].get('datum', 'Absens')
        gloria = datum[6] if len(datum) == 9 else 'Absens'
        return template('frontend/elements/responsorium-breve.tpl', incipit=incipit, response=response, verse=verse, gloria=gloria)

def stringhandle(line: str) -> str:
    result = re.search('\\[[a-z-]+\\]', line)
    if not result is None:
        line[result.span()[0] + 1 : result.span()[1] - 1]
    line = line.replace('/', '<br>').replace('N.','<span class=red>N.</span>').replace('V. ', '<span class=red>&#8483;.</span> ').replace('R. br. ', '<span class=red>&#8479;. br. </span> ').replace('R. ', '<span class=red>&#8479;.</span> ').replace('✠', '<span class=red>✠</span>').replace('✙', '<span class=red>✙</span>').replace('+', '<span class=red>†</span>').replace('*', '<span class=red>*</span>')
    return f'<p class={textlineclass}>{line}</p>'

def chomp(gabc: str, tags) -> str:
    mode: str | None = None
    if 'mode:' in gabc:
        mode = gabc[gabc.index('mode:') + 5:gabc.index('\n', gabc.index('mode:'))].strip()
        if mode.endswith(';'):
            mode = mode[:-1]
    gabc = '%%\n' + gabc[re.search('\\([cf]\\d\\)', gabc).span()[0]:]
    gabc = gabc.replace('<sp>V/</sp>', '<v>\\Vbar</v>').replace('<sp>R/</sp>', '<v>\\Rbar</v>')
    if mode:
        gabc = f'mode:{mode};\n{gabc}'
    if 'intonata' in tags:
        return gabc[:gabc.index('*')] + '(::)'
    elif 'repetita' in tags:
        return 'initial-style:0;\n' + gabc.replace('*','')[gabc.index('\n') + 1:]
    elif 'responsorium-breve' in tags:
        clef = gabc[:gabc.index(')') + 1]
        incipit = gabc[gabc.index(')') + 1 : gabc.index('*')].strip()
        response = gabc[gabc.index(')', gabc.index('*')) + 1 : gabc.index('(::)')].strip()
        verseloc = gabc.index('<v>\\Vbar</v>') + len('<v>\\Vbar</v>')
        verse = gabc[verseloc : gabc.index('(::)', verseloc)].strip()
        gloria = gabc[gabc.index('(::)',  verseloc) + 4 : -4].strip()

        return f'{clef} {incipit} *(;) {response} (::) <v>\\Rbar</v> {incipit} (;) {response} (::) <v>\\Vbar</v> {verse} *(;) {response} (::) <v>\\Vbar</v> {gloria} (::) <v>\\Rbar</v> {incipit} (;) {response} (::)'
    else:
        return gabc

def render(data, neumes: bool) -> str:
    match data:
        case {"tags": tags} if {'formula','responsorium-breve'}.issubset(set(tags)):
            return responsoriumbreve(data, neumes)
        case {"tags": tags} if 'antiphona' in set(tags):
            return antiphon(data, neumes)
        case {"src": src, "tags": tags} if neumes:
            return getchant(src, tags)
        case {"datum": datum}:
            return render(datum, neumes)
        case list():
            return ''.join(render(v, neumes) for v in data)
        case str():
            return stringhandle(data)
    raise ValueError(f"Unhandled case: {data!r}")
