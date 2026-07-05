from nyc_hunt.report import render

ROW = {"dedupe_hash": "h1", "url": "https://x/1", "source": "renthop", "search_type": "studio_1br",
       "price": 3000, "address": "", "neighborhood": "Chelsea", "beds": 1.0, "baths": 1.0,
       "no_fee": 1, "available_date": "", "posted_date": "", "priority": "high", "status": "new",
       "first_seen": "2026-07-05 12:00:00"}


def test_render_html_and_md():
    html, md = render([ROW], {"high": 1, "medium": 0, "low": 0, "total": 1}, {"h1"})
    assert "Chelsea" in html and "$3,000" in html and "NEW" in html
    assert "https://x/1" in html and "no fee" in html.lower()
    assert "HIGH" in md and "https://x/1" in md
