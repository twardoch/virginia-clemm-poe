---
this_file: issues/330-review.md
---

# Issue 330 final direct review

Reviewed the current diff against `issues/330.md` and the single-agent repository instructions. Cleanup, standards, specification, and architecture checks were performed directly. The optional ai-slop-cleaner skill is unavailable locally; this record documents the direct cleanup pass instead. No reviewer or Architect agent was used.

## Specification audit

- All 28 requested handles are present, with casing preserved, in the packaged good_vendors.txt; unit test and installed-wheel inspection confirm packaging.
- Profile discovery is called from normal sync_bots before update selection. Created-list hydration and rendered cards are scoped to the profile's Created panel, and longer lists scroll their actual scroll container.
- All 28 profiles reached their advertised count in live checks: 488 unique bots. Incomplete or failed profiles warn and retain existing vendor bots. Forced refresh loads recovery data and forces normal scraping.
- API/profile IDs merge case-insensitively. API metadata wins; prior scraped data survives. Vendor-only entries do not receive fabricated creation dates, modalities, API pricing, or API timestamps. The CLI and stored-data schema support those unknown values.
- Vendor-only entries enter normal scrape/update/persist logic, demonstrated by an integration test including zero-point pricing and reload.
- All 17 requested rate tables were observed live, saved as HTML, and reported as advertised website prices. API access and actual message billing are explicitly unverified.

## Cleanup and standards

Reused Playwright, Beautiful Soup, Pydantic, and Loguru. No runtime dependency, alternate transport, general-purpose scraping framework, custom retry system, or remote messaging was added. Removed an unused import and duplicate pool acquisition. README is under 200 lines. Source files have this_file markers. New-module lint passes except ERA001 is deliberately excluded because it conflicts with the required this_file marker. Existing broader lint debt is unchanged.

## Verification

- All 159 regression tests pass with ./test.sh; the discovery module passes 14 tests at 100% Python statement coverage. Scrolling JavaScript is additionally exercised by all 28 live profile checks.
- Source distribution and wheel build successfully; wheel contains discovery code and all vendor handles. Installed-wheel import verifies the packaged resource.
- Current diff passes git diff --check.
- Full uvx hatch test runs all tests successfully but exits unsuccessfully at the existing repository-wide coverage gate: 53.61% versus 85%. This gate is not claimed to pass and its threshold has not been lowered. The separate discovery coverage check meets 85%.

Direct Standards and Spec review: APPROVE for issue 330. Direct architecture review: CLEAR for this scoped change. The broader coverage debt remains documented separately from the completed issue requirements.
