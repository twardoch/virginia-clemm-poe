---
this_file: src_docs/md/models/assistant.md
---

# [assistant](https://poe.com/assistant){ .md-button .md-button--primary }

**Tier 6:** ≈ 2,580 points · per 1024×1024 image (assumed 1290 output tokens)

[Comparison method and assumptions](../pricing-method.md).

## Pricing

### Website Pricing

| Type | Cost |
|------|------|
| Input Text | Up to 17 points/1k tokens |
| Input Image | Up to 17 points/1k tokens |
| Output (Text) | Up to $3.03/1M tokens · Up to 100 points/1k tokens |
| Input (Video) | Up to $0.00028/second · Up to 10 points/second |
| Input (Audio) | Up to $0.00013/second · Up to 5 points/second |
| Web Search | Up to $0.014/search · Up to 467 points/search |
| Cached Input (When Available) | Up to $0.40/1M tokens · Up to 14 points/1k tokens |
| Cache Write Surcharge | Up to $1.01/1M tokens · Up to 34 points/1k tokens |
| Output (Image) | Up to $60.61/1M tokens · Up to 2000 points/1k tokens |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| Input (text) | USD | 0.81 | 1000000 tokens |
| Input (text) | POINTS | 27 | 1000 tokens |
| Output (text) | USD | 3.64 | 1000000 tokens |
| Output (text) | POINTS | 120 | 1000 tokens |
| Input (image) | USD | 0.81 | 1000000 tokens |
| Input (image) | POINTS | 27 | 1000 tokens |
| Input (video) | USD | 0.000057 | 1 second |
| Input (video) | POINTS | 2 | 1 second |
| Input (audio) | USD | 0.000026 | 1 second |
| Input (audio) | POINTS | 1 | 1 second |
| Web search | USD | 0.014 | 1 search |
| Web search | POINTS | 467 | 1 search |
| Cached input (when available) | USD | 0.081 | 1000000 tokens |
| Cached input (when available) | POINTS | 3 | 1000 tokens |
| Cache write surcharge | USD | 0.051 | 1000000 tokens |
| Cache write surcharge | POINTS | 2 | 1000 tokens |
| Input (text) | USD | 4.04 | 1000000 tokens |
| Input (text) | POINTS | 134 | 1000 tokens |
| Output (text) | USD | 18.18 | 1000000 tokens |
| Output (text) | POINTS | 600 | 1000 tokens |
| Input (image) | USD | 4.04 | 1000000 tokens |
| Input (image) | POINTS | 134 | 1000 tokens |
| Input (video) | USD | 0.00028 | 1 second |
| Input (video) | POINTS | 10 | 1 second |
| Input (audio) | USD | 0.00013 | 1 second |
| Input (audio) | POINTS | 5 | 1 second |
| Web search | USD | 0.014 | 1 search |
| Web search | POINTS | 467 | 1 search |
| Cached input (when available) | USD | 0.40 | 1000000 tokens |
| Cached input (when available) | POINTS | 14 | 1000 tokens |
| Cache write surcharge | USD | 1.01 | 1000000 tokens |
| Cache write surcharge | POINTS | 34 | 1000 tokens |
| Input (text) | USD | 0.51 | 1000000 tokens |
| Input (text) | POINTS | 17 | 1000 tokens |
| Output (text) | USD | 3.03 | 1000000 tokens |
| Output (text) | POINTS | 100 | 1000 tokens |
| Input (image) | USD | 0.51 | 1000000 tokens |
| Input (image) | POINTS | 17 | 1000 tokens |
| Output (image) | USD | 60.61 | 1000000 tokens |
| Output (image) | POINTS | 2000 | 1000 tokens |
| Web search | USD | 0.014 | 1 search |
| Web search | POINTS | 467 | 1 search |

**Last Checked:** 2026-10-22 13:19:03.247422


## Bot Information

**Creator:** @poe

**Description:** General-purpose assistant. Write, code, ask for real-time information, create images, and more.

Queries are automatically routed based on the task and subscription status.

For subscribers:
- General queries: @GPT-5.5
- Image generation: @Nano-Banana-2
- Video-input tasks: @Gemini-3.1-Pro

For non-subscribers:
- General queries: @GPT-5.4-Nano
- Image generation: @Nano-Banana-2
- Video-input tasks: @Gemini-3-Flash

**Extra:** Powered by third party model providers. Learn more


## Architecture

**Input Modalities:** text, image, video

**Output Modalities:** image, text

**Modality:** text+image+video->image+text


## Technical Details

**Model ID:** `assistant`

**Object Type:** model

**Created:** 1694610718936

**Owned By:** Poe

**Root:** assistant

**API Last Updated:** 2026-10-22 13:58:59.073362
