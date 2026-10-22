---
this_file: src_docs/md/models/Clef-OSL.md
---

# [Clef-OSL](https://poe.com/Clef-OSL){ .md-button .md-button--primary }

**Tier 2:** 9.5 points · 1,000 tokens (500 input + 500 output)

[Comparison method and assumptions](../pricing-method.md).

## Pricing

### Website Pricing

| Type | Cost |
|------|------|
| Input Text | 5 points/1k tokens |
| Output (Text) | $0.40/1M tokens · 14 points/1k tokens |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| Input (text) | USD | 0.13 | 1000000 tokens |
| Input (text) | POINTS | 5 | 1000 tokens |
| Output (text) | USD | 0.40 | 1000000 tokens |
| Output (text) | POINTS | 14 | 1000 tokens |

**Last Checked:** 2026-10-22 13:00:05.966460


## Bot Information

**Creator:** @OpenSourceLab

**Description:** Clef evaluates your input state alongside a schema of typed questions and returns a calibrated probability for every allowed option. This open-weight decision model is designed for high-volume, real-time pipelines. It supports PDF and XLSX files but does not support video or audio attachments. 

Developed by Cloudflare and released on October 1, 2026, Clef is a 9-billion-parameter model built on a post-trained Qwen3.5-9B backbone. Unlike traditional language models that sequentially generate free-form text, it processes requests through a non-autoregressive, prefill-only forward pass, scoring permitted choices in parallel through a joint decision head.

**Extra:** Powered by a server managed by @OpenSourceLab. Learn more


## Architecture

**Input Modalities:** Unknown

**Output Modalities:** Unknown

**Modality:** unknown


## Technical Details

**Model ID:** `Clef-OSL`

**Object Type:** bot

**Created:** Unknown

**Owned By:** OpenSourceLab

**Root:** Clef-OSL

**API Last Updated:** Not listed in API
