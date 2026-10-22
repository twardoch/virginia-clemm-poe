---
this_file: issues/340-poe-verification.md
---

# Issue 340 Poe integration verification — 2026-10-22

VCP340-1/2/3/4 code is implemented and verified. Final delivery follows the
user-selected headless sample with traditional headed fallback on failure, then
commit/push of both repositories. Unmeasured matrix cells remain follow-up coverage.

## Runtime and regression evidence

- 228 Python regression tests pass, with 18 JavaScript checks and 14 vendor tests
  (100% vendor coverage). The 38 focused new-module tests yield 91.81% coverage.
- Changed-file F/I lint passes; targeted mypy for browser settings, auth, manager,
  command scope and private store passes with `MYPYPATH=../playwrightauthor/src`.
  Whole-repository coverage/type/lint is not claimed green.
- [Owned-pool evidence](340-poe-owned-pool.json) uses real browsers and the actual
  Poe adapter/probe/pool, intercepting service requests with deterministic HTML.
  CfT, Chromium and Firefox each share one context across distinct task tabs;
  cancellation closes its tab while other jobs remain usable. A redirected login
  fixture produces AUTH_REQUIRED with no visible login. Latest source-environment 109 window/focus
  samples pass. A separate clean-wheel Playwright 1.64 run passed all three engine
  behavior checks but failed focus stability in 114 samples with no visible browser
  windows. Preserve that failure in 340-poe-owned-pool-clean-wheel-focus-failure.json;
  later passes do not explain it. A new clean-wheel recheck with Playwright 1.64
  passes 122 samples, recording app identifiers and engine phases for any future
  focus transitions (340-poe-clean-wheel-focus-recheck.json). These fixture checks
  use no provider credentials.
- [Live anonymous probe](340-live-unauth-probe.json) visits actual Poe settings in
  a fresh headless Chromium identity and returns AUTH_REQUIRED, without using
  credentials or attempting interactive login. It does not verify signed-in DOM.
- [Package audit](340-poe-package-audit.json) covers local source/wheel byte matches
  and excluded private runtime/work data. Both locally built wheels install into
  a fresh environment and expose the new settings and browser manager API.

## Reproduce the paired development environment

Install project dependencies, then install the paired PlaywrightAuthor source
into VCP's environment. Avoid letting `uv run` resync it to the older published
package during this unreleased integration check. Use `.venv/bin/python` for the
checks below (or an explicit uv override pointing to the paired source).

Local builds use explicit test-only versions:
VCP `0.0.0`, PWA `1.0.23+issue340` for a paired wheel install satisfying VCP's
existing minimum requirement. These are not releases. Source test installations
may use `0.0.0`; a future paired publication must set VCP's minimum to the actual
published session-capable PWA version. Runtime capability detection gives older
installations a clear ENGINE_UNAVAILABLE rather than opening headed fallback UI.

- `.venv/bin/python -m pytest --no-cov`
- `node --test tests/test_price_compare.cjs`
- `.venv/bin/python -m pytest tests/test_vendors.py --override-ini addopts=
  --cov=virginia_clemm_poe.vendors --cov-fail-under=85`
- `.venv/bin/python -m playwright install chromium firefox`
- `.venv/bin/python scripts/verify_owned_pool.py --chrome-binary=PATH_TO_CFT`
- Build both wheels, install them together in a fresh temporary environment, and
  import BrowserManager/BrowserSettings and AsyncBrowserSession.

CLI help verifies browser_engine/profile/mode options on update/balance and
engine/profile/executable options on login. Environment defaults use VCP_BROWSER_*
variables. AUTO auth failures include the explicit profile's login command.

## Safety and failure checks

Tests cover concurrent startup, distinct jobs, pool shutdown cancellation, missing
session APIs, provider refusal, bounded login timeout, failed-login non-export,
OAuth-page preservation, cookie domain/expiry filtering, 0700/0600 permissions,
atomic replace failures, mismatched export identity, stale cache invalidation,
structured auth exit and CLI selection forwarding. The profile cookie jar is
never populated from an HTTP export; legacy unscoped exports stay separate.

## Outstanding acceptance

Intel hardware, additional provider methods, real provider refusals and expired
live sessions remain unverified. Actual typed-text delivery and Stage Manager were
not measured; the controlled keyboard-focus and Spaces observations are below.
The first focus anomaly remains unexplained despite later passing samples.

The user selected `poe-primary` / Chrome for Testing and confirmed manual login.
The original observer timed out on stale selectors. Live inspection found Poe's
new `settings?tab=subscription` and inline points row. Those selectors are fixed;
[headless live evidence](340-live-signed-in.json) verifies saved authorization,
restart reuse, scoped HTTP export and numeric browser balance. A separate normal
`balance --refresh` CLI run succeeded through the headless browser fallback.
No account values or credentials are recorded in that evidence. Login detection
also accepts the current settings tab before the fresh points probe.

The full forced headless update completed into temporary output: 497 valid unique
bots, 476 scraped prices, 20 undisclosed rates and one rendering timeout for
`glm-5.3-zai`. The original dataset stayed unchanged. A three-bot headless sample
updated Analyse-PDF and AnimagineXL, but the same bot timed out again. The user
authorized traditional headed fallback on failure; that incremental update completed successfully.
See 340-live-update-summary.json for the sample result. Full parity is not asserted.

## Coordinated attention test

The user left a text cursor in iTerm for a controlled real-browser test. Across
190 observations, its AXTextArea object stayed focused with no observed frontmost-app change,
new browser windows or active-Space notifications. No field content was read and
no keystrokes were sent. Actual typing delivery and Stage Manager layout were not
measured. See the paired PlaywrightAuthor issues/340-acceptance-matrix.md and its
controlled/uncontrolled JSON files; the earlier FontLab focus change is retained.

## Final headed fallback result

[Saved result](340-headed-update-summary.json) records exit 0 with 492 validated
unique bots, 473 scraped prices, 19 undisclosed rates and no scraping failures or
missing bot information. Fresh discovery removed eight IDs and added three since
the headless run; `glm-5.3-zai` is among the removed IDs. All 470 previously priced
bots still in the catalogue retain their scraped pricing unchanged; all three
added bots have prices. This is a normal incremental fallback over a changing
catalogue, not a full forced parity comparison. Original dataset hashes remain
unchanged because both outputs are isolated verification artifacts.
