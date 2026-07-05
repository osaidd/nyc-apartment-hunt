from nyc_hunt.config import Config, Search
from nyc_hunt.models import Listing
from nyc_hunt.score import area_tier, in_window, matches, priority

CFG = Config(move_in="2026-09-01", tier1=["Chelsea", "Hell's Kitchen"], tier2=["East Village"],
             searches=[Search("studio_1br", 3600, 0, 1, 1)])
S = CFG.searches[0]


def L(**kw):
    base = dict(url="https://x/1", source="craigslist", search_type="studio_1br", price=3000)
    base.update(kw)
    return Listing(**base)


def test_matches():
    assert matches(L(beds=1, baths=1), S)
    assert matches(L(beds=None, baths=None), S)  # unknowns pass
    assert not matches(L(price=3700), S)
    assert not matches(L(beds=2), S)


def test_area_tier():
    assert area_tier("West Chelsea", CFG) == 1  # substring both ways
    assert area_tier("east village", CFG) == 2
    assert area_tier("Bushwick", CFG) == 0


def test_in_window():
    assert in_window("", "2026-09-01") and in_window("2026-09-10", "2026-09-01")
    assert not in_window("2026-11-01", "2026-09-01")
    assert in_window("soon", "2026-09-01")  # unparseable → permissive


def test_priority_matrix():
    assert priority(L(neighborhood="Chelsea", no_fee=True), S, CFG) == "high"
    assert priority(L(neighborhood="Chelsea", price=3300), S, CFG) == "high"  # $300 headroom
    assert priority(L(neighborhood="Chelsea", price=3600), S, CFG) == "medium"  # fee at ceiling
    assert priority(L(neighborhood="Chelsea", no_fee=True, available_date="2026-12-01"), S, CFG) == "medium"
    assert priority(L(neighborhood="East Village", no_fee=True), S, CFG) == "medium"
    assert priority(L(neighborhood="Bushwick", no_fee=True), S, CFG) == "low"
