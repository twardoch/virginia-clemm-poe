# [qwen3.5-omni-plus](https://poe.com/qwen3.5-omni-plus){ .md-button .md-button--primary }

## Bot Information

**Creator:** @empiriolabsai

**Description:** Qwen3.5-Omni Plus is the flagship variant of Qwen's latest omni-modal model, supporting text, image, audio, and video understanding and interaction. It handles up to 3 hours of audio and 1 hour of video input, with audio input in 90+ languages and speech output in 30+ languages across 55 voice timbres.
This model is served by Alibaba Cloud Int. from Singapore.

Notes:
- Context Window: 256K
- Recommended: instruct the model to avoid markdown formatting in Text + Audio mode

Input limits:
- Images: up to 2,048 files, ≤20 MB each, min 10×10 px, aspect ratio ≤200:1
- Audio: up to 2,048 files, ≤2 GB each, up to 3 hrs
- Video: up to 512 files, ≤2 GB each, up to 1 hr
- Formats — Image: JPG, JPEG, JPE, PNG, WebP, BMP, TIF, TIFF, HEIC, GIF | Audio: AMR, WAV, 3GP, 3GPP, AAC, MP3 | Video: MP4, AVI, MKV, MOV, FLV, WMV
- Audio Input: 92 languages, 21 dialects

Output:
- Modalities: text only, or text + audio (audio-only not available)
- 55 voice timbres (default: Tina)
- Audio output: 29 languages, 7 dialects

This bot supports optional parameters for additional customization.


## Architecture

**Input Modalities:** text, video, audio

**Output Modalities:** text

**Modality:** text,video,audio->text


## Technical Details

**Model ID:** `qwen3.5-omni-plus`

**Object Type:** model

**Created:** 1774889310984

**Owned By:** EmpirioLabs AI

**Root:** qwen3.5-omni-plus

**API Last Updated:** 2026-10-05 01:48:43.415538
