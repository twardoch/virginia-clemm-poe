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
Local evidence: `331-theme-points-local.json`. Publication/live evidence follows.
