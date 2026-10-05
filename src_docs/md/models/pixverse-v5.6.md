---
this_file: src_docs/md/models/pixverse-v5.6.md
---

# [pixverse-v5.6](https://poe.com/pixverse-v5.6){ .md-button .md-button--primary }

**Tier 7:** From 25,667 points · per 10 seconds video

[Comparison method and assumptions](../pricing-method.md).

## Pricing

### Website Pricing

| Type | Cost |
|------|------|
| 360P | 58667 ($1.78) · 25667 ($0.78) |
| 540P | 58667 ($1.78) · 25667 ($0.78) |
| 720P | 66000 ($2.00) · 33000 ($1.00) |
| 1080P | 100000 ($3.03) · 50000 ($1.52) |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| Video Output (360p; 5 seconds:) | USD | 0.81 | 5 second |
| Video Output (360p; 5 seconds:) | POINTS | 26667 | 5 second |
| Video Output (360p; 5 seconds:) | USD | 0.35 | 5 second |
| Video Output (360p; 5 seconds:) | POINTS | 11667 | 5 second |
| Video Output (540p; 5 seconds:) | USD | 0.81 | 5 second |
| Video Output (540p; 5 seconds:) | POINTS | 26667 | 5 second |
| Video Output (540p; 5 seconds:) | USD | 0.35 | 5 second |
| Video Output (540p; 5 seconds:) | POINTS | 11667 | 5 second |
| Video Output (720p; 5 seconds:) | USD | 0.91 | 5 second |
| Video Output (720p; 5 seconds:) | POINTS | 30000 | 5 second |
| Video Output (720p; 5 seconds:) | USD | 0.45 | 5 second |
| Video Output (720p; 5 seconds:) | POINTS | 15000 | 5 second |
| Video Output (1080p; 5 seconds:) | USD | 1.52 | 5 second |
| Video Output (1080p; 5 seconds:) | POINTS | 50000 | 5 second |
| Video Output (1080p; 5 seconds:) | USD | 0.76 | 5 second |
| Video Output (1080p; 5 seconds:) | POINTS | 25000 | 5 second |
| Video Output (360p; 8 seconds:) | USD | 1.62 | 8 second |
| Video Output (360p; 8 seconds:) | POINTS | 53334 | 8 second |
| Video Output (360p; 8 seconds:) | USD | 0.71 | 8 second |
| Video Output (360p; 8 seconds:) | POINTS | 23334 | 8 second |
| Video Output (540p; 8 seconds:) | USD | 1.62 | 8 second |
| Video Output (540p; 8 seconds:) | POINTS | 53334 | 8 second |
| Video Output (540p; 8 seconds:) | USD | 0.71 | 8 second |
| Video Output (540p; 8 seconds:) | POINTS | 23334 | 8 second |
| Video Output (720p; 8 seconds:) | USD | 1.82 | 8 second |
| Video Output (720p; 8 seconds:) | POINTS | 60000 | 8 second |
| Video Output (720p; 8 seconds:) | USD | 0.91 | 8 second |
| Video Output (720p; 8 seconds:) | POINTS | 30000 | 8 second |
| Video Output (1080p; 8 seconds:) | USD | 3.03 | 8 second |
| Video Output (1080p; 8 seconds:) | POINTS | 100000 | 8 second |
| Video Output (1080p; 8 seconds:) | USD | 1.52 | 8 second |
| Video Output (1080p; 8 seconds:) | POINTS | 50000 | 8 second |
| Video Output (360p; 10 seconds:) | USD | 1.78 | 10 second |
| Video Output (360p; 10 seconds:) | POINTS | 58667 | 10 second |
| Video Output (360p; 10 seconds:) | USD | 0.78 | 10 second |
| Video Output (360p; 10 seconds:) | POINTS | 25667 | 10 second |
| Video Output (540p; 10 seconds:) | USD | 1.78 | 10 second |
| Video Output (540p; 10 seconds:) | POINTS | 58667 | 10 second |
| Video Output (540p; 10 seconds:) | USD | 0.78 | 10 second |
| Video Output (540p; 10 seconds:) | POINTS | 25667 | 10 second |
| Video Output (720p; 10 seconds:) | USD | 2.00 | 10 second |
| Video Output (720p; 10 seconds:) | POINTS | 66000 | 10 second |
| Video Output (720p; 10 seconds:) | USD | 1.00 | 10 second |
| Video Output (720p; 10 seconds:) | POINTS | 33000 | 10 second |

**Last Checked:** 2026-10-05T02:11:09.367447+00:00


## Bot Information

**Creator:** empiriolabsai

**Description:** PixVerse v5.6 is capable of creating high-quality videos from text prompts alone or by animating uploaded images (1 or 2 frames). It supports resolutions up to 1080p, multiple aspect ratios, durations of 5–10 seconds, optional synchronized audio, and the ability to control style presets, thinking mode, negative prompts, and seed-based reproducibility.

Parameter controls available:
1. Basic
- Default: text-to-video (no images needed)
- If animating from image(s): attach 1 image (first frame) or 2 images (first + last frame)
- Resolution \[360p | 540p | 720p | 1080p\]` (default: 1080p)
- Aspect ratio \[16:9 | 4:3 | 1:1 | 3:4 | 9:16\]` (default: 16:9) (ignored for image input)
- Audio \[true | false\]` generate synchronized audio (default: true)

2. Timing and Randomness
- Duration \[5 | 8 | 10\]` seconds (default: 5; 10s not available at 1080p)
- Seed \[1-9223372036854775807\]` for reproducible results (omit for random)

3. Advanced
- Style \[none | anime | 3d_animation | clay | comic | cyberpunk\]` visual style preset (default: none)
- Thinking \[auto | enabled | disabled\]` enhanced reasoning during generation (default: auto)
- Negative prompt "blurry, low quality, distorted"` content to exclude (max 2048 chars)

Input Limits & Requirements:
- Prompt length: 2,048 characters max (both positive and negative prompt)
- Image inputs: JPEG, PNG, WEBP, or HEIC only. Max 20MB per file. Images below 300x300 are automatically upscaled; images above 4000x4000 are automatically downscaled.


## Architecture

**Input Modalities:** text

**Output Modalities:** video

**Modality:** text->video


## Technical Details

**Model ID:** `pixverse-v5.6`

**Object Type:** model

**Created:** 1771637794517

**Owned By:** EmpirioLabs AI

**Root:** pixverse-v5.6

**API Last Updated:** 2026-10-05 01:48:43.415919
