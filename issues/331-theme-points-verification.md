---
this_file: issues/331-theme-points-verification.md
---

# Theme, point references and tiers

The requested theme and catalogue changes are generated from the existing
501-model snapshot. No Poe scrape or catalogue refresh is part of this build.
The packaged dataset remains byte-identical to the previous commit.

The source configuration loads the four documented FontLab theme assets on
MaterialX, without the separately loaded FontLab menu/footer components.
Native navigation, local search and the palette picker are browser-verified.

Every generated model carries `point_estimate` and `pricing_tier`. The same
JavaScript implementation runs at build time and in the interactive table;
browser verification compares all 501 results against the generated JSON.
Saved rate cards repair bare point amounts, missing table blank lines, duration
columns/sections and million-token denominators without network collection.

The [published method](../src_docs/md/pricing-method.md) specifies reference
quantities, assumptions, conversion and all ten tier boundaries. Price sources
remain visible. The catalogue-wide conversion is the median of 1,022 positive
matching website point/USD pairs: approximately 33,222 points/$; a bot-specific
conversion takes precedence. Eighteen models have no numeric pricing.

Verification commands:

```bash
uv sync --locked
uv run python src_docs/update_docs.py
./test.sh
uv run pytest tests/test_price_parsing.py --override-ini addopts= \
  --cov=virginia_clemm_poe.pricing --cov-fail-under=85
uv run python scripts/verify_catalogue.py --url=http://127.0.0.1:8765
```

Results: strict clean build passes; 190 Python and 18 JavaScript tests pass;
pricing parser coverage 99.22%, vendor coverage 100%. Rendered acceptance checks
all ten tier filters, every creator/modality option, combined filters, search,
USD switching, unknowns last in both sort directions, all estimate/tier
assignments, width to the right edge, absent side ToC/empty headings, dark-mode
sync, mobile page width, native menu/search and zero browser page errors.

Tier counts 0–9: **22, 20, 43, 75, 85, 64, 62, 92, 20, 18**.
Local evidence: `331-theme-points-local.json` and screenshot.

Published commit: `a7973341bbdc74fcaff5f3257371211f2fa3afae`.
[GitHub Pages deployment](https://github.com/twardoch/virginia-clemm-poe/actions/runs/37328597581)
and [locked documentation build](https://github.com/twardoch/virginia-clemm-poe/actions/runs/37328599058)
pass. The live catalogue repeats all browser acceptance checks without page errors;
see `331-theme-points-live.json` and screenshot. All **509** checked live files
(every model page/index and seven catalogue/site artifacts) match local SHA-256
hashes exactly; see `331-theme-points-live-hashes.json`.

The general CI workflow still fails repository-wide lint and its existing test
environment's inability to import `virginia_clemm_poe`. Its integration/security
jobs pass; the separate locked docs build, Pages publication and directly run
full suite above pass. This site change does not claim the general CI was repaired.
