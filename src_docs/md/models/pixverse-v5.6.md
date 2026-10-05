# [pixverse-v5.6](https://poe.com/pixverse-v5.6){ .md-button .md-button--primary }

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
| 360p | USD | 0.81 | 1 360p |
| 360p | USD | 0.35 | 1 360p |
| 540p | USD | 0.81 | 1 540p |
| 540p | USD | 0.35 | 1 540p |
| 720p | USD | 0.91 | 1 720p |
| 720p | USD | 0.45 | 1 720p |
| 1080p | USD | 1.52 | 1 1080p |
| 1080p | USD | 0.76 | 1 1080p |
| 360p | USD | 1.62 | 1 360p |
| 360p | USD | 0.71 | 1 360p |
| 540p | USD | 1.62 | 1 540p |
| 540p | USD | 0.71 | 1 540p |
| 720p | USD | 1.82 | 1 720p |
| 720p | USD | 0.91 | 1 720p |
| 1080p | USD | 3.03 | 1 1080p |
| 1080p | USD | 1.52 | 1 1080p |
| 360p | USD | 1.78 | 1 360p |
| 360p | USD | 0.78 | 1 360p |
| 540p | USD | 1.78 | 1 540p |
| 540p | USD | 0.78 | 1 540p |
| 720p | USD | 2.00 | 1 720p |
| 720p | USD | 1.00 | 1 720p |

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
