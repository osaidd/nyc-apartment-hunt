import pytest

from nyc_hunt.models import Listing, listing_from_dict


def test_dedupe_hash_ignores_query_and_trailing_slash():
    a = Listing(url="https://WWW.renthop.com/listings/x/123/?src=a", source="renthop", search_type="studio_1br", price=3000)
    b = Listing(url="https://www.renthop.com/listings/x/123", source="renthop", search_type="studio_1br", price=3000)
    assert a.dedupe_hash() == b.dedupe_hash()
    assert len(a.dedupe_hash()) == 64


def test_from_dict_roundtrip_and_validation():
    d = {"url": "https://x.com/1", "source": "zillow", "search_type": "2br_2ba", "price": 4800, "beds": 2, "baths": 2}
    l = listing_from_dict(d)
    assert l.price == 4800 and l.beds == 2.0 and l.no_fee is False
    with pytest.raises(ValueError):
        listing_from_dict({"url": "https://x.com/2"})
