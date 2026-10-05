# [kling-3.0-turbo](https://poe.com/kling-3.0-turbo){ .md-button .md-button--primary }

## Bot Information

**Creator:** @empiriolabsai

**Description:** Kling 3.0 Turbo is a fast video generation model that produces high-quality videos with synchronized native audio, at 720p or 1080p resolution. It supports Text-to-Video and Image-to-Video, with multi-shot prompting for up to 6 sequential scenes in a single clip.

Multi-Shot Mode
- Generate up to 6 sequential shots in one video by formatting the prompt as `shot 1, <seconds>, <description>; shot 2, <seconds>, <description>;` — separate shots with a semicolon
- n: shot sequence number (1 to 6 shots)
- m: shot duration; each shot is at least 1 second, and the sum of shot durations equals the total video duration
- words: the prompt for that shot, up to 512 characters
- Per-shot timing is treated as guidance, so cuts may not land on the exact frame
- Text-to-Video only

Prompting
- There is no separate negative prompt. To steer away from unwanted elements, describe them directly in your prompt, for example: a calm forest at dawn, avoid blurry motion, no on-screen text

Input Limits & Requirements
- Prompt length: up to 3,072 characters (2,500 recommended). Positive and negative descriptions can both go in the prompt
- Resolution: 720p or 1080p. Duration: 3 to 15 seconds
- Aspect ratio: 16:9, 9:16, or 1:1 for Text-to-Video; Image-to-Video follows the source image
- Image inputs (Image-to-Video): JPEG or PNG only, up to 50MB. Width and height must each be at least 300px, and the aspect ratio must fall within 1:2.5 to 2.5:1
- Native audio is generated automatically

This bot supports optional parameters for additional customization.


## Architecture

**Input Modalities:** text

**Output Modalities:** text

**Modality:** text->text


## Technical Details

**Model ID:** `kling-3.0-turbo`

**Object Type:** model

**Created:** 1781802100470

**Owned By:** EmpirioLabs AI

**Root:** kling-3.0-turbo

**API Last Updated:** 2026-10-05 01:48:43.418228
