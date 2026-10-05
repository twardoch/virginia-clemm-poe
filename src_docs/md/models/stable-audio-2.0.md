---
this_file: src_docs/md/models/stable-audio-2.0.md
---

# [stable-audio-2.0](https://poe.com/stable-audio-2.0){ .md-button .md-button--primary }

**Tier 8:** From 69 points · rate: Per Step Cost

[Comparison method and assumptions](../pricing-method.md).

## Pricing

### Website Pricing

| Type | Cost |
|------|------|
| Base Cost | 19267 ($0.58) points |
| Per Step Cost | 69 ($0.0021) points |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| Base Cost | USD | 0.58 | 1 base cost |
| Base Cost | POINTS | 19267 | 1 base cost |
| Per Step Cost | USD | 0.0021 | 1 step cost |
| Per Step Cost | POINTS | 69 | 1 step cost |

**Last Checked:** 2026-10-05T02:11:59.907516+00:00


## Bot Information

**Creator:** empiriolabsai

**Description:** Stable Audio 2.0 generates audio up to 3 minutes long from text prompts, supporting text-to-audio and audio-to-audio transformations with customizable settings like duration, steps, CFG scale, and more. It is ideal for creative professionals seeking detailed and extended outputs from simple prompts.

Note: Audio-to-audio mode requires a prompt alongside an uploaded audio file for generation.

Parameter controls available:
1. Basic
- Generation Mode: Text to Audio, Audio to Audio (Transform)
- Output format: WAV (high quality), MP3 (Compressed)

2. Timing and Randomness
- Duration \[1-190 seconds\] controls how long generated audio is
- Seed \[0-4294967294\]' disables random seed generation. Use random seed must be toggled off to set.

3. Advanced
- Cfg scale \[1-25\]: Higher = closer to prompt (recommended 7-15)
- Steps \[4-8\]`: Higher = better quality (recommended 6-8)

4. Transformation control (only for audio-to-audio)
- Strength \[0-1\]`: How much to change/transform (0.3-0.7 typical)


## Architecture

**Input Modalities:** text, audio

**Output Modalities:** audio

**Modality:** text,audio->audio


## Technical Details

**Model ID:** `stable-audio-2.0`

**Object Type:** model

**Created:** 1756880177270

**Owned By:** EmpirioLabs AI

**Root:** stable-audio-2.0

**API Last Updated:** 2026-10-05 01:48:43.417003
