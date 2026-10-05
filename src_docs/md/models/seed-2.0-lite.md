# [seed-2.0-lite](https://poe.com/seed-2.0-lite){ .md-button .md-button--primary }

## Pricing

### API Pricing (USD)

| Type | Cost |
|------|------|
| Prompt | $3.157E-7/token |
| Completion | $0.0000025253/token |

## Bot Information

**Creator:** @empiriolabsai

**Description:** Seed 2.0 Lite is a balanced model designed for high-frequency enterprise workloads, optimizing for both capability and cost. Its overall performance surpasses the previous-generation ByteDance-Seed-1.8. It is well-suited for production tasks such as unstructured information processing, text content creation, search and recommendation, and data analysis. The model supports long-context processing, multi-source information fusion, multi-step instruction execution, and high-fidelity structured outputs—delivering stable quality while significantly reducing cost.
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

**Model ID:** `seed-2.0-lite`

**Object Type:** model

**Created:** 1772817225611

**Owned By:** EmpirioLabs AI

**Root:** seed-2.0-lite

**API Last Updated:** 2026-10-05 01:48:43.415530
