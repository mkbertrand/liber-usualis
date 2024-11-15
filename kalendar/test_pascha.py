# Copyright 2024 (AGPL-3.0-or-later), Miles K. Bertrand et al.

from datetime import datetime
import json
import pathlib
import pytest
from kalendar import pascha


# Load data file
easters = json.loads(pathlib.Path("kalendar/testdata/pascha.json").read_text())


@pytest.mark.parametrize("year", range(1, 9999))
def test_pascha(year):
    easter = pascha.geteaster_assert(year)

    # Ensure computed date matches date recorded in file
    easter_ref = datetime.strptime(easters[str(year)], "%Y-%m-%d").date()
    assert easter == easter_ref
