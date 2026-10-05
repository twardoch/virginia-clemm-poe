---
this_file: src_docs/md/models/seed-2.0-pro.md
---

# [seed-2.0-pro](https://poe.com/seed-2.0-pro){ .md-button .md-button--primary }

**Tier 3:** 73 points · 1,000 tokens (500 input + 500 output)

[Comparison method and assumptions](../pricing-method.md).

## Pricing

### API Pricing (USD)

| Type | Cost |
|------|------|
| Prompt | $6.313E-7/token |
| Completion | $0.0000037879/token |

### Website Pricing

| Type | Cost |
|------|------|
| Input (Text) | $0.63/1M tokens · 21 points/1k tokens |
| Output (Text) | $3.79/1M tokens · 125 points/1k tokens |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| Input (text) | USD | 0.63 | 1000000 tokens |
| Input (text) | POINTS | 21 | 1000 tokens |
| Output (text) | USD | 3.79 | 1000000 tokens |
| Output (text) | POINTS | 125 | 1000 tokens |

**Last Checked:** 2026-10-05T02:10:54.605937+00:00


## Bot Information

**Creator:** empiriolabsai

**Description:** Seed 2.0 Pro is a flagship all-purpose general model designed for complex reasoning and long-chain task execution in the Agent era. It emphasizes multimodal understanding, long-context reasoning, structured generation, and tool-augmented execution. It delivers outstanding performance in handling complex instructions and multi-constraint execution, and can reliably address scenarios such as multi-step complex planning, sophisticated visual-text reasoning, video content understanding, and high-difficulty analysis.
This model is served from Malaysia.

Notes:
- Pricing is 2x when input tokens >128k
- Context Window: 256k
- Temperature and top_p are fixed by the model (temp=1, top_p=0.95).

Parameter controls available:
1. Reasoning
- Default: Thinking enabled
- Reasoning effort \[low, medium, high\]: How deeply the model thinks. Low=fast, Medium=balanced, High=thorough (default: medium). Only applies if thinking is enabled.

2. Search & Vision
- Web Search: Enable real-time web search for up-to-date information (default: false).
- Image Detail \[low, high, xhigh\]: Quality for image understanding. Higher = more accurate but uses more tokens (default: high).
- Video FPS \[0.2-5\]: Frame sampling rate for video input. Higher = more frames analyzed, more accurate, more tokens (default: 1).


## Architecture

**Input Modalities:** text, image, video

**Output Modalities:** text

**Modality:** text,image,video->text


## Technical Details

**Model ID:** `seed-2.0-pro`

**Object Type:** model

**Created:** 1774508584107

**Owned By:** EmpirioLabs AI

**Root:** seed-2.0-pro

**API Last Updated:** 2026-10-05 01:48:43.415700
