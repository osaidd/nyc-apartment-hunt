"""RentHop NYC search — cards carry data-listing-id; parse each card block leniently.
Titles/neighborhoods are HTML-unescaped before storage.

RentHop often sits behind a Cloudflare challenge for non-browser clients; when
that happens fetch() raises and the caller reports the source as blocked.
"""
import html as html_mod
import re
from urllib.parse import urlencode

from ..config import Config, Search
from ..models import Listing
from . import http

BASE = "https://www.renthop.com/search/nyc"
URL_RE = re.compile(r'href="(https://www\.renthop\.com/listings/[^"]+)"')
PRICE_RE = re.compile(r"\$([\d,]+)")
BEDS_RE = re.compile(r"([\d.]+)\s*Bed|Studio", re.I)
BATHS_RE = re.compile(r"([\d.]+)\s*Bath", re.I)
HOOD_RE = re.compile(r">\s*([^<>,]+),\s*(?:Manhattan|New York)", re.I)


def search_url(s: Search) -> str:
    q = {"max_price": s.max_price, "min_bedrooms": int(s.beds_min),
         "max_bedrooms": int(s.beds_max), "sort": "hopscore", "page": 1}
    return f"{BASE}?{urlencode(q)}"


def parse(html: str, search_type: str) -> list[Listing]:
    out, seen = [], set()
    for block in re.split(r"data-listing-id=", html)[1:]:
        block = block[:4000]
        u, p = URL_RE.search(block), PRICE_RE.search(block)
        if not u or not p:
            continue
        url = u.group(1).split("?")[0]
        if url in seen:
            continue
        seen.add(url)
        title_m = re.search(r'listing-title-link[^>]*>([^<]+)<', block)
        beds_m, baths_m, hood_m = BEDS_RE.search(block), BATHS_RE.search(block), HOOD_RE.search(block)
        beds = None
        if beds_m:
            beds = 0.0 if beds_m.group(0).lower() == "studio" else float(beds_m.group(1))
        out.append(Listing(
            url=url, source="renthop", search_type=search_type,
            price=int(p.group(1).replace(",", "")),
            address=html_mod.unescape(title_m.group(1).strip()) if title_m else "",
            beds=beds, baths=float(baths_m.group(1)) if baths_m else None,
            neighborhood=html_mod.unescape(hood_m.group(1).strip()) if hood_m else "",
            no_fee="no fee" in block.lower()))
    return out


def fetch(cfg: Config, get=http.get, sleep=http.polite_sleep) -> list[Listing]:
    out = []
    for s in cfg.searches:
        out += parse(get(search_url(s)), s.name)
        sleep()
    return out
