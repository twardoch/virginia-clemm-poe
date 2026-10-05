---
this_file: src_docs/md/models/qwen3.5-flash-el.md
---

# [qwen3.5-flash-el](https://poe.com/qwen3.5-flash-el){ .md-button .md-button--primary }

**Tier 5:** 342 points · 1,000 tokens (500 input + 500 output) + message fee

[Comparison method and assumptions](../pricing-method.md).

## Pricing

### API Pricing (USD)

| Type | Cost |
|------|------|
| Prompt | $9.09E-8/token |
| Completion | $3.717E-7/token |

### Website Pricing

| Type | Cost |
|------|------|
| Input (Text) | $0.091/1M tokens · 3 points/1k tokens |
| Output (Text) | $0.37/1M tokens · 13 points/1k tokens |
| Bot Message | $0.010/message · 334 points/message |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| Input (text) | USD | 0.091 | 1000000 tokens |
| Input (text) | POINTS | 3 | 1000 tokens |
| Output (text) | USD | 0.37 | 1000000 tokens |
| Output (text) | POINTS | 13 | 1000 tokens |
| Bot message | USD | 0.010 | 1 message |
| Bot message | POINTS | 334 | 1 message |

**Last Checked:** 2026-10-05T02:10:47.165778+00:00


## Bot Information

**Creator:** empiriolabsai

**Description:** The Qwen3.5 native vision-language Flash models are built on a hybrid architecture that integrates a linear attention mechanism with a sparse mixture-of-experts model, achieving higher inference efficiency. Compared to the 3 series, these models deliver a leap forward in performance for both pure text and multimodal tasks, offering fast response times while balancing inference speed and overall performance.
This model is served by Alibaba Cloud Int. from Singapore.
Save 10% on input tokens and 8% on output tokens compared to standard API rates.

Notes:
- Context Window: 1,000,000
- Text, Image, & Video input are supported
- Built-in tool calls are not supported with video attachments

This bot supports optional parameters for additional customization.


## Architecture

**Input Modalities:** text, image, video

**Output Modalities:** text

**Modality:** text,image,video->text


## Technical Details

**Model ID:** `qwen3.5-flash-el`

**Object Type:** model

**Created:** 1771963175057

**Owned By:** EmpirioLabs AI

**Root:** qwen3.5-flash-el

**API Last Updated:** 2026-10-05 01:48:43.415505
