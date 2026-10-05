---
this_file: src_docs/md/models/qwen3-max-thinking-el.md
---

# [qwen3-max-thinking-el](https://poe.com/qwen3-max-thinking-el){ .md-button .md-button--primary }

**Tier 5:** 310 points · 1,000 tokens (500 input + 500 output) + message fee

[Comparison method and assumptions](../pricing-method.md).

## Pricing

### API Pricing (USD)

| Type | Cost |
|------|------|
| Prompt | $0.0000010909/token |
| Completion | $0.0000055758/token |

### Website Pricing

| Type | Cost |
|------|------|
| Input (Text) | $1.09/1M tokens · 36 points/1k tokens |
| Output (Text) | $5.58/1M tokens · 184 points/1k tokens |
| Bot Message | $0.0061/message · 200 points/message |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| Input (text) | USD | 1.09 | 1000000 tokens |
| Input (text) | POINTS | 36 | 1000 tokens |
| Output (text) | USD | 5.58 | 1000000 tokens |
| Output (text) | POINTS | 184 | 1000 tokens |
| Bot message | USD | 0.0061 | 1 message |
| Bot message | POINTS | 200 | 1 message |

**Last Checked:** 2026-10-05T02:10:57.815602+00:00


## Bot Information

**Creator:** empiriolabsai

**Description:** This model is retiring on 2026-10-10. Please switch to: https://poe.com/Qwen3.7-Max
Qwen3-Max-Thinking is a flagship reasoning model that integrates adaptive tool use, autonomously employing search, memory, and code interpretation to address complex tasks. It further optimizes performance through test-time scaling, a strategy that allocates additional computation during inference to improve reasoning accuracy and context efficiency.
This model is served by Alibaba Cloud Int. from Singapore.

Notes:
- Context window: 256K
- Pricing is 2x when input tokens >32K, 2.5x when input tokens >128K
- Save 10% on input tokens and 8% on output tokens compared to standard API rates.

This bot supports optional parameters for additional customization.


## Architecture

**Input Modalities:** text

**Output Modalities:** text

**Modality:** text->text


## Technical Details

**Model ID:** `qwen3-max-thinking-el`

**Object Type:** model

**Created:** 1769457283480

**Owned By:** EmpirioLabs AI

**Root:** qwen3-max-thinking-el

**API Last Updated:** 2026-10-05 01:48:43.415807
