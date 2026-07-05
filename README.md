# nyc-apartment-hunt

Automated NYC apartment hunt. A Python CLI scrapes the scrape-tolerant sources,
dedupes everything into a SQLite tracker, scores each listing HIGH / MEDIUM /
LOW against *your* criteria, and renders a ranked digest (optionally emailed).
An optional Claude Code skill adds the two platforms that block scrapers —
StreetEasy and Zillow — by browsing them like a human.

Inspired by [london-property-hunt](https://github.com/mikepapadim/london-property-hunt-public),
rebuilt as config-driven code for New York.

## Sources

| Source | Coverage | How |
|---|---|---|
| **StreetEasy** | THE NYC platform — most inventory | Claude skill (browser) |
| **Zillow** | Second most common in NYC | Claude skill (browser) |
| **Craigslist** | High volume, owner-listed / no-fee finds | Python scraper |
| **RentHop** | Aggregator, good freshness | Python scraper (best-effort, see below) |

**Works without Claude:** the CLI alone gives you Craigslist + RentHop, the
tracker, scoring, and the digest. The skill is a booster, not a requirement.

## Quickstart

```bash
# with uv (recommended)
uv tool install nyc-apartment-hunt   # or: git clone + uv run nyc-hunt ...
mkdir my-hunt && cd my-hunt
nyc-hunt init          # writes config.toml
$EDITOR config.toml    # budget, areas, move-in date — everything is a knob
nyc-hunt run           # scrape → dedupe → score → reports/latest.html
```

Re-run as often as you like — the tracker dedupes by listing URL, so you only
ever see genuinely new listings marked NEW. Cron it, or use Claude Code's
`/schedule` for twice-daily runs.

## Configuration (`config.toml`)

Every spec lives in config — nothing is hardcoded:

- `[[search]]` blocks — one per apartment type you want. Ships with two
  examples: `studio_1br` (≤ $3,600, 0–1 beds) and `2br_2ba` (≤ $5,000, 2 beds,
  2+ baths). Add, edit, or delete freely; `name` is the join key everywhere.
- `[areas] tier1 / tier2` — neighborhoods that score HIGH / MEDIUM. Anything
  else scores LOW. Case-insensitive substring match.
- `[hunt] move_in` — listings available within ±3 weeks of this date score best.
- `[hunt] no_fee_preferred` — broker-fee listings need $200+ budget headroom to
  stay HIGH.
- `[email]` — optional digest email (see below).

## Scoring

Deterministic — no AI involved:

| Priority | Rule |
|---|---|
| HIGH | tier1 area AND in budget AND (no fee OR ≥$200 under budget) AND available in window |
| MEDIUM | tier1 with exactly one flag, or tier2 in window |
| LOW | everything else that still matches a search |

Listings that match no `[[search]]` block are dropped entirely.

## Commands

```
nyc-hunt init                  # scaffold config.toml
nyc-hunt run [--source craigslist] [--no-email]
nyc-hunt add --json file.json  # ingest listings from anywhere ('-' = stdin)
nyc-hunt report                # re-render reports/latest.{html,md}
```

All commands end with a machine-readable line:
`found=N new=N dup=N high=N med=N low=N`.

## The Claude skill (StreetEasy + Zillow)

Install [`skill/SKILL.md`](skill/SKILL.md) as a Claude Code skill (requires the
Claude in Chrome extension). It browses StreetEasy and Zillow per your config,
extracts listings as JSON, and pipes them into `nyc-hunt add --json` — same
tracker, same scoring, one digest. Schedule it with `/schedule` for hands-off
hunting.

## Email digest

Set `[email] enabled = true`, fill in `to` / `smtp_user`, and export a Gmail
[app password](https://support.google.com/accounts/answer/185833):

```bash
export NYC_HUNT_SMTP_PASS="xxxx xxxx xxxx xxxx"
```

Emails send only when a run finds new listings. Email failure never fails a run.

## Source reliability

Scraping is polite by design: sequential requests, 2–4 s jittered delays, an
honest UA, no proxy rotation, no CAPTCHA solving. If a site blocks the request
anyway, that source reports `failed` on stderr and the run continues — `run`
only exits non-zero when **every** source fails.

- **Craigslist** serves static no-JS results and works reliably (153 live
  listings parsed at build time).
- **RentHop** sits behind a Cloudflare challenge in many environments; when
  blocked it degrades gracefully. Its parser is tested against representative
  fixture markup.
- **StreetEasy / Zillow** are deliberately *not* scraped by code — use the skill.

## Disclaimer

Personal-use tool. Respect each platform's terms of service and rate limits.
Listing data belongs to the respective platforms. Not affiliated with
StreetEasy, Zillow, Craigslist, or RentHop.

## License

MIT
