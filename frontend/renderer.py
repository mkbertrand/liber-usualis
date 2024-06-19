from bottle import template
import urllib.parse
import re
import requests
import json

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

    return f'<div class="text-line">{content}</div>'

def responsoriumbreve(data: dict, neumes: bool) -> str:
    datum = data['datum']
    if neumes and 'src' in datum[0]:
        return getchant(datum[0]['src'], data['tags'])
    else:
        return template('frontend/components/responsorium-breve.tpl', incipit=datum[0].get('datum', 'Absens'), response=datum[1].get('datum', 'Absens'), verse=datum[4].get('datum', 'Absens'), gloria=datum[6] if len(datum) == 9 else 'Absens')

def stringhandle(line: str) -> str:
    line = line.replace('/', '<br>').replace('\n', '<br>')
    # Has to be reversed since if there exist verse numbers like 10 and 1, the 1 will be replaced in both, and then the 0 will be ignored, and not included as a verse number.
    for i in reversed(re.findall('[0-9]+', line)):
        line = line.replace(i, f'<span class="verse-number">{i}</span>')
    return line.replace('N.','<span class=red>N.</span>').replace('V. ', '<span class=red>&#8483;.</span> ').replace('R. br. ', '<span class=red>&#8479;. br. </span> ').replace('R. ', '<span class=red>&#8479;.</span> ').replace('✠', '<span class=red>✠</span>').replace('✙', '<span class=red>✙</span>').replace('+', '<span class=red>†</span>').replace('*', '<span class=red>*</span>')

def render(data, parameters, language = None, translation = None) -> str:
    if 'tags' in data and not language == None:
        tran = json.loads(requests.get('http://localhost:8000/json/tags', params={'tags': ' '.join(data['tags'])}, stream=True, timeout=10).text)
        if not tran is None:
            translation = tran['datum']
    match data:
        case {"tags": tags} if {'formula','responsorium-breve'}.issubset(set(tags)):
            return responsoriumbreve(data, parameters['chant'])
        case {"tags": tags} if 'antiphona' in set(tags):
            return antiphon(data, parameters['chant'])
        case {"src": src, "tags": tags} if parameters['chant']:
            return getchant(src, tags)
        case {'tags': tags, 'datum': datum} if any('psalmi' in i for i in tags):
            return render(datum, parameters, language, translation)
        case {"datum": datum}:
            return render(datum, parameters, language, translation)
        case list():
            if translation and len(translation) == len(data):
                ret = ''
                for i in range(0, len(data)):
                    ret += render(data[i], parameters, language, translation[i])
                return ret
            return ''.join(render(v, parameters, language, None) for v in data)
        case str():
            if translation:
                return template('frontend/components/text.tpl', content=stringhandle(data), translation=translation)
            else:
                return template('frontend/components/text.tpl', content=stringhandle(data))
    raise ValueError(f"Unhandled case: {data!r}")
