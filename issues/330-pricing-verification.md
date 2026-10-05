---
this_file: issues/330-pricing-verification.md
---

# Pricing correction verification — 2026-10-05

The entire 501-bot catalogue was inspected through its public Rates response.
Evidence: [`330-pricing-evidence/`](330-pricing-evidence/), one JSON per bot with
the collection timestamp, public profile, rendered tables, and raw rate cards.
All 501 pages were observed after retrying hidden rate triggers.

| Measure | Before | After |
|---|---:|---:|
| Numeric prices displayed by table | 159 | 483 |
| Missing numeric prices | 342 | 18 |
| Zero-cost bots displayed correctly | Incorrectly sorted/omitted | 23 |

Amounts and denominators are parsed with Decimal. Table rows, Markdown rate
cards, prose fees, paired currencies, scientific notation, ranges, milli-cent
markers, and image quality matrices are covered. Struck-out prices, discounts,
and temporary free allowances are excluded. Missing rates are not invented.
Script bots with a disclosed 1-point base fee show a lower bound; bots that only
list possible called models remain usage-dependent.

Default sorting uses point prices, with USD-only prices grouped separately.
Text references use 1k input + 1k output tokens plus the message fee. Other rows
show the relevant disclosed unit/tier; different units are not equivalent.
USD selection uses disclosed dollars or separately labelled API rates.

Local validation:

- `./test.sh`: 183 Python tests; 5 JavaScript comparison tests; vendor coverage 100%.
- Parser coverage: 99%, exceeding the focused 85% threshold.
- `uv run mkdocs build --clean --strict -f src_docs/mkdocs.yml`: passes.
- Pydantic validates all persisted rates; package/source/site JSON hashes match.
- Rendered iframe: 501 rows, 483 prices, 23 zeros first, unknowns last ascending
  and descending, USD switching, search, fee display, 73 image-filter results,
  and no browser page errors. No literal `N/A` cells remain.
- Canonical model filename casing is recorded in Git and regenerated safely.

The remaining 18 bots publish no numeric rate or disclose only variable calls:
canvas-creator, claude-code, code-editor, FLUX-anime, FLUX-pixel-art, GitHub,
HunyuanVideo, hy3-n, imgsys.org, ling-3.0-flash-fin, ling-3.0-flash-vl, Playwright,
qwen3.8-27b, Restyler-Deprecated, script-bot-creator, Seedream-VTON, Style-Studio,
and StyleMaker.

Release procedure: `uvx gitnextver`, followed by GitHub Pages completion and a
fresh live iframe check plus exact asset hash comparison. General CI retains
the previously documented repository lint/test-environment issues; local tests
and strict documentation validation above are independently verified.
