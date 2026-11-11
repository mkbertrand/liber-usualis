# Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import re

from renderer.rite_renderer import RiteRenderer

def render_lines(element, translation=None) -> tuple[list[str], list[str]]:
    renderer = RiteRenderer({})
    renderer.recurse_rite(element, translation, frozenset({'litaniae-sanctorum', 'ritus'}))
    renderer.close_paragraph()
    html = ''.join(renderer.rite)
    latin = re.search(r'<p class="rite-text rite-text-latin">(.*?)</p>', html).group(1).split('<br>')
    translated = re.search(r'<p class="rite-text rite-text-translation">(.*?)</p>', html).group(1).split('<br>')
    return latin, translated

def response(tag: str, datum: str, translation: str | None = None) -> dict:
    element = {'tags': frozenset({'litaniae-sanctorum', tag}), 'datum': datum}
    if translation is not None:
        element['translation'] = translation
    return element

def test_litany_response_continues_the_invocation_line() -> None:
    latin, _ = render_lines([
        'Sancta María,', response('ora', 'ora pro nobis.'),
        'Ab omni malo,', response('libera', 'líbera nos Dómine.'),
    ])
    assert latin == ['Sancta María, ora pro nobis.', 'Ab omni malo, líbera nos Dómine.']

def test_litany_response_translation_continues_the_translated_line() -> None:
    latin, translated = render_lines(
        ['Sancta María,', response('ora', 'ora pro nobis.', 'pray for us.')],
        ['Holy Mary,', None],
    )
    assert latin == ['Sancta María, ora pro nobis.']
    assert translated == ['Holy Mary, pray for us.']

def test_litany_response_opening_a_paragraph_is_its_own_line() -> None:
    latin, _ = render_lines([response('te-rogamus', 'Te rogámus audi nos.'), 'Fili Dei,'])
    assert latin == ['Te rogámus audi nos.', 'Fili Dei,']

def test_non_response_elements_still_start_a_new_line() -> None:
    latin, _ = render_lines(['Kýrie eléison.', {'tags': frozenset({'litaniae-sanctorum', 'formula'}), 'datum': 'Christe eléison.'}])
    assert latin == ['Kýrie eléison.', 'Christe eléison.']

def test_composite_commemoration_name_renders_as_heading() -> None:
    caput = {'tags': frozenset({'formula-commemorationis', 'formula', 'caput', 'annotatio'}), 'datum': {'tags': frozenset({'dominica', 'nomen'}), 'datum': [
        'Dominica ', {'tags': frozenset({'basis-nominis', 'hebdomada-vi-epiphaniae'}), 'datum': 'VI quæ superfuit post Epiphaniam'}
    ]}}
    element = {'tags': frozenset({'formula-commemorationis', 'formula'}), 'datum': 'Orémus.', 'caput': caput}
    renderer = RiteRenderer({})
    renderer.recurse_rite(element, None, frozenset({'ritus'}))
    renderer.close_paragraph()
    assert 'Dominica VI quæ superfuit post Epiphaniam' in ''.join(renderer.rite)


def invitatory_chomp(name: str, extra_tags: frozenset[str]) -> str:
    from datamanage import render_resources
    from renderer.chomp import chomp
    gabc = open(f'data/liber-usualis-chant/nocturnale/untagged/invitatoria/{name}.gabc', encoding='utf-8').read()
    return chomp(gabc, frozenset({'matutinum', 'antiphona', 'antiphona-invitatorium'}) | extra_tags, render_resources())


def test_invitatory_takes_no_psalm_tone_ending() -> None:
    # Ave Maria (mode 7a) has a psalm tone, but the Invitatory is answered by the Venite rather than a Euouae
    assert 'E(' not in invitatory_chomp('CSMSI', frozenset())


def test_invitatory_pars_begins_after_the_asterisk() -> None:
    # Sancta Maria: the referenced chant holds the whole antiphon; pars repeats only its second half, under a single clef
    gabc = invitatory_chomp('CBMVI', frozenset({'pars'}))
    body = gabc.split('%%\n', 1)[1]
    assert re.match(r'\(c3\)\s+In\(d_f@gwh\)ter\(i\)', body)
    assert 'San(' not in body
