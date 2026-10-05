# [seedance-2.5-el](https://poe.com/seedance-2.5-el){ .md-button .md-button--primary }

## Bot Information

**Creator:** @empiriolabsai

**Description:** Seedance 2.5 is ByteDance's next-generation video model. It generates a coherent clip of up to 30 seconds in a single request, draws on up to 50 reference assets at once, and edits or extends video you already have.

Modes (auto-detected)
- Text to video: a prompt on its own.
- Image to video: attach one image for a first frame, or two for a first and last frame.
- Multimodal reference: attach up to 30 images, 10 videos, and 10 audio clips together. Audio works on its own, with no visual input.
- Video edit: attach a clip and say what to change. Add, remove, or replace something in the footage.
- Video extend: attach a clip and ask to continue it.

Addressing references
With several assets attached, point the prompt at a specific one by index: @Image1, @Image2, @Video1, @Audio1. Attachments are numbered in the order you send them, per type.

Input limits
- Images: jpeg, png, webp, bmp, tiff, gif, heic, heif. 300 to 6000 px per side, under 30 MB each.
- Videos: MP4 or MOV, 2 to 30 seconds each and 30 seconds in total, under 200 MB each.
- Audio: WAV or MP3, 2 to 30 seconds each and 30 seconds in total, under 15 MB each.

This bot supports optional parameters for additional customization.


## Architecture

**Input Modalities:** text

**Output Modalities:** text

**Modality:** text->text


## Technical Details

**Model ID:** `seedance-2.5-el`

**Object Type:** model

**Created:** 1786105741004

**Owned By:** EmpirioLabs AI

**Root:** seedance-2.5-el

**API Last Updated:** 2026-10-05 01:48:43.418789
