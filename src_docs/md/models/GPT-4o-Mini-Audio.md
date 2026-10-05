---
this_file: src_docs/md/models/GPT-4o-Mini-Audio.md
---

# [GPT-4o-Mini-Audio](https://poe.com/GPT-4o-Mini-Audio){ .md-button .md-button--primary }

**Tier 2:** 22 points · 1,000 tokens (500 input + 500 output)

[Comparison method and assumptions](../pricing-method.md).

## Pricing

### Website Pricing

| Type | Cost |
|------|------|
| Input (Text) | 10 ($0.00028) points / 1K tokens |
| Output (Text) | 34 ($0.0010) points / 1K tokens |
| Input (Audio) | 550 ($0.017) points / 1K tokens |
| Output (Audio) | 1100 ($0.033) points / 1K tokens |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| Input (text) | USD | 0.00028 | 1000 tokens |
| Input (text) | POINTS | 10 | 1000 tokens |
| Output (text) | USD | 0.0010 | 1000 tokens |
| Output (text) | POINTS | 34 | 1000 tokens |
| Input (audio) | USD | 0.017 | 1000 tokens |
| Input (audio) | POINTS | 550 | 1000 tokens |
| Output (audio) | USD | 0.033 | 1000 tokens |
| Output (audio) | POINTS | 1100 | 1000 tokens |

**Last Checked:** 2026-10-05T02:08:58.702117+00:00


## Bot Information

**Creator:** binaai

**Description:** OpenAI's gpt-4o-mini-audio-preview model, brought to Poe as a server bot! This model accepts text and audio inputs and can respond with natural-sounding speech. Learn more at https://platform.openai.com/docs/models/gpt-4o-mini-audio-preview.

When audio output is on, responses include both a voice recording and a text transcript. When audio output is off, one of your messages must include an audio file attachment (audio in previous messages is fine).

Optional parameters:
- enable_audio_output: either true or false to control whether responses are spoken aloud (default: true)
- voice: the name of a voice for voice outputs: "alloy", "ash", "ballad", "cedar", "coral", "echo", "fable", "marin", "nova", "onyx", "sage", or "shimmer" (default: marin)
-  model_snapshot: select a specific model version
- auto_max_tokens: Let the model decide the max number of tokens to output (enabled by default). Disable this option to manually specify a token limit between 10 and 16,384 using the max_tokens parameter.


## Architecture

**Input Modalities:** text

**Output Modalities:** audio

**Modality:** text->audio


## Technical Details

**Model ID:** `GPT-4o-Mini-Audio`

**Object Type:** bot

**Created:** Unknown

**Owned By:** binaai

**Root:** GPT-4o-Mini-Audio

**API Last Updated:** Not listed in API
