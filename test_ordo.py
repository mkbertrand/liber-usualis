# Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import warnings

import datamanage


def ordo(date: str, time: str) -> dict:
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return datamanage.ordo(date, time, '')


def test_vesperal_psalms_of_another_office() -> None:
    # Vespers of St Hilary take the psalms of the Octave of the Epiphany
    result = ordo('2026-01-13', 'vesperale')
    assert result['primary'][0] == 'S. Hilarii Episcopi Confessoris et Ecclesiæ Doctoris'
    assert result['psalmi'][0] == 'In Octava Epiphaniæ Domini'
    assert 'psalmi' in result['psalmi'][1]


def test_vesperal_psalms_of_the_primary_office() -> None:
    assert ordo('2026-12-25', 'vesperale')['psalmi'] is None


def test_diurnal_has_no_vesperal_psalms() -> None:
    assert ordo('2026-01-13', 'diurnale')['psalmi'] is None
