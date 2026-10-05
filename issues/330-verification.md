---
this_file: issues/330-verification.md
---

# Issue 330: vendor discovery and advertised free rates

Checked on 2026-10-05 using the existing Poe browser session. No messages were sent.

## Vendor profiles

The shipped `src/virginia_clemm_poe/data/good_vendors.txt` contains the 28 requested profile handles, preserving casing. Normal `update`/`sync_bots()` visits each profile, scrolls its Created panel to the advertised count, unions those bots with the API catalog, and uses the existing info/pricing scraper. API metadata wins when both sources contain a bot. `vendor_profile` records provenance. Website-only bots have no API pricing or API timestamp; unknown creation time is null and unknown modalities are empty.

A failed or incomplete profile scrape logs a warning and retains that vendor's existing bots, including on forced refresh. Successful profiles replace their previous listings. No unrelated profile links enter the bot list.

All 28 live profiles completed: 488 bot listings, 488 unique handles. The complete discovered metadata and per-profile timestamps are in [vendor-profiles.json](330-evidence/vendor-profiles.json).

| Vendor | Created bots |
|---|---:|
| [anthropic](https://poe.com/anthropic) | 13 |
| [binaai](https://poe.com/binaai) | 7 |
| [Bytedance](https://poe.com/Bytedance) | 12 |
| [cartesiateam](https://poe.com/cartesiateam) | 3 |
| [cerebrasai](https://poe.com/cerebrasai) | 1 |
| [deepinfra](https://poe.com/deepinfra) | 8 |
| [deepseek](https://poe.com/deepseek) | 5 |
| [elevenlabsco](https://poe.com/elevenlabsco) | 4 |
| [empiriolabsai](https://poe.com/empiriolabsai) | 110 |
| [fal](https://poe.com/fal) | 109 |
| [fireworksai](https://poe.com/fireworksai) | 14 |
| [google](https://poe.com/google) | 18 |
| [gptrdev](https://poe.com/gptrdev) | 1 |
| [ideogramai](https://poe.com/ideogramai) | 2 |
| [meta](https://poe.com/meta) | 2 |
| [minimax](https://poe.com/minimax) | 3 |
| [moonshotai](https://poe.com/moonshotai) | 4 |
| [novitaai](https://poe.com/novitaai) | 42 |
| [openai](https://poe.com/openai) | 45 |
| [OpenSourceLab](https://poe.com/OpenSourceLab) | 31 |
| [opentools](https://poe.com/opentools) | 3 |
| [poe_tools](https://poe.com/poe_tools) | 6 |
| [reka](https://poe.com/reka) | 3 |
| [tencent](https://poe.com/tencent) | 1 |
| [thinkymachines](https://poe.com/thinkymachines) | 1 |
| [togetherai](https://poe.com/togetherai) | 33 |
| [trytako](https://poe.com/trytako) | 1 |
| [xAI](https://poe.com/xAI) | 6 |

## Free endpoints

All 17 requested bot pages displayed **$0.00/message and 0 points/message** in their Rates table. This verifies the advertised website rate for the observed session at the recorded time. It does not verify API availability, an API price, actual billing after sending a message, or a permanent price guarantee. Public profile descriptions are vendor claims, not independently verified model specifications.

| Bot page | Advertised total rate | Evidence |
|---|---|---|
| [DeepSeek-V4.1-FlashT](https://poe.com/DeepSeek-V4.1-FlashT) | $0.00/message; 0 points/message | [Rates HTML](330-evidence/DeepSeek-V4.1-FlashT.html) |
| [Zai-GLM-5.3](https://poe.com/Zai-GLM-5.3) | $0.00/message; 0 points/message | [Rates HTML](330-evidence/Zai-GLM-5.3.html) |
| [GLM-5.3-Flash-T](https://poe.com/GLM-5.3-Flash-T) | $0.00/message; 0 points/message | [Rates HTML](330-evidence/GLM-5.3-Flash-T.html) |
| [DeepSeek-V4-Pro-813](https://poe.com/DeepSeek-V4-Pro-813) | $0.00/message; 0 points/message | [Rates HTML](330-evidence/DeepSeek-V4-Pro-813.html) |
| [Qwen3.8-2.4T-A95B](https://poe.com/Qwen3.8-2.4T-A95B) | $0.00/message; 0 points/message | [Rates HTML](330-evidence/Qwen3.8-2.4T-A95B.html) |
| [Muse-Glimmer-30B](https://poe.com/Muse-Glimmer-30B) | $0.00/message; 0 points/message | [Rates HTML](330-evidence/Muse-Glimmer-30B.html) |
| [DS-V4-Flash-0731](https://poe.com/DS-V4-Flash-0731) | $0.00/message; 0 points/message | [Rates HTML](330-evidence/DS-V4-Flash-0731.html) |
| [TML-Inkling-Small](https://poe.com/TML-Inkling-Small) | $0.00/message; 0 points/message | [Rates HTML](330-evidence/TML-Inkling-Small.html) |
| [TM-Inkling](https://poe.com/TM-Inkling) | $0.00/message; 0 points/message | [Rates HTML](330-evidence/TM-Inkling.html) |
| [PrismML-Tern-Bonsai](https://poe.com/PrismML-Tern-Bonsai) | $0.00/message; 0 points/message | [Rates HTML](330-evidence/PrismML-Tern-Bonsai.html) |
| [Kimi-K2.7-Code-T](https://poe.com/Kimi-K2.7-Code-T) | $0.00/message; 0 points/message | [Rates HTML](330-evidence/Kimi-K2.7-Code-T.html) |
| [Nemotron-3-Ultra](https://poe.com/Nemotron-3-Ultra) | $0.00/message; 0 points/message | [Rates HTML](330-evidence/Nemotron-3-Ultra.html) |
| [Kimi-K2.6-T](https://poe.com/Kimi-K2.6-T) | $0.00/message; 0 points/message | [Rates HTML](330-evidence/Kimi-K2.6-T.html) |
| [Minimax-M2.7-T](https://poe.com/Minimax-M2.7-T) | $0.00/message; 0 points/message | [Rates HTML](330-evidence/Minimax-M2.7-T.html) |
| [Gemma-4-31B-T](https://poe.com/Gemma-4-31B-T) | $0.00/message; 0 points/message | [Rates HTML](330-evidence/Gemma-4-31B-T.html) |
| [Qwen3.5-9B-T](https://poe.com/Qwen3.5-9B-T) | $0.00/message; 0 points/message | [Rates HTML](330-evidence/Qwen3.5-9B-T.html) |
| [EssentialAI-Rnj-1-T](https://poe.com/EssentialAI-Rnj-1-T) | $0.00/message; 0 points/message | [Rates HTML](330-evidence/EssentialAI-Rnj-1-T.html) |

[free-endpoints.json](330-evidence/free-endpoints.json) records timestamps and extracted table text. [updater-live.json](330-evidence/updater-live.json) records a successful live run of the package scraper for DeepSeek-V4.1-FlashT.

## Regression and packaging

`./test.sh`: 159 regression tests pass; 14 discovery tests provide 100% statement coverage. The source distribution and wheel build successfully and contain the 28 handles. See [direct review](330-review.md). The unchanged repository-wide Hatch coverage gate remains unmet at 53.61% against 85%; no claim is made that this broader gate passes.

## Publication refresh

A fresh public API list contains 342 bots. Union with a fresh scrape of all 28 vendor profiles (488 bots) produces 501 unique catalog entries. All 17 requested bot pages were scraped again through the package updater and their zero-point rates are present in the served JSON and individual rendered pages. Source dataset, documentation-source JSON, and built-site JSON are byte-identical. Strict MkDocs build passes. See [catalog-refresh.json](330-evidence/catalog-refresh.json). Publication uses `uvx gitnextver`; the site is served from committed `main/docs`.
