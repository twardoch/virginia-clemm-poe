# [qwen3-next-80b-think](https://poe.com/qwen3-next-80b-think){ .md-button .md-button--primary }

## Pricing

### API Pricing (USD)

| Type | Cost |
|------|------|
| Prompt | $1.515E-7/token |
| Completion | $0.0000015152/token |

### Website Pricing

| Type | Cost |
|------|------|
| Input (Text) | $0.15/1M tokens · 5 points/1k tokens |
| Output (Text) | $1.52/1M tokens · 50 points/1k tokens |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| Input (text) | USD | 0.15 | 1000000 tokens |
| Input (text) | POINTS | 5 | 1000 tokens |
| Output (text) | USD | 1.52 | 1000000 tokens |
| Output (text) | POINTS | 50 | 1000 tokens |

**Last Checked:** 2026-10-05T02:11:23.065291+00:00


## Bot Information

**Creator:** novitaai

**Description:** Qwen3-Next uses a highly sparse MoE design: 80B total parameters, but only ~3B activated per inference step. Experiments show that, with global load balancing, increasing total expert parameters while keeping activated experts fixed steadily reduces training loss.Compared to Qwen3’s MoE (128 total experts, 8 routed), Qwen3-Next expands to 512 total experts, combining 10 routed experts + 1 shared expert — maximizing resource usage without hurting performance.
The Qwen3-Next-80B-A3B-Thinking excels at complex reasoning tasks — outperforming higher-cost models like Qwen3-30B-A3B-Thinking-2507 and Qwen3-32B-Thinking, outpeforming the closed-source Gemini-2.5-Flash-Thinking on multiple benchmarks, and approaching the performance of our top-tier model Qwen3-235B-A22B-Thinking-2507.

File Support: Text, Markdown and PDF files
Context window: 131k tokens


## Architecture

**Input Modalities:** text

**Output Modalities:** text

**Modality:** text->text


## Technical Details

**Model ID:** `qwen3-next-80b-think`

**Object Type:** model

**Created:** 1757556610505

**Owned By:** Novita AI

**Root:** qwen3-next-80b-think

**API Last Updated:** 2026-10-05 01:48:43.416167
