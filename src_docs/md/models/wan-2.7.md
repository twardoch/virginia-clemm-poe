# [wan-2.7](https://poe.com/wan-2.7){ .md-button .md-button--primary }

## Pricing

### Website Pricing

| Type | Cost |
|------|------|
| 720P | $0.10/sec · 3,333 pts/sec |
| 1080P | $0.150/sec · 5,000 pts/sec |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| 720P | USD | 0.10 | 1 second |
| 720P | POINTS | 3333 | 1 second |
| 1080P | USD | 0.150 | 1 second |
| 1080P | POINTS | 5000 | 1 second |

**Last Checked:** 2026-10-05T02:11:10.560779+00:00


## Bot Information

**Creator:** empiriolabsai

**Description:** Wan 2.7 is Alibaba's latest multimodal video generation model, capable of creating high-fidelity videos from text, images, video references, or by editing existing videos. It supports four generation modes: Text-to-Video (T2V), Image-to-Video (I2V), Video Edit, and Reference-to-Video (R2V).

Notes:
- This model is served from the Singapore area.
- Upload an image to enable image-to-video, a video for video editing, or images/videos for reference-to-video. The mode is auto-detected from your attachments, or you can choose manually to override.
- Responses may take upwards of 30 minutes to finish generating.
- Shot type is described directly in your prompt (e.g., "Generate a multi-shot video" or use timeline syntax like "Shot 1 \[0-5s\] wide shot of...").

Attachments:
- For T2V: No attachments required. Optionally attach an audio file for custom audio.
- For I2V (First Frame): Attach 1 image as the first frame. Optionally attach an audio file for driving audio.
- For I2V (First + Last Frame): Attach exactly 2 images (first frame and last frame). Optionally attach an audio file for driving audio.
- For I2V (Video Continuation): Attach 1 video (2–10s) as the first clip. Optionally attach 1 image as the target last frame.
- For Video Edit: Attach 1 video (2–10s, ≤100 MB, MP4/MOV) + up to 3 reference images. If your video is shorter than the selected duration, the output will match your video's length instead.
- For R2V: Attach up to 5 references total (images + videos combined). Use `Video1`, `Video2` in your prompt to reference subjects from uploaded videos, and `Image1`, `Image2` for uploaded images. Optionally attach an audio file for voice timbre reference.
- Audio files: For T2V and I2V: 2–30 seconds. For R2V: 1–10 seconds (voice timbre sample). Max 15 MB, .mp3/.wav. Audio is automatically trimmed to the mode's limit if too long.
- Images are automatically resized to fit limits (240–8,000px per side). HEIC/HEIF images are auto-converted. Videos are validated (MP4/MOV, ≤100 MB) and auto-trimmed if exceeding the mode's max duration.

This bot supports optional parameters for additional customization.


## Architecture

**Input Modalities:** text

**Output Modalities:** video

**Modality:** text->video


## Technical Details

**Model ID:** `wan-2.7`

**Object Type:** model

**Created:** 1775194323304

**Owned By:** EmpirioLabs AI

**Root:** wan-2.7

**API Last Updated:** 2026-10-05 01:48:43.415929
