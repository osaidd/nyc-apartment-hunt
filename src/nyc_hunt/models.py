"""Single listing shape shared by all sources (code scrapers and the Claude skill)."""
import hashlib
from dataclasses import asdict, dataclass
from urllib.parse import urlsplit

REQUIRED = ("url", "source", "search_type", "price")


@dataclass
class Listing:
    url: str
    source: str
    search_type: str
    price: int
    address: str = ""
    neighborhood: str = ""
    beds: float | None = None
    baths: float | None = None
    no_fee: bool = False
    available_date: str = ""
    posted_date: str = ""

    def normalized_url(self) -> str:
        p = urlsplit(self.url.strip())
        return f"{p.scheme.lower()}://{p.netloc.lower()}{p.path.rstrip('/')}"

    def dedupe_hash(self) -> str:
        return hashlib.sha256(self.normalized_url().encode()).hexdigest()

    def to_dict(self) -> dict:
        return asdict(self)


def listing_from_dict(d: dict) -> Listing:
    missing = [k for k in REQUIRED if not d.get(k)]
    if missing:
        raise ValueError(f"listing missing {missing}")
    return Listing(
        url=str(d["url"]),
        source=str(d["source"]),
        search_type=str(d["search_type"]),
        price=int(d["price"]),
        address=str(d.get("address", "")),
        neighborhood=str(d.get("neighborhood", "")),
        beds=None if d.get("beds") is None else float(d["beds"]),
        baths=None if d.get("baths") is None else float(d["baths"]),
        no_fee=bool(d.get("no_fee", False)),
        available_date=str(d.get("available_date", "")),
        posted_date=str(d.get("posted_date", "")),
    )
