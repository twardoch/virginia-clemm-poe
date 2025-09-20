# [Stable-Audio-2.5](https://poe.com/Stable-Audio-2.5){ .md-button .md-button--primary }

## Pricing

| Type | Cost |
|------|------|
| Initial Points Cost | 22667 points |
| Generation | 22667 points |

**Last Checked:** 2025-09-20 12:37:08.116585


## Bot Information

**Creator:** @empiriolabsai

**Description:** Stable Audio 2.5 generates high-quality audio up to 3 minutes long from text prompts, supporting text-to-audio, audio-to-audio transformations, and inpainting with customizable settings like duration, steps, CFG scale, and more. It is Ideal for music production, cinematic sound design, and remixing. 

Note: Audio-to-audio and inpaint modes require a prompt alongside an uploaded audio file for generation.

Parameter controls available:
1. Basic
   - Default: text-to-audio (no `--mode` needed)
   - If transforming uploaded audio: `--mode audio-to-audio`
   - If replacing specific parts: `--mode audio-inpaint`
   - `--output_format wav` (for high quality, otherwise omit for mp3)
2. Timing and Randomness 
   - `--duration [1-190 seconds]` controls how long generated audio is
   - '--random_seed false --seed [0-4294967294]' disables random seed generation
3. Advanced
   - `--cfg_scale [1-25]`: Higher = closer to prompt (recommended 7-15)
   - `--steps [4-8]`: Higher = better quality (recommended 6-8)
4. Transformation control (only for audio-to-audio)
   - `--strength [0-1]`: How much to change/transform (0.3-0.7 typical)
5. Inpainting control (only for audio-inpaint)
   - `--mask_start_time [seconds]` start time of the uploaded audio to modify
   - `--mask_end_time [seconds]` end time of the uploaded audio to modify

**Extra:** Powered by a server managed by @empiriolabsai. Learn more


## Architecture

**Input Modalities:** text

**Output Modalities:** text

**Modality:** text->text


## Technical Details

**Model ID:** `Stable-Audio-2.5`

**Object Type:** model

**Created:** 1756869275249

**Owned By:** poe

**Root:** Stable-Audio-2.5
