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
