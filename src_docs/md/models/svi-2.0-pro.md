# [svi-2.0-pro](https://poe.com/svi-2.0-pro){ .md-button .md-button--primary }

## Bot Information

**Creator:** @empiriolabsai

**Description:** Stable Video Infinity 2.0 Pro, powered by WAN 2.2, generates seamlessly extending, theoretically infinite-length videos from still images while maintaining consistent character IDs. It uses advanced temporal coherence and generative scene expansion to maintain visual consistency, allowing endless, smooth motion and evolving visuals without looping or abrupt transitions.

This model is hosted by EmpirioLabs.ai and is exclusive to the Poe platform.

Learn more: https://stable-video-infinity.github.io/homepage/

Notes: 
- Generations may take upwards of 45 minutes depending on the selected length.
- If you are experiencing issues with slow motion, try adjusting the prompt to describe more consecutive motion per segment (ex. A knight stands in the rain, water dripping from his helmet as he clenches his fist, looks up toward the castle gates, takes a steadying breath, then turns and marches forward.).
- Image-to-Video generations will likely yield superior results.
- Supported image upload file types: .jpg, .jpeg, .png, .webp, .heic, .heif, .bmp, .tiff, .tif

Parameter controls available:
1. Video Settings
- Resolution. \[832x480, 480x832, 720x1280, 1280x720\]: Controls output dimensions (Default: 832x480)
- Duration \[18-121.5\]: Estimated video length in seconds (Step 4.5)
  - For 480p: Max 121.5s
  - For 720p: Max 40.5s

2. Advanced
- Cfg \[1.0-2.0\]: Prompt adherence strength (Default: 1.0)
- Negative prompt \[text\]`: Standard negative prompt included by default (e.g. "vibrant tone, overexposed...")

3. Text-to-Video Settings
- t2v quality \[fast or quality\]: Generation mode for text-to-video (Default: quality)


## Architecture

**Input Modalities:** text

**Output Modalities:** video

**Modality:** text->video


## Technical Details

**Model ID:** `svi-2.0-pro`

**Object Type:** model

**Created:** 1767577823164

**Owned By:** EmpirioLabs AI

**Root:** svi-2.0-pro

**API Last Updated:** 2026-10-05 01:48:43.417065
