"""nyc-hunt CLI: init | run | add | report."""
import argparse
import json
import shutil
import sys
from pathlib import Path

from . import config as config_mod
from . import report as report_mod
from .emailer import EmailError, send
from .models import listing_from_dict
from .score import matches, priority
from .sources import SOURCES
from .tracker import Tracker


def _paths(config_path: str):
    cfg_file = Path(config_path).resolve()
    base = cfg_file.parent
    return cfg_file, base / "data" / "tracker.db", base / "reports"


def _ingest(listings, cfg, tracker):
    stats = {"found": 0, "new": 0, "dup": 0, "high": 0, "medium": 0, "low": 0}
    new_hashes = set()
    for l in listings:
        stats["found"] += 1
        s = cfg.search_by_name(l.search_type)
        if not s or not matches(l, s):
            continue
        pri = priority(l, s, cfg)
        if tracker.add(l, pri):
            stats["new"] += 1
            stats[pri] += 1
            new_hashes.add(l.dedupe_hash())
        else:
            stats["dup"] += 1
    return stats, new_hashes


def _finish(cfg, tracker, stats, new_hashes, reports_dir, email_ok=True):
    html, md = report_mod.render(tracker.active(), tracker.counts(), new_hashes)
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "latest.html").write_text(html)
    (reports_dir / "latest.md").write_text(md)
    if email_ok and cfg.email.enabled and stats["new"]:
        try:
            send(cfg.email, f"NYC hunt: {stats['new']} new ({stats['high']} high)", html)
        except EmailError as e:
            print(f"email failed (run continues): {e}", file=sys.stderr)
    print(f"found={stats['found']} new={stats['new']} dup={stats['dup']} "
          f"high={stats['high']} med={stats['medium']} low={stats['low']}")


def cmd_init(args) -> int:
    dst = Path(args.config)
    if dst.exists():
        print(f"{dst} already exists")
        return 1
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(Path(__file__).parent / "config.example.toml", dst)
    print(f"wrote {dst} — edit your budget, areas and move-in date, then run: nyc-hunt run")
    return 0


def cmd_run(args) -> int:
    cfg_file, db, reports_dir = _paths(args.config)
    cfg = config_mod.load(cfg_file)
    tracker = Tracker(db)
    wanted = {k: f for k, f in SOURCES.items() if not args.source or k in args.source}
    all_listings, failures = [], []
    for name, fetch in wanted.items():
        try:
            all_listings += fetch(cfg)
        except Exception as e:  # noqa: BLE001 — a blocked source must not kill the run
            failures.append(name)
            print(f"source {name} failed: {e}", file=sys.stderr)
    stats, new_hashes = _ingest(all_listings, cfg, tracker)
    _finish(cfg, tracker, stats, new_hashes, reports_dir, email_ok=not args.no_email)
    return 1 if wanted and len(failures) == len(wanted) else 0


def cmd_add(args) -> int:
    cfg_file, db, reports_dir = _paths(args.config)
    cfg = config_mod.load(cfg_file)
    tracker = Tracker(db)
    raw = sys.stdin.read() if args.file == "-" else Path(args.file).read_text()
    invalid, listings = 0, []
    for d in json.loads(raw):
        try:
            listings.append(listing_from_dict(d))
        except (ValueError, TypeError):
            invalid += 1
    stats, new_hashes = _ingest(listings, cfg, tracker)
    stats["found"] += invalid
    if invalid:
        print(f"skipped_invalid={invalid}")
    _finish(cfg, tracker, stats, new_hashes, reports_dir)
    return 0


def cmd_report(args) -> int:
    cfg_file, db, reports_dir = _paths(args.config)
    cfg = config_mod.load(cfg_file)
    tracker = Tracker(db)
    _finish(cfg, tracker, {"found": 0, "new": 0, "dup": 0, "high": 0, "medium": 0, "low": 0},
            set(), reports_dir, email_ok=False)
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="nyc-hunt", description="Automated NYC apartment hunt")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("init", "run", "add", "report"):
        sp = sub.add_parser(name)
        sp.add_argument("--config", default="config.toml")
        if name == "run":
            sp.add_argument("--source", action="append")
            sp.add_argument("--no-email", action="store_true")
        if name == "add":
            sp.add_argument("--json", action="store_true", required=True)
            sp.add_argument("file", nargs="?", default="-")
    args = p.parse_args(argv)
    return {"init": cmd_init, "run": cmd_run, "add": cmd_add, "report": cmd_report}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
