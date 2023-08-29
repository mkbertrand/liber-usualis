import pickle
import datetime
import json
import pathlib
import pytest
import random

from kalendar import kalendar


@pytest.mark.parametrize("kal_name", kalendar.kalendars.keys())
@pytest.mark.parametrize("year", random.sample(range(1582, 3000), k=10))
def test_repeatable(kal_name: str, year: int) -> None:
    """
    Make sure results are repeatable (i.e. we don't damage the database during a run)
    """
    # TODO: Fixture for kal_def, but make sure we get a new one!
    kal_def = kalendar.kalendars[kal_name]()
    kal_def_pickle = pickle.dumps(kal_def)
    kal = kal_def.gen(year)
    assert pickle.dumps(kal_def) == kal_def_pickle, "Kalendar def changed after use!"


class TestKalendar:
    @pytest.fixture(scope="class", params=kalendar.kalendars.keys())
    def kal_def(self, request) -> kalendar.Kalendar:
        return kalendar.kalendars[request.param]()

    @pytest.fixture(scope="class", params=range(1900, 2200))
    def kal(self, kal_def: kalendar.Kalendar, request) -> kalendar.KalendarRange:
        return kal_def.gen(request.param)

    def test_structure(self, kal: kalendar.KalendarRange) -> None:
        """Make sure the structure is correct"""
        for date, entries in kal.items():
            assert type(date) == datetime.date
            assert date.year == kal.year
            assert type(entries) == list
            assert len(entries) >= 1, f"Day {date} has no entries"
            for entry in entries:
                assert type(entry) == set
                assert len(entry) >= 1, "Entry has no tags"
                for tag in entry:
                    assert type(tag) == str

    def test_alldates(self, kal: kalendar.KalendarRange) -> None:
        """Make sure every day of the year has at least one entry"""
        date = datetime.date(kal.year, 1, 1)
        while date.year == kal.year:
            assert date in kal.kal, f"No entries for {date}"

            date = date + datetime.timedelta(days=1)

    def test_transfers(self, kal: kalendar.KalendarRange) -> None:
        """Make sure translations are sane"""
        assert not kal.match_any({"translatus", "translatus-originalis"})
        for match1 in kal.match({"translatus-originalis"}):
            for match2 in kal.match(
                match1.feast - {"translatus-originalis"} | {"translatus"},
                {"translatus-originalis"},
            ):
                assert match1.date != match2.date, f"Transfer to self: {match1!s} => {match2!s}"

    def test_compare(self, kal: kalendar.KalendarRange) -> None:
        """Compare to known-good output"""
        try:
            ref = json.loads(pathlib.Path(f"kalendar/testdata/year-{kal.year}.json").read_text())
        except FileNotFoundError:
            pytest.skip(f"No reference file found for {kal.year}")

        def normalize(kal):
            return {
                datetime.datetime.strptime(day, "%Y-%m-%d").date() if type(day) == str else day:
                {frozenset(entry) for entry in entries}
                for day, entries in kal.items()
            }

        kal_run = normalize(kal.kal)
        kal_ref = normalize(ref)

        assert kal_run == kal_ref
