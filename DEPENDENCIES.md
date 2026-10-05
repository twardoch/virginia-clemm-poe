---
this_file: DEPENDENCIES.md
---

# Dependencies

Issue 330 reuses existing runtime dependencies: Playwright for browser navigation and scrolling, Beautiful Soup for profile/price HTML, Pydantic for persisted bot records, and Loguru for discovery failures. No new runtime package is needed. Hatch test environments explicitly include pytest-cov and pytest-asyncio, matching the existing pytest configuration and async tests. The complete runtime and development requirements remain in `pyproject.toml` and `uv.lock`.

The pricing correction adds Python-Markdown as a direct runtime dependency for
Poe's raw Markdown rate cards, using its maintained table extension. Decimal and
Pydantic preserve exact amounts and denominators; Beautiful Soup handles multiple
tables, image quality matrices, and obsolete-price markup. Node's built-in test
runner checks the browser's shared comparison code without another dependency.

Documentation follows the shared theme's tested versions: ProperDocs 1.6.7,
MaterialX 10.1.8 and PyMdown Extensions 11.0.1. MaterialX replaces stock Material;
the four FontLab theme assets load from the CDN without its global chrome.
Node 22+ executes the same price/tier implementation for static model pages and
browser comparisons. The locked environment is reused by the documentation CI.
