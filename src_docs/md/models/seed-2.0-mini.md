# [seed-2.0-mini](https://poe.com/seed-2.0-mini){ .md-button .md-button--primary }

## Pricing

### API Pricing (USD)

| Type | Cost |
|------|------|
| Prompt | $1.263E-7/token |
| Completion | $5.051E-7/token |

## Bot Information

**Creator:** @empiriolabsai

**Description:** Seed-2.0-Mini from Bytedance targets latency-sensitive, high-concurrency, and cost-sensitive scenarios, emphasizing fast response and flexible inference deployment. It supports 256k context, four reasoning effort modes, and multimodal understanding (including image and video), and is optimized for lightweight tasks where cost and speed take priority.
This model is served from Malaysia.

Note: Pricing is 2x when input tokens >128k

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

**Model ID:** `seed-2.0-mini`

**Object Type:** model

**Created:** 1771632981140

**Owned By:** EmpirioLabs AI

**Root:** seed-2.0-mini

**API Last Updated:** 2026-10-05 01:48:43.415625
