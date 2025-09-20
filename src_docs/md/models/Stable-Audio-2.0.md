# [Stable-Audio-2.0](https://poe.com/Stable-Audio-2.0){ .md-button .md-button--primary }

## Pricing

| Type | Cost |
|------|------|
| Initial Points Cost | 21307+ points |
| Base Cost | 19267 points |
| Per Step Cost | 69 points |

**Last Checked:** 2025-09-20 12:37:00.322217


## Bot Information

**Creator:** @empiriolabsai

**Description:** Stable Audio 2.0 generates audio up to 3 minutes long from text prompts, supporting text-to-audio and audio-to-audio transformations with customizable settings like duration, steps, CFG scale, and more. It is ideal for creative professionals seeking detailed and extended outputs from simple prompts.

Note: Audio-to-audio mode requires a prompt alongside an uploaded audio file for generation.

Parameter controls available:
1. Basic
   - Default: text-to-audio (no `--mode` needed)
   - If transforming uploaded audio: `--mode audio-to-audio`
   - `--output_format wav` (for high quality, otherwise omit for mp3)
2. Timing and Randomness 
   - `--duration [1-190 seconds]` controls how long generated audio is
   - '--random_seed false --seed [0-4294967294]' disables random seed generation
3. Advanced
   - `--cfg_scale [1-25]`: Higher = closer to prompt (recommended 7-15)
   - `--steps [30-100]`: Higher = better quality (recommended 50-80)
4. Transformation control (only for audio-to-audio)
   - `--strength [0-1]`: How much to change/transform (0.3-0.7 typical)

**Extra:** Powered by a server managed by @empiriolabsai. Learn more


## Architecture

**Input Modalities:** text

**Output Modalities:** text

**Modality:** text->text


## Technical Details

**Model ID:** `Stable-Audio-2.0`

**Object Type:** model

**Created:** 1756880177270

**Owned By:** poe

**Root:** Stable-Audio-2.0
