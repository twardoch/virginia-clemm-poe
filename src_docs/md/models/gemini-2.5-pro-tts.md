---
this_file: src_docs/md/models/gemini-2.5-pro-tts.md
---

# [gemini-2.5-pro-tts](https://poe.com/gemini-2.5-pro-tts){ .md-button .md-button--primary }

**Tier 4:** From 100 points · 1,000 input tokens only

[Comparison method and assumptions](../pricing-method.md).

## Pricing

### Website Pricing

| Type | Cost |
|------|------|
| Input (Text Tokens) | 100 ($0.0030) points / 1k tokens |
| Output (Audio Tokens) | 2000 ($0.061) points / 1k tokens |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| Input (text tokens) | USD | 0.0030 | 1000 tokens |
| Input (text tokens) | POINTS | 100 | 1000 tokens |
| Output (audio tokens) | USD | 0.061 | 1000 tokens |
| Output (audio tokens) | POINTS | 2000 | 1000 tokens |

**Last Checked:** 2026-10-05T02:12:00.953154+00:00


## Bot Information

**Creator:** empiriolabsai

**Description:** Gemini‑2.5‑Pro‑TTS is Google’s highest‑quality text‑to‑speech model preview, designed for complex workflows like podcasts, audiobooks, and customer support; it delivers expressive, accent‑ and style‑controllable single‑ or multi‑speaker speech, supporting over 23 languages, and built for state‑of‑the‑art output with the most powerful model architecture.

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

**Model ID:** `gemini-2.5-pro-tts`

**Object Type:** model

**Created:** 1758861500162

**Owned By:** EmpirioLabs AI

**Root:** gemini-2.5-pro-tts

**API Last Updated:** 2026-10-05 01:48:43.417010
