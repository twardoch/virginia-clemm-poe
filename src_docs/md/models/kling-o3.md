# [kling-o3](https://poe.com/kling-o3){ .md-button .md-button--primary }

## Pricing

### Website Pricing

| Type | Cost |
|------|------|
| Text / Image | 17500 ($0.53) /s |
| Text / Image + Sound | 17500 ($0.53) /s |
| Video Input (Edit / Ref) | 11200 ($0.34) /s |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| Text / Image | USD | 0.17 | 1 second |
| Text / Image + Sound | USD | 0.23 | 1 second |
| Video Input (Edit / Ref) | USD | 0.25 | 1 second |
| Text / Image | USD | 0.23 | 1 second |
| Text / Image + Sound | USD | 0.28 | 1 second |
| Video Input (Edit / Ref) | USD | 0.34 | 1 second |
| Text / Image | USD | 0.53 | 1 second |
| Text / Image + Sound | USD | 0.53 | 1 second |

**Last Checked:** 2026-10-05T02:11:13.391087+00:00


## Bot Information

**Creator:** empiriolabsai

**Description:** Kling O3 is a versatile AI video generation model capable of creating high-quality videos in Standard or Pro modes, with resolution varying by aspect ratio. It supports multiple workflows including Text-to-Video, Image-to-Video, Reference-to-Video, and Video Editing, with advanced features like native sound generation and multi-scene transitions.

Multi-Scene Mode
- Separate scenes with `|` in your prompt — automatically detected, no toggle needed (max 6 scenes)
- Not compatible with video input workflows (video edit, reference with video)
- Optional per-scene durations: `5s: Scene one | 3s: Scene two | 7s: Scene three`
- Explicit per-scene durations override the total duration set
- If no durations specified, the slider duration is distributed evenly across scenes
- Per-scene duration may sometimes not be exact as the model treats them as guidance, not exact frame cuts

Input Limits & Requirements
- Prompt length: 3 characters minimum, 2,500 characters maximum
- Image inputs: JPEG, PNG, or WEBP only. Max 10MB per file. Images below 300x300 are automatically upscaled; images outside the 1:2.5-2.5:1 aspect ratio range are automatically center-cropped to fit
- Video inputs: MP4, MOV, or WEBM only. Videos longer than 10 seconds are automatically trimmed; videos outside the 720-2160px resolution range are automatically resized. Minimum 3 seconds (cannot be extended)
- Video workflow duration: When a video input is used (Video Edit, Reference with video), output duration is automatically capped at 10 seconds
- Image-to-Video: Max 2 images (first frame + optional last frame)
- Reference-to-Video: Max 7 reference images (max 4 if a reference video is also included), max 1 reference video
- Video Edit: Exactly 1 video, no images

This bot supports optional parameters for additional customization.


## Architecture

**Input Modalities:** text, image, video

**Output Modalities:** video

**Modality:** text,image,video->video


## Technical Details

**Model ID:** `kling-o3`

**Object Type:** model

**Created:** 1771637573229

**Owned By:** EmpirioLabs AI

**Root:** kling-o3

**API Last Updated:** 2026-10-05 01:48:43.415957
