# [happyhorse-1.0-el](https://poe.com/happyhorse-1.0-el){ .md-button .md-button--primary }

## Pricing

### Website Pricing

| Type | Cost |
|------|------|
| 720P | $0.14/sec · 4,667 pts/sec |
| 1080P | $0.24/sec · 8,000 pts/sec |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| 720P | USD | 0.14 | 1 second |
| 720P | POINTS | 4667 | 1 second |
| 1080P | USD | 0.24 | 1 second |
| 1080P | POINTS | 8000 | 1 second |

**Last Checked:** 2026-10-05T02:13:08.039420+00:00


## Bot Information

**Creator:** empiriolabsai

**Description:** HappyHorse 1.0 is a video generation model, capable of creating high-fidelity, motion-smooth videos from text, images, or by editing existing videos. It supports four generation modes: Text-to-Video (T2V), Image-to-Video (I2V), Reference-to-Video (R2V), and Video Edit.

Notes:
- This model is served from the Singapore region.
- Upload one image to enable image-to-video, multiple images for reference-to-video, or a video for video editing. The mode is auto-detected from your attachments, or you can choose manually to override.
- Generation typically takes 1–5 minutes per video, but may take longer.
- Shot type and camera moves are described directly in your prompt (e.g., "side medium shot opens, then cuts to a low-angle shot, then pushes into a facial close-up").

Attachments:
- For T2V: No attachments required. Just describe the video you want.
- For I2V: Attach exactly 1 image as the first frame. The output's aspect ratio automatically follows your input image (the Aspect Ratio control is ignored). The prompt is optional but recommended.
- For R2V: Attach 1–9 reference images. Use `character1`, `character2`, … in your prompt to reference each image in the order they were attached (e.g., "A woman in a red qipao character1 holding a folding fan character2…").
- For Video Edit: Attach 1 video (3–15s, ≤100 MB, MP4/MOV) plus 0–5 reference images. Output duration follows the input video's length (capped at 15s); audio can be kept from the source via the Audio Setting control.
- Audio files: Not supported. HappyHorse 1.0 does not accept audio attachments, please remove any audio file before submitting.
- Images are automatically validated and resized to fit limits (300–8,000px per side; R2V references should be at least 400px on the short side, 720P+ recommended). HEIC/HEIF images are auto-converted to JPEG.
- Videos are validated (MP4/MOV, ≤100 MB, 3–15s) and auto-transcoded/trimmed if needed.

This bot supports optional parameters for additional customization.


## Architecture

**Input Modalities:** text

**Output Modalities:** text

**Modality:** text->text


## Technical Details

**Model ID:** `happyhorse-1.0-el`

**Object Type:** model

**Created:** 1777302726008

**Owned By:** EmpirioLabs AI

**Root:** happyhorse-1.0-el

**API Last Updated:** 2026-10-05 01:48:43.417991
