---
this_file: src_docs/md/models/gpt-audio-mini.md
---

# [gpt-audio-mini](https://poe.com/gpt-audio-mini){ .md-button .md-button--primary }

**Tier 3:** 83.5 points · 1,000 tokens (500 input + 500 output)

[Comparison method and assumptions](../pricing-method.md).

## Pricing

### Website Pricing

| Type | Cost |
|------|------|
| Input (Text) | 34 ($0.0010) points / 1K tokens |
| Output (Text) | 133 ($0.0040) points / 1K tokens |
| Input (Audio) | 550 ($0.017) points / 1K tokens |
| Output (Audio) | 1100 ($0.033) points / 1K tokens |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| Input (text) | USD | 0.0010 | 1000 tokens |
| Input (text) | POINTS | 34 | 1000 tokens |
| Output (text) | USD | 0.0040 | 1000 tokens |
| Output (text) | POINTS | 133 | 1000 tokens |
| Input (audio) | USD | 0.017 | 1000 tokens |
| Input (audio) | POINTS | 550 | 1000 tokens |
| Output (audio) | USD | 0.033 | 1000 tokens |
| Output (audio) | POINTS | 1100 | 1000 tokens |

**Last Checked:** 2026-10-05T02:11:16.157347+00:00


## Bot Information

**Creator:** binaai

**Description:** OpenAI's gpt-audio-mini model, brought to Poe as a server bot! This model accepts text and audio inputs and can respond with natural-sounding speech. Learn more about this model at https://platform.openai.com/docs/models/gpt-audio-mini.

When audio output is on, responses include both a voice recording and a text transcript. When audio output is off, one of the messages in the conversation must include an audio file attachment (audio in previous messages from either you or the bot is fine).

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

**Model ID:** `gpt-audio-mini`

**Object Type:** model

**Created:** 1768926869174

**Owned By:** Bina AI

**Root:** gpt-audio-mini

**API Last Updated:** 2026-10-05 01:48:43.416006
