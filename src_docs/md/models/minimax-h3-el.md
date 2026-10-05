---
this_file: src_docs/md/models/minimax-h3-el.md
---

# [minimax-h3-el](https://poe.com/minimax-h3-el){ .md-button .md-button--primary }

**Tier 7:** From 60,000 points · per 10 seconds video

[Comparison method and assumptions](../pricing-method.md).

## Pricing

### Website Pricing

| Type | Cost |
|------|------|
| 768P | $0.18/sec · 6,000 pts/sec |
| 2K | $0.26/sec · 8,667 pts/sec |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| 768p | USD | 0.18 | 1 second |
| 768p | POINTS | 6000 | 1 second |
| 2K | USD | 0.26 | 1 second |
| 2K | POINTS | 8667 | 1 second |

**Last Checked:** 2026-10-05T02:13:35.093556+00:00


## Bot Information

**Creator:** empiriolabsai

**Description:** MiniMax H3 is a multimodal video generation model that produces 4 to 15 second clips at 768p or 2K, 24 fps, each with a native stereo audio track. It supports Text-to-Video, Image-to-Video, First/Last Frame, and Reference-to-Video, auto-detected from your attachments or set manually.

Input Limits & Requirements
- Prompt: up to 7,000 characters. Can describe action, camera work, dialogue, sound effects, and on-screen text
- Images: JPEG, PNG, WEBP, or HEIC. 256 to 5760px per side, aspect ratio within 1:2.5-2.5:1, max 30MB each
- Videos: MP4, MOV, MKV, or WEBM. 2 to 15 seconds each, max 50MB each
- Audio: WAV or MP3. 2 to 15 seconds each, max 15MB each, and requires an accompanying image or video reference
- Image-to-Video: 1 image (the opening frame). First/Last Frame: exactly 2 images
- Reference-to-Video: max 9 images, 3 videos, and 3 audio clips, 12 files total

This bot supports optional parameters for additional customization.


## Architecture

**Input Modalities:** text

**Output Modalities:** text, video

**Modality:** text->text+video


## Technical Details

**Model ID:** `minimax-h3-el`

**Object Type:** model

**Created:** 1785757782897

**Owned By:** EmpirioLabs AI

**Root:** minimax-h3-el

**API Last Updated:** 2026-10-05 01:48:43.418785
