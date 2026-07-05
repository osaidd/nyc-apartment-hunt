from pathlib import Path

from nyc_hunt.config import Search
from nyc_hunt.sources import SOURCES, renthop

HTML = (Path(__file__).parent / "fixtures" / "renthop_search.html").read_text()


def test_parse_fixture():
    out = renthop.parse(HTML, "studio_1br")
    assert len(out) == 3
    l = out[0]
    assert "renthop.com" in l.url and l.price == 3450 and l.source == "renthop"
    assert l.neighborhood == "Hudson Yards" and l.beds == 1.0 and l.no_fee is True
    assert out[1].beds == 0.0  # Studio
    assert out[2].baths == 1.5


def test_registry():
    assert set(SOURCES) == {"craigslist", "renthop"}


def test_search_url():
    assert "max_price=5000" in renthop.search_url(Search("2br_2ba", 5000, 2, 2, 2))
