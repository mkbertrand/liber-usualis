# Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import warnings
from typing import Any

import datamanage
from renderer.rendering_utils import claw, align_part_clefs, transpose_gabc_notes


def matins_html(date: str) -> str:
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return str(datamanage.rendered_rite_request(date, 'matutinum-laudes+officium', '', 'primarium', 'latina', ''))


def matins_text(date: str) -> Any:
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return datamanage.rite_request(date, 'matutinum-laudes+officium', '', 'primarium', 'english', '')['text']


def responsories_with_gloria(element: Any) -> list[dict]:
    if isinstance(element, dict):
        own = [element] if {'responsorium', 'cum-gloria'} <= set(element.get('tags', ())) and isinstance(element.get('datum'), list) else []
        return own + responsories_with_gloria(element.get('datum'))
    if isinstance(element, list):
        return [found for item in element for found in responsories_with_gloria(item)]
    return []


def gloria_of(responsory: dict) -> dict:
    return next(claw(part) for part in responsory['datum'] if isinstance(part, dict) and 'gloria' in claw(part)['tags'])


def test_simple_feast_gloria_follows_the_nocturn_of_the_feria() -> None:
    # St Anicetus (simplex, Friday in Eastertide): the second responsory of the second nocturn takes the Gloria
    # before the Te Deum, on the common mode 8 tone (written in C4) transposed into the C3 clef of In servis suis
    gloria = gloria_of(responsories_with_gloria(matins_text('2026-04-17'))[-1])
    assert 'nocturna-ii' in gloria['tags']
    assert gloria['datum'] == 'Glória Patri, et Fílio, et Spirítui sancto.'
    assert gloria['translation']['datum'].startswith('Glory be to the Father')
    assert 'Gló(h)ri(hg)a(hihghgffoe) Pa(gf)tri,(gh)' in matins_html('2026-04-17')


def test_simple_feast_gloria_on_monday_uses_the_first_nocturn() -> None:
    # St Paulinus (simplex, Monday): Ecce sacerdos from the first nocturn of the Common of a Confessor Bishop
    gloria = gloria_of(responsories_with_gloria(matins_text('2026-06-22'))[-1])
    assert 'nocturna-i' in gloria['tags']
    assert 'Gló(j)ri(ji)a(jkjijihhog) Pa(ih)tri,(ij)' in matins_html('2026-06-22')


def test_paschal_saturday_office_of_the_virgin_resolves_its_alleluja() -> None:
    # Saturday Office of the Blessed Virgin in Eastertide adds an alleluja to the double respond
    assert responsories_with_gloria(matins_text('2026-04-18'))


def test_transpose_gabc_notes_shifts_pitches_but_not_text_or_attributes() -> None:
    assert transpose_gabc_notes('Spi(g)rí(ixhi_HG/hih[ll:1])tu(ghf)', -2) == 'Spi(e)rí(gxfg_FE/fgf[ll:1])tu(efd)'


def test_align_part_clefs_transposes_parts_into_the_first_clef() -> None:
    parts = ['mode:8;\n%%\n(c3) In(e)', ' (::) ', 'mode:8;\n%%\n(c4) Gló(j)ri(ji)']
    assert align_part_clefs(parts) == ['mode:8;\n%%\n(c3) In(e)', ' (::) ', 'mode:8;\n%%\n(c3) Gló(h)ri(hg)']


def test_align_part_clefs_moves_between_c_and_f_clefs_by_the_nearest_octave() -> None:
    parts = ['mode:2;\n%%\n(c4) A(j)', 'mode:2;\n%%\n(f3) B(e)']
    # Do on the F3 clef (e) becomes do on the C4 clef, a shift of two steps down rather than five up
    assert align_part_clefs(parts)[1] == 'mode:2;\n%%\n(c4) B(c)'


def test_immaculate_conception_proper_responsory_renders_as_a_responsory() -> None:
    # Signum magnum (third responsory of the second nocturn) must carry the responsorium tag, or its chant
    # formula is rendered as a bare chant and fails
    assert 'Signum magnum' in matins_html('2026-12-08')


def test_translated_responsory_formulae_keep_the_gloria_as_its_own_part() -> None:
    # Translations are matched to the Latin responsory part by part, so the Gloria must be a separate slot rather
    # than text written into the formula; SS Philip and James has a fully translated responsory with a Gloria
    for translation, gloria in (('deutsch', 'Ehre sei dem Vater und dem Sohne'), ('nederlands', 'Eer aan de Vader')):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            html = str(datamanage.rendered_rite_request('2026-05-01', 'matutinum-laudes+officium', '', 'primarium', translation, ''))
        assert gloria in html
