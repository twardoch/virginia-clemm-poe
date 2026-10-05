---
this_file: src_docs/md/models/stable-audio-2.5.md
---

# [stable-audio-2.5](https://poe.com/stable-audio-2.5){ .md-button .md-button--primary }

**Tier 8:** 22,667 points · rate: Generation

[Comparison method and assumptions](../pricing-method.md).

## Pricing

### Website Pricing

| Type | Cost |
|------|------|
| Generation | 22667 ($0.69) points |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| Generation | USD | 0.69 | 1 generation |
| Generation | POINTS | 22667 | 1 generation |

**Last Checked:** 2026-10-05T02:11:59.347033+00:00


## Bot Information

**Creator:** empiriolabsai

**Description:** Stable Audio 2.5 generates high-quality audio up to 3 minutes long from text prompts, supporting text-to-audio, audio-to-audio transformations, and inpainting with customizable settings like duration, steps, CFG scale, and more. It is Ideal for music production, cinematic sound design, and remixing. 

Note: Audio-to-audio and inpaint modes require a prompt alongside an uploaded audio file for generation.

Parameter controls available:
1. Basic
   - Generation Mode: Text to Audio, Audio to Audio (Transform), Audio Inpaint (Edit Segment)
   - Output format: WAV (high quality), MP3 (Compressed)

2. Timing and Randomness 
   - Duration \[1-190 seconds\] controls how long generated audio is
   - Seed \[0-4294967294\]' disables random seed generation. Use random seed must be toggled off to set.

3. Advanced
   - Cfg scale \[1-25\]: Higher = closer to prompt (recommended 7-15)
   - Steps \[4-8\]`: Higher = better quality (recommended 6-8)

4. Transformation control (only for audio-to-audio)
   - Strength \[0-1\]`: How much to change/transform (0.3-0.7 typical)

5. Inpainting control (only for audio-inpaint)
   - Mask start time \[seconds\] start time of the uploaded audio to modify
   - Mask end time \[seconds\] end time of the uploaded audio to modify


## Architecture

**Input Modalities:** text, audio

**Output Modalities:** audio

**Modality:** text,audio->audio


## Technical Details

**Model ID:** `stable-audio-2.5`

**Object Type:** model

**Created:** 1756869275249

**Owned By:** EmpirioLabs AI

**Root:** stable-audio-2.5

**API Last Updated:** 2026-10-05 01:48:43.416999
