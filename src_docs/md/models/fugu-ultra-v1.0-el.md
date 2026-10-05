---
this_file: src_docs/md/models/fugu-ultra-v1.0-el.md
---

# [fugu-ultra-v1.0-el](https://poe.com/fugu-ultra-v1.0-el){ .md-button .md-button--primary }

**Tier 5:** 875 points · 1,000 tokens (500 input + 500 output)

[Comparison method and assumptions](../pricing-method.md).

## Pricing

### API Pricing (USD)

| Type | Cost |
|------|------|
| Prompt | $0.0000075758/token |
| Completion | $0.0000454545/token |

### Website Pricing

| Type | Cost |
|------|------|
| Input (Text) | $7.58/1M tokens · 250 points/1k tokens |
| Output (Text) | $45.45/1M tokens · 1500 points/1k tokens |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| Input (text) | USD | 7.58 | 1000000 tokens |
| Input (text) | POINTS | 250 | 1000 tokens |
| Output (text) | USD | 45.45 | 1000000 tokens |
| Output (text) | POINTS | 1500 | 1000 tokens |

**Last Checked:** 2026-10-05T02:13:18.270929+00:00


## Bot Information

**Creator:** empiriolabsai

**Description:** Fugu Ultra v1.0 is Sakana AI's multi-agent conductor: it coordinates a pool of expert models on every request and composes their work into one answer, built for hard reasoning, coding, and research. It accepts text and image input with a 1M token context.

Notes:
- Responses can take from a few seconds to a few minutes to complete.
- The full answer arrives at once rather than token by token (ie. streaming is not available), because the model finishes its internal work before it replies.
- Extra High and Max reasoning levels are aliases. 

This bot supports optional parameters for additional customization.


## Architecture

**Input Modalities:** text, image

**Output Modalities:** text

**Modality:** text,image->text


## Technical Details

**Model ID:** `fugu-ultra-v1.0-el`

**Object Type:** model

**Created:** 1782177874038

**Owned By:** EmpirioLabs AI

**Root:** fugu-ultra-v1.0-el

**API Last Updated:** 2026-10-05 01:48:43.418247
