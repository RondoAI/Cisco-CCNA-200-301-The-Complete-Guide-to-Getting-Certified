"""Tests for the elections layer — the political map. Real-data shape, injected
so there's no network dependency; one county flips D->R between cycles."""

from glasshouse.elections import CountyResultsAdapter, ElectionStore

# Two cycles, real column shape from the tonmcg county dataset. County 12001
# flips D -> R; county 12003 stays solid R.
_ROWS = {
    2020: [
        {"county_fips": "12001", "county_name": "Alpha County",
         "state_name": "Florida", "votes_dem": "5200", "votes_gop": "4800",
         "total_votes": "10000"},
        {"county_fips": "12003", "county_name": "Beta County",
         "state_name": "Florida", "votes_dem": "2000", "votes_gop": "8000",
         "total_votes": "10000"},
    ],
    2024: [
        {"county_fips": "12001", "county_name": "Alpha County",
         "state_name": "Florida", "votes_dem": "4600", "votes_gop": "5400",
         "total_votes": "10000"},
        {"county_fips": "12003", "county_name": "Beta County",
         "state_name": "Florida", "votes_dem": "1800", "votes_gop": "8200",
         "total_votes": "10000"},
    ],
}


def _store():
    s = ElectionStore()
    for r in CountyResultsAdapter(years=[2020, 2024], rows_by_year=_ROWS).fetch():
        s.add(r)
    return s


def test_adapter_parses_real_county_shape_and_sources_it():
    rows = CountyResultsAdapter(years=[2024], rows_by_year=_ROWS).fetch()
    r = next(x for x in rows if x.fips == "12001")
    assert r.county == "Alpha County" and r.state == "Florida"
    assert r.winner == "R" and r.margin_pct == 8.0      # (5400-4600)/10000
    assert r.sources, "every result carries its dataset source"


def test_lean_buckets():
    s = _store()
    alpha = next(r for r in s.by_year(2024) if r.fips == "12001")
    beta = next(r for r in s.by_year(2024) if r.fips == "12003")
    assert alpha.lean == "lean_R"      # 8% margin -> lean
    assert beta.lean == "solid_R"      # 64% margin -> solid


def test_map_data_is_choropleth_ready_by_fips():
    s = _store()
    md = s.map_data(2024)
    assert {d["fips"] for d in md} == {"12001", "12003"}
    assert all({"winner", "margin_pct", "lean"} <= set(d) for d in md)


def test_county_history_across_cycles():
    s = _store()
    hist = s.county_history("12001")
    assert [r.year for r in hist] == [2020, 2024]
    assert hist[0].winner == "D" and hist[1].winner == "R"   # it flipped


def test_flips_detects_party_change():
    s = _store()
    flips = s.flips(2020, 2024)
    assert len(flips) == 1
    f = flips[0]
    assert f["fips"] == "12001" and f["from"] == "D" and f["to"] == "R"


def test_state_and_national_rollups():
    s = _store()
    roll = s.state_rollup(2024)["Florida"]
    assert roll["counties"] == 2 and roll["winner"] == "R"
    nat = s.national_totals(2024)
    assert nat["total_votes"] == 20000 and nat["winner"] == "R"


def test_provenance_required():
    import pytest
    from glasshouse.elections import CountyResult
    s = ElectionStore()
    with pytest.raises(ValueError):
        s.add(CountyResult("12001", "X", "FL", 2024, 1, 2, 3))  # no source
