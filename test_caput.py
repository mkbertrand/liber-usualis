# Copyright 2025 (AGPL-3.0-or-later), Miles K. Bertrand et al.

from typing import Any

import pytest

import datamanage

def lesson_headers(obj: Any) -> list[Any]:
    if isinstance(obj, dict):
        tags = set(obj.get('quaesitum') or obj.get('tags') or ())
        own = [obj.get('caput', {}).get('datum')] if {'formula', 'formula-lectionis'} <= tags else []
        return own + lesson_headers(obj.get('datum'))
    if isinstance(obj, list):
        return [header for item in obj for header in lesson_headers(item)]
    return []

# The short lesson of Compline and of the Officium Capituli at Prime is headed by a caput entry that must be
# loaded for those hours, not only alongside Matins
@pytest.mark.parametrize('day', ['2026-11-09', '2026-03-10', '2026-04-12'])
@pytest.mark.parametrize('hour', ['completorium', 'prima'])
def test_lectio_brevis_has_header(day: str, hour: str) -> None:
    rite = datamanage.rite_request(day, hour + '+officium', '', 'primarium', 'none', '')
    assert lesson_headers(rite['text']) == ['Lectio Brevis.']

def test_matins_lessons_keep_their_headers() -> None:
    rite = datamanage.rite_request('2026-11-09', 'matutinum-laudes+officium', '', 'primarium', 'none', '')
    assert lesson_headers(rite['text'])[:3] == ['Lectio I.', 'Lectio II.', 'Lectio III.']
