---
this_file: src_docs/md/models/qwen3.5-plus-el.md
---

# [qwen3.5-plus-el](https://poe.com/qwen3.5-plus-el){ .md-button .md-button--primary }

**Tier 4:** 210 points · 1,000 tokens (500 input + 500 output) + message fee

[Comparison method and assumptions](../pricing-method.md).

## Pricing

### API Pricing (USD)

| Type | Cost |
|------|------|
| Prompt | $3.636E-7/token |
| Completion | $0.0000022303/token |

### Website Pricing

| Type | Cost |
|------|------|
| Input (Text) | $0.36/1M tokens · 12 points/1k tokens |
| Output (Text) | $2.23/1M tokens · 74 points/1k tokens |
| Bot Message | $0.0051/message · 167 points/message |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| Input (text) | USD | 0.36 | 1000000 tokens |
| Input (text) | POINTS | 12 | 1000 tokens |
| Output (text) | USD | 2.23 | 1000000 tokens |
| Output (text) | POINTS | 74 | 1000 tokens |
| Bot message | USD | 0.0051 | 1 message |
| Bot message | POINTS | 167 | 1 message |

**Last Checked:** 2026-10-05T02:10:45.090466+00:00


## Bot Information

**Creator:** empiriolabsai

**Description:** Qwen3.5-Plus is a state-of-the-art multimodal model featuring a hybrid architecture designed for efficient deep thinking and robust visual understanding. It supports text, image, and video inputs within a massive 1M token context window, delivering performance comparable to leading global models across diverse tasks.
This model is served by Alibaba Cloud Int. from Singapore.

Notes:
- Save 10% on input tokens and 8% on output tokens compared to standard API rates.
- Pricing is 3x when input tokens >256K
- Context Window: 1,000,000
- Text, Image, & Video input are supported
- Built-in tool calls are not supported with video attachments

This bot supports optional parameters for additional customization.


## Architecture

**Input Modalities:** text, image, video

**Output Modalities:** text

**Modality:** text,image,video->text


## Technical Details

**Model ID:** `qwen3.5-plus-el`

**Object Type:** model

**Created:** 1771229977166

**Owned By:** EmpirioLabs AI

**Root:** qwen3.5-plus-el

**API Last Updated:** 2026-10-05 01:48:43.415471
