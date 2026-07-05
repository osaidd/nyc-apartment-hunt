"""Deterministic HIGH/MED/LOW. No LLM anywhere in scoring."""
from datetime import date, timedelta

from .config import Config, Search
from .models import Listing

WINDOW = timedelta(days=21)
HEADROOM = 200


def matches(l: Listing, s: Search) -> bool:
    if l.price > s.max_price:
        return False
    if l.beds is not None and not (s.beds_min <= l.beds <= s.beds_max):
        return False
    if l.baths is not None and l.baths < s.baths_min:
        return False
    return True


def area_tier(neighborhood: str, cfg: Config) -> int:
    n = neighborhood.strip().lower()
    if not n:
        return 0
    for tier, names in ((1, cfg.tier1), (2, cfg.tier2)):
        if any(x.lower() in n or n in x.lower() for x in names):
            return tier
    return 0


def in_window(available_date: str, move_in: str) -> bool:
    try:
        avail, target = date.fromisoformat(available_date), date.fromisoformat(move_in)
    except ValueError:
        return True  # unknown/unparseable dates never disqualify
    return abs(avail - target) <= WINDOW


def priority(l: Listing, s: Search, cfg: Config) -> str:
    tier = area_tier(l.neighborhood, cfg)
    fee_ok = l.no_fee or l.price <= s.max_price - HEADROOM
    window = in_window(l.available_date, cfg.move_in)
    if tier == 1 and fee_ok and window:
        return "high"
    if tier == 1 and (fee_ok or window):
        return "medium"
    if tier == 2 and window:
        return "medium"
    return "low"
