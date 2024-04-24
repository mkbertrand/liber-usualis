from bottle import template
import urllib.parse
import re
import frontend.psalms as psalms

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
        return template('frontend/elements/responsorium-breve.tpl', incipit=datum[0].get('datum', 'Absens'), response=datum[1].get('datum', 'Absens'), verse=datum[4].get('datum', 'Absens'), gloria=datum[6] if len(datum) == 9 else 'Absens')

def stringhandle(line: str) -> str:
    result = re.search('\\[.+\\]', line)
    if not result is None:
        return render(psalms.render(result.group()[1:-1]).split('\n'), False)

    line = line.replace('/', '<br>')
    for i in re.findall('[0-9]+', line):
        line = line.replace(i, f'<span class="verse-number">{i}</span>')
    line = line.replace('N.','<span class=red>N.</span>').replace('V. ', '<span class=red>&#8483;.</span> ').replace('R. br. ', '<span class=red>&#8479;. br. </span> ').replace('R. ', '<span class=red>&#8479;.</span> ').replace('✠', '<span class=red>✠</span>').replace('✙', '<span class=red>✙</span>').replace('+', '<span class=red>†</span>').replace('*', '<span class=red>*</span>')
    return f'<p class={textlineclass}>{line}</p>'

def chomp(gabc: str, tags) -> str:
    mode: str | None = None
    if 'mode:' in gabc:
        mode = gabc[gabc.index('mode:') + 5:gabc.index('\n', gabc.index('mode:'))].strip()
        if mode.endswith(';'):
            mode = mode[:-1]
    gabc = '%%\n' + gabc[re.search('\\([cf]\\d\\)', gabc).span()[0]:]
    gabc = gabc.replace('<sp>V/</sp>.', '<v>\\Vbar</v>').replace('<sp>R/</sp>.', '<v>\\Rbar</v>')
    if mode:
        gabc = f'mode:{mode};\n{gabc}'
    if 'antiphona' in tags:
        # Notes which define the termination
        euouae = re.sub('<.?eu>', '', re.search(' <eu>.+$', gabc).group())
        # Gabc without the euouae
        gabc = gabc[:gabc.index('<eu>')]
        if 'intonata' in tags:
            return gabc[:gabc.index('*')] + '(::)' + euouae
        elif 'repetita' in tags:
            gabc = gabc.replace('*','')[gabc.index('\n') + 1:]
            firstsyllable = re.search('\\w+\\(', gabc).group()
            gabc = 'initial-style:0;\n' + gabc[:gabc.index('(')].capitalize() + gabc[gabc.index('('):].replace(firstsyllable, firstsyllable.capitalize())
        if not 'paschalis' in tags and ' <i>T. P.</i>' in gabc:
            return gabc[:gabc.index(' <i>T. P.</i>')]
        return gabc

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
