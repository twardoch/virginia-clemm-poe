---
this_file: src_docs/md/models/qwen3-next-80b.md
---

# [qwen3-next-80b](https://poe.com/qwen3-next-80b){ .md-button .md-button--primary }

**Tier 2:** 27.5 points · 1,000 tokens (500 input + 500 output)

[Comparison method and assumptions](../pricing-method.md).

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

**Last Checked:** 2026-10-05T02:11:23.171151+00:00


## Bot Information

**Creator:** novitaai

**Description:** Qwen3-Next uses a highly sparse MoE design: 80B total parameters, but only ~3B activated per inference step. Experiments show that, with global load balancing, increasing total expert parameters while keeping activated experts fixed steadily reduces training loss.Compared to Qwen3’s MoE (128 total experts, 8 routed), Qwen3-Next expands to 512 total experts, combining 10 routed experts + 1 shared expert — maximizing resource usage without hurting performance.
The Qwen3-Next-80B-A3B-Instruct performs comparably to our flagship model Qwen3-235B-A22B-Instruct-2507, and shows clear advantages in tasks requiring ultra-long context (up to 256K tokens).


File Support: Text, Markdown and PDF files
Context window: 131k tokens

**Extra:** Powered by a server managed by @novitaai. Learn more


## Architecture

**Input Modalities:** text

**Output Modalities:** text

**Modality:** text->text


## Technical Details

**Model ID:** `qwen3-next-80b`

**Object Type:** model

**Created:** 1757556042820

**Owned By:** Novita AI

**Root:** qwen3-next-80b

**API Last Updated:** 2026-10-05 01:48:43.416183
