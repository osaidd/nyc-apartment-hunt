"""SQLite tracker. One table, URL-hash dedupe, no ORM."""
import sqlite3
from pathlib import Path

from .models import Listing

SCHEMA = """
CREATE TABLE IF NOT EXISTS listings (
  id INTEGER PRIMARY KEY,
  dedupe_hash TEXT NOT NULL UNIQUE,
  url TEXT NOT NULL, source TEXT NOT NULL, search_type TEXT NOT NULL,
  price INTEGER NOT NULL, address TEXT, neighborhood TEXT,
  beds REAL, baths REAL, no_fee INTEGER NOT NULL DEFAULT 0,
  available_date TEXT, posted_date TEXT,
  priority TEXT NOT NULL CHECK (priority IN ('high','medium','low')),
  status TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new','saved','dead')),
  first_seen TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


class Tracker:
    def __init__(self, db_path: str | Path):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(db_path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)

    def add(self, l: Listing, priority: str) -> bool:
        cur = self.db.execute(
            "INSERT OR IGNORE INTO listings (dedupe_hash,url,source,search_type,price,address,"
            "neighborhood,beds,baths,no_fee,available_date,posted_date,priority) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (l.dedupe_hash(), l.url, l.source, l.search_type, l.price, l.address,
             l.neighborhood, l.beds, l.baths, int(l.no_fee), l.available_date, l.posted_date, priority))
        self.db.commit()
        return cur.rowcount == 1

    def active(self) -> list[dict]:
        rows = self.db.execute(
            "SELECT * FROM listings WHERE status != 'dead' ORDER BY first_seen DESC, id DESC")
        return [dict(r) for r in rows]

    def counts(self) -> dict:
        out = {"high": 0, "medium": 0, "low": 0, "total": 0}
        for r in self.db.execute("SELECT priority, COUNT(*) n FROM listings WHERE status != 'dead' GROUP BY priority"):
            out[r["priority"]] = r["n"]
        out["total"] = sum(out[k] for k in ("high", "medium", "low"))
        return out
