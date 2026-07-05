"""Craigslist Manhattan apartments — parses the static no-JS results Craigslist ships."""
import re
from urllib.parse import urlencode

from ..config import Config, Search
from ..models import Listing
from . import http

BASE = "https://newyork.craigslist.org/search/mnh/apa"  # mnh = Manhattan
ITEM_RE = re.compile(
    r'<li class="cl-static-search-result"[^>]*title="(?P<title>[^"]*)".*?'
    r'href="(?P<url>[^"]+)".*?class="price">\s*\$(?P<price>[\d,]+).*?'
    r'class="location">\s*(?P<loc>[^<]*?)\s*<', re.S)


def search_url(s: Search) -> str:
    q = {"max_price": s.max_price, "min_bedrooms": int(s.beds_min), "max_bedrooms": int(s.beds_max)}
    if s.baths_min:
        q["min_bathrooms"] = int(s.baths_min)
    return f"{BASE}?{urlencode(q)}"


def parse(html: str, search_type: str) -> list[Listing]:
    out = []
    for m in ITEM_RE.finditer(html):
        title = m.group("title")
        out.append(Listing(
            url=m.group("url").split("?")[0], source="craigslist", search_type=search_type,
            price=int(m.group("price").replace(",", "")), address=title,
            neighborhood=m.group("loc"), no_fee="no fee" in title.lower()))
    return out


def fetch(cfg: Config, get=http.get, sleep=http.polite_sleep) -> list[Listing]:
    out = []
    for s in cfg.searches:
        out += parse(get(search_url(s)), s.name)
        sleep()
    return out
