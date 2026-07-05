from pathlib import Path

from nyc_hunt.config import Config, Search
from nyc_hunt.sources import craigslist

HTML = (Path(__file__).parent / "fixtures" / "craigslist_search.html").read_text()


def test_parse_fixture():
    out = craigslist.parse(HTML, "studio_1br")
    assert len(out) >= 1
    l = out[0]
    assert l.source == "craigslist" and l.url.startswith("https://") and l.price > 100


def test_search_url():
    u = craigslist.search_url(Search("studio_1br", 3600, 0, 1, 1))
    assert "max_price=3600" in u and "max_bedrooms=1" in u and "/mnh/" in u


def test_fetch_uses_all_searches():
    calls = []
    cfg = Config(searches=[Search("a", 3600, 0, 1), Search("b", 5000, 2, 2, 2)])
    craigslist.fetch(cfg, get=lambda u: (calls.append(u), HTML)[1], sleep=lambda: None)
    assert len(calls) == 2


def test_parse_unescapes_html_entities():
    from nyc_hunt.sources.craigslist import parse
    block = ('<li class="cl-static-search-result" title="Hell&#39;s Kitchen &quot;MINT&quot; 1BR">'
             '<a href="https://www.craigslist.org/view/d/x/1"><div class="title">t</div>'
             '<div class="details"><div class="price">$3,000</div>'
             '<div class="location">Hell&#39;s Kitchen</div></div></a></li>')
    out = parse(block, "studio_1br")
    assert out[0].address == 'Hell\'s Kitchen "MINT" 1BR'
    assert out[0].neighborhood == "Hell's Kitchen"
