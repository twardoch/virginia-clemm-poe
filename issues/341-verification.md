---
this_file: issues/341-verification.md
---

# Issue 341: refreshed Poe catalogue

Refreshed on 4 November 2026: **471 active bots**, including **all 99 requested handles**. Added 14 entries, removed 33 unavailable/private bots and consolidated two duplicate aliases. **456 bots have newly observed numeric website prices; 15 have none.**

The API and all 28 vendor profiles completed discovery. The full sweep covered 506 candidates, including every previous bot and every requested handle. Corrected hydrated display-name handling exposed Kimi-K3.1-Pro-T during a second discovery pass; its price was also scraped.

Every removal has a separate live recheck. Private/inaccessible pages and deleted bots are retained in the evidence, not mistaken for temporary extraction failures. Both alias URLs were checked against their canonical bot IDs. No model generation was requested.

Website-rate parsing now prefers an equally or more complete public Markdown rate card over a partial HTML table. Reparsed saved disclosures without changing observation dates; all 471 package/site price records agree exactly. The seven affected records retain additional USD rates or explicit video-duration units.

Explicit public handles outside discovery are packaged in `extra_bots.txt`: G5-LM, mimo-v2.6-flash, mimo-v2.6-pro and Qwen3.8-27B. Normal forced updates retain and scrape them.

For the 15 missing numeric prices, reviewed all rate dialogs/public rate cards. Most cards say that details are unavailable; three describe variable calls to other bots. Aplomb-1 returns an empty rate table. Account Points content is excluded. These cases are labelled “Rates dialog contains no numeric pricing”; no old website price is presented as fresh.

## Verification

- Strict clean MkDocs build passes. Exact canonical filenames exist for all 471 bots; obsolete generated pages are absent.
- Every package rate and observation date matches the served JSON. Public data aliases agree byte for byte.
- Browser checks cover every tier, modality and creator, combined filters, search, currency, sorting, dark mode, mobile width, native navigation/search and zero page errors.
- Regression: 236 Python and 18 JavaScript checks pass; vendor-module coverage is 100%. Hatch's existing global coverage gate fails at 65.23% against 85%. Source fixtures cover canonical display names, explicit-handle persistence, partial rate tables and account points exclusion. Real scraper smoke matches all 26 GPT-Image-1.5 and 44 Pixverse-v5.6 saved rates.
- No dependency was added. No credentials, viewer payloads or account balances are included in the evidence.

Source JSON SHA-256: `a21465d7e294fe21458f906c54f6b63f25ee63fd74ad23b0044311cc8f712704`. [Full public observations and rechecks](341-refresh.json). [Rendered catalogue checks](341-site-checks.json). [Site SHA-256 manifest](341-site-hashes.json).

## Removed or consolidated handles

| Previous handle | Result |
|---|---|
| DeepSeek-V3.2-Exp | Private/inaccessible |
| DeepSeek-V4-Pro-N | Private/inaccessible |
| Kimi-K2-Instruct-N | Private/inaccessible |
| MiMo-V2-Flash | Private/inaccessible |
| Muse-Spark-1.1 | Alias of muse-spark-1-1 |
| Qwen-V3.8-Max | Private/inaccessible |
| Qwen3-235B-0527-T | Alias of Qwen-3-235B-2507-T |
| Qwen3-Coder-Next-N | Private/inaccessible |
| Search-OSL | Private/inaccessible |
| Wan-2.6-N | Private/inaccessible |
| amazon-nova-reel-1.1 | Private/inaccessible |
| deepseek-v4-0731 | Private/inaccessible |
| deepseek-v4-pro-0813-ds | Deleted/unavailable |
| deepseek-v4.1-1017 | Private/inaccessible |
| deepseek-vision-exp | Private/inaccessible |
| ds-v4.1-flash-el | Private/inaccessible |
| gemma-4-31b-n | Private/inaccessible |
| glm-4.6v-n | Private/inaccessible |
| glm-5.2-n | Private/inaccessible |
| gpt-oss-20b-n | Private/inaccessible |
| hy3-n | Private/inaccessible |
| kimi-k2.7-code-n | Private/inaccessible |
| mimo-v2.6-flash-xiaomi | Deleted/unavailable |
| minimax-speech-2.8 | Private/inaccessible |
| qwen3-235b-a22b-n | Private/inaccessible |
| qwen3-coder-480b-n | Private/inaccessible |
| qwen3-max-n | Private/inaccessible |
| qwen3-next-80b | Private/inaccessible |
| qwen3-next-80b-think | Private/inaccessible |
| qwen3-vl-235b-a22b-i | Private/inaccessible |
| qwen3-vl-235b-a22b-t | Private/inaccessible |
| qwen3.8-2.4t-a95b-n | Private/inaccessible |
| qwen3.8-27b-alibaba | Deleted/unavailable |
| z9340pub | Deleted/unavailable |
| ztest-9233 | Deleted/unavailable |

## Added handles

G5-LM, GPT-6.1-Terra, Kimi-K3.1-Pro-T, Kolibri-1, Mistral-Small-4-OSL, Object-Generator, Qwen3-Coder-30B, Qwen3.8-27B, Subject-Generator, Z-Image-OSL, gemma-4-31b-vercel, glm-5.3-fast, kimi-k3.1-pro, mercury-3-vercel.
