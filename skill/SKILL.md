---
name: nyc-apartment-hunt
description: Run the NYC apartment hunt across StreetEasy and Zillow using Claude in Chrome, feeding results into the nyc-hunt tracker. Use when the user says "apartment hunt", "run the NYC apartment search", "any new apartments", or wants StreetEasy/Zillow coverage on top of the CLI's Craigslist/RentHop pull.
---

# NYC Apartment Hunt — browser pass (StreetEasy + Zillow)

You are running the user's NYC apartment hunt. StreetEasy and Zillow block plain
scrapers, so you browse them like a human via Claude in Chrome, then hand every
listing to the `nyc-hunt` CLI, which owns dedupe, scoring, the tracker, and the
digest. You never decide priority yourself — the CLI's deterministic scorer does.

## Requirements

- Claude Code with the Claude in Chrome extension connected
- `nyc-apartment-hunt` installed (`uv tool install nyc-apartment-hunt` or a clone)
- A `config.toml` (run `nyc-hunt init` first if missing)

## Steps

1. **Read `config.toml`** in the hunt directory. Note every `[[search]]` block
   (name, max_price, beds_min/max, baths_min), `move_in`, and `no_fee_preferred`.

2. **StreetEasy** — for each `[[search]]`, open:
   `https://streeteasy.com/for-rent/manhattan/price:-{max_price}|beds:{beds_min}-{beds_max}`
   - When `baths_min` > 1, add the bathrooms filter in the UI (URL grammar varies).
   - When `no_fee_preferred`, switch on the "No fee" toggle.
   - Sort by "Newest".

3. **Zillow** — open `https://www.zillow.com/new-york-ny/rentals/`, then via the
   UI: set price max, beds range, baths min per `[[search]]`; draw/select the
   Manhattan boundary; sort newest.

4. **Extract** from the first 2 result pages per search, per site. For each
   listing collect:
   `url, source ("streeteasy" | "zillow"), search_type (the [[search]] name),
   price (integer, monthly), address, neighborhood, beds, baths,
   no_fee (true/false), available_date (YYYY-MM-DD or "")`.
   Skip anything missing a price or URL. Open individual listings only when the
   card lacks beds/baths — and at most a handful per run.

5. **Ingest** — write the combined JSON array to a temp file, then:
   ```bash
   nyc-hunt add --json /tmp/nyc-hunt-batch.json
   nyc-hunt report
   ```
   The `add` output line (`found=… new=… high=…`) is your ground truth.

6. **Summarize** for the user: how many new, the new HIGH/MEDIUM listings with
   links, and where the full digest lives (`reports/latest.html`).

## Rules

- Personal-use scale only. Respect each site's terms of use.
- One tab at a time, no parallel hammering, pause naturally between pages.
- If a CAPTCHA or challenge appears: STOP that site and report it. Never solve
  or bypass a CAPTCHA.
- Never fabricate a listing. If a field is unknown, leave it empty/null.
