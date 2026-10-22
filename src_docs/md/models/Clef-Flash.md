---
this_file: src_docs/md/models/Clef-Flash.md
---

# [Clef-Flash](https://poe.com/Clef-Flash){ .md-button .md-button--primary }

**Tier 1:** 4.75 points · 1,000 tokens (500 input + 500 output)

[Comparison method and assumptions](../pricing-method.md).

## Pricing

### Website Pricing

| Type | Cost |
|------|------|
| Input Text | 2.5 points/1k tokens |
| Output (Text) | $0.20/1M tokens · 7 points/1k tokens |
| Input (File) | $0.00000416/KB (64 est. tokens) · 0.16 points/KB |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| Input (text) | USD | 0.065 | 1000000 tokens |
| Input (text) | POINTS | 2.5 | 1000 tokens |
| Output (text) | USD | 0.20 | 1000000 tokens |
| Output (text) | POINTS | 7 | 1000 tokens |
| Input (file) | USD | 0.00000416 | 1 kb |
| Input (file) | POINTS | 0.16 | 1 kb |

**Last Checked:** 2026-10-22 13:00:01.907691


## Bot Information

**Creator:** @OpenSourceLab

**Description:** Clef-flash evaluates your input state alongside a schema of typed questions and returns a calibrated probability for every allowed option. This ultra-low-latency, open-weight decision model serves as a drop-in, Jev alternative tailored for high-volume, real-time pipelines. It supports PDF and XLSX files. Clef-Flash does not support video and audio attachments.

Developed by Cloudflare and released on October 1, 2026, Clef-flash is a 9-billion parameter model built on a post-trained Qwen3.5-9B backbone. Unlike traditional language models that sequentially generate free-form sentences, it processes requests via a non-autoregressive, prefill-only forward pass, scoring permitted choices in parallel through a joint decision head.

**Extra:** Powered by a server managed by @OpenSourceLab. Learn more


## Architecture

**Input Modalities:** Unknown

**Output Modalities:** Unknown

**Modality:** unknown


## Technical Details

**Model ID:** `Clef-Flash`

**Object Type:** bot

**Created:** Unknown

**Owned By:** OpenSourceLab

**Root:** Clef-Flash

**API Last Updated:** Not listed in API
