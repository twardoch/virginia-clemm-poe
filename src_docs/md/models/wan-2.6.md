---
this_file: src_docs/md/models/wan-2.6.md
---

# [wan-2.6](https://poe.com/wan-2.6){ .md-button .md-button--primary }

**Tier 7:** From 7,500 points · per 10 seconds video

[Comparison method and assumptions](../pricing-method.md).

## Pricing

### Website Pricing

| Type | Cost |
|------|------|
| 720P | Without · $0.0225 /sec · 750 pts/sec |
| 1080P | Without · $0.03450 /sec · 1,150 pts/sec |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| 720P | USD | 0.10 | 1 second |
| 720P | USD | 0.09 | 1 second |
| 720P | POINTS | 3000 | 1 second |
| 1080P | USD | 0.15 | 1 second |
| 1080P | USD | 0.138 | 1 second |
| 1080P | POINTS | 4600 | 1 second |
| 720P | USD | 0.050 | 1 second |
| 720P | USD | 0.045 | 1 second |
| 720P | POINTS | 1500 | 1 second |
| 720P | USD | 0.0250 | 1 second |
| 720P | USD | 0.0225 | 1 second |
| 720P | POINTS | 750 | 1 second |
| 1080P | USD | 0.0750 | 1 second |
| 1080P | USD | 0.0690 | 1 second |
| 1080P | POINTS | 2300 | 1 second |
| 1080P | USD | 0.03750 | 1 second |
| 1080P | USD | 0.03450 | 1 second |
| 1080P | POINTS | 1150 | 1 second |

**Last Checked:** 2026-10-05T02:12:19.726982+00:00


## Bot Information

**Creator:** empiriolabsai

**Description:** Wan 2.6 is Alibaba’s multimodal video generation model built for cinematic, multi-shot storytelling—creating high-fidelity videos from text and/or images while keeping characters and style consistent across scenes. It also supports native audio-visual sync (including lip-sync) and can generate or align dialogue/music/SFX with the visuals, enabling “prompt-to-video” results that feel production-ready without heavy post work.

Notes:
- This model is served from the Singapore area. 
- Upload an image to enable image-to-video generations or video(s) for reference-to-video generations. The mode is auto-detected from your attachments, or you can choose manually to override.
- Responses may take upwards of 10 minutes to finish generating. 

Attachments
   - For i2v: Attach an image as the first frame
   - For r2v: Attach up to 5 images + 1-3 reference videos (1-30 seconds each, 100MB max, MP4/MOV) (Use `character1`, `character2`, `character3` in prompt to reference subjects, ex. character1 references the subject in the first uploaded video) (combined max 5). Uploaded audio files are silently ignored in R2V. Instead, audio is extracted from reference videos.
   - For t2v/i2v: Optionally attach an audio file (3-30 seconds, max 15mb, .mp3/.wav) for custom audio
   - Images are automatically resized to fit limits (I2V: 240–8,000px, R2V: 240–8,000px). HEIC/HEIF images are auto-converted. Videos for R2V are validated (MP4/MOV, 1–30s, ≤100 MB) and auto-trimmed if longer than 30 seconds. For R2V, if output duration is set above 10 seconds, it will be automatically capped to 10 seconds.

Multi-Shot Prompting
   - For multi-shot mode, use timeline syntax: `\[Shot #\] \[Timestamp\] \[Action\]`. Example: `\[Shot 1\] \[0-5s\] Wide shot of city skyline. \[Shot 2\] \[5-10s\] Close-up of character walking.` 
   - Ensure timestamps match your selected duration and use transition keywords like "Hard cut" or "Fade in" between shots.

This bot supports optional parameters for additional customization.


## Architecture

**Input Modalities:** text

**Output Modalities:** video

**Modality:** text->video


## Technical Details

**Model ID:** `wan-2.6`

**Object Type:** model

**Created:** 1765907288740

**Owned By:** EmpirioLabs AI

**Root:** wan-2.6

**API Last Updated:** 2026-10-05 01:48:43.417156
