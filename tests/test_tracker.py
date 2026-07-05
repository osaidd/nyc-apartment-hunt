from nyc_hunt.models import Listing
from nyc_hunt.tracker import Tracker


def test_add_dedupe_active_counts(tmp_path):
    t = Tracker(tmp_path / "t.db")
    l = Listing(url="https://x/1", source="renthop", search_type="studio_1br", price=3000, neighborhood="Chelsea")
    assert t.add(l, "high") is True
    assert t.add(l, "high") is False  # same URL → dup
    assert t.add(Listing(url="https://x/2", source="renthop", search_type="studio_1br", price=3100), "low")
    rows = t.active()
    assert len(rows) == 2 and rows[0]["priority"] in ("high", "low")
    assert t.counts() == {"high": 1, "medium": 0, "low": 1, "total": 2}
