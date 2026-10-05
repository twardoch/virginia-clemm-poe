---
this_file: src_docs/md/models/gemini-2.5-flash-tts.md
---

# [gemini-2.5-flash-tts](https://poe.com/gemini-2.5-flash-tts){ .md-button .md-button--primary }

**Tier 3:** From 50 points · 1,000 input tokens only

[Comparison method and assumptions](../pricing-method.md).

## Pricing

### Website Pricing

| Type | Cost |
|------|------|
| Input (Text Tokens) | 50 ($0.0015) points / 1k tokens |
| Output (Audio Tokens) | 1000 ($0.030) points / 1k tokens |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| Input (text tokens) | USD | 0.0015 | 1000 tokens |
| Input (text tokens) | POINTS | 50 | 1000 tokens |
| Output (audio tokens) | USD | 0.030 | 1000 tokens |
| Output (audio tokens) | POINTS | 1000 | 1000 tokens |

**Last Checked:** 2026-10-05T02:13:39.944848+00:00


## Bot Information

**Creator:** empiriolabsai

**Description:** Gemini‑2.5‑Flash‑TTS is Google’s low‐latency text‑to‑speech model that converts text input into audio output, supporting both single‑ and multi‑speaker voices with controllable style, accent, and expressive tone — ideal for applications like podcasts, audiobooks, and conversational voice systems.

Notes:
- Text and style prompt limited to 4,000 bytes each (8,000 bytes combined)
- Max output duration: approximately 10 minutes
- Multi-speaker requires SpeakerName: text format (example: Alice: Hi! Bob: Hello, must be on new lines)
- The model auto-detects the input language. The Language setting is a hint to help choose the right voice/accent, the model may override it if the text is in a different language.

This bot supports optional parameters for additional customization.


## Architecture

**Input Modalities:** text

**Output Modalities:** text

**Modality:** text->text


## Technical Details

**Model ID:** `gemini-2.5-flash-tts`

**Object Type:** model

**Created:** 1758667568690

**Owned By:** EmpirioLabs AI

**Root:** gemini-2.5-flash-tts

**API Last Updated:** 2026-10-05 01:48:43.418826
