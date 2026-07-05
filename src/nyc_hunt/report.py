"""Render the ranked digest. Same data → HTML (email/browser) and markdown (terminal/vault)."""
from html import escape

ORDER = ("high", "medium", "low")
COLORS = {"high": "#1a7f37", "medium": "#9a6700", "low": "#6e7781"}


def _card(r: dict, is_new: bool) -> str:
    bits = [f"${r['price']:,}", r.get("neighborhood") or "?"]
    if r.get("beds") is not None:
        bits.append("Studio" if r["beds"] == 0 else f"{r['beds']:g} bd")
    if r.get("baths") is not None:
        bits.append(f"{r['baths']:g} ba")
    if r.get("no_fee"):
        bits.append("NO FEE")
    if r.get("available_date"):
        bits.append(f"avail {r['available_date']}")
    badge = ' <b style="color:#cf222e">NEW</b>' if is_new else ""
    return (f'<div style="border:1px solid #d0d7de;border-radius:6px;padding:10px;margin:8px 0">'
            f'<a href="{escape(r["url"])}" style="font-size:16px">{escape(r.get("address") or r["url"])}</a>{badge}'
            f'<div style="color:#57606a">{escape(" · ".join(bits))} · {escape(r["source"])}</div></div>')


def render(rows: list[dict], counts: dict, new_hashes: set[str]) -> tuple[str, str]:
    html = [f"<h2>NYC Apartment Hunt</h2><p>HIGH {counts['high']} · MED {counts['medium']} · "
            f"LOW {counts['low']} · total {counts['total']}</p>"]
    md = [f"# NYC Apartment Hunt\n\nHIGH {counts['high']} · MED {counts['medium']} · LOW {counts['low']}\n"]
    for pri in ORDER:
        group = [r for r in rows if r["priority"] == pri]
        if not group:
            continue
        html.append(f'<h3 style="color:{COLORS[pri]}">{pri.upper()} ({len(group)})</h3>')
        md.append(f"\n## {pri.upper()} ({len(group)})\n")
        for r in group:
            html.append(_card(r, r["dedupe_hash"] in new_hashes))
            star = " **NEW**" if r["dedupe_hash"] in new_hashes else ""
            md.append(f"- [{r.get('address') or r['url']}]({r['url']}) — ${r['price']:,}, "
                      f"{r.get('neighborhood') or '?'} ({r['source']}){star}")
    return "".join(html), "\n".join(md)
