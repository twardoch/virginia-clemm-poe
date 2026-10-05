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
