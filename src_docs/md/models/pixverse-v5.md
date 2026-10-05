# [pixverse-v5](https://poe.com/pixverse-v5){ .md-button .md-button--primary }

## Pricing

### Website Pricing

| Type | Cost |
|------|------|
| 360P | 8s · 15334 ($0.46) |
| 540P | 8s · 15334 ($0.46) |
| 720P | 8s · 20445 ($0.62) |
| 1080P | 5s · 20445 ($0.62) |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| 360p | USD | 0.23 | 1 360p |
| 360p | USD | 0.46 | 1 360p |
| 540p | USD | 0.23 | 1 540p |
| 540p | USD | 0.46 | 1 540p |
| 720p | USD | 0.31 | 1 720p |
| 720p | USD | 0.62 | 1 720p |
| 1080p | USD | 0.62 | 1 1080p |

**Last Checked:** 2026-10-05T02:12:23.371630+00:00


## Bot Information

**Creator:** empiriolabsai

**Description:** Pixverse v5 offers advanced creative tools with three main features: 
1. Text-to-Video, which transforms written prompts into cinematic, high-detail video clips with fluid motion and accurate visual interpretation;
2. Image-to-Video, which animates static images into dynamic short videos with lifelike motion and smooth transitions; and 
3. Transition, which generates seamless morphs between frames or scenes to create unified, professional-quality visual flow.

Parameter Controls and Usage:
1. Video Generation (Main Control Section)
  - Set Video Resolution. Select from 360p , 540p, 720p, 1080p. This is set to 540p by default.
  - Set Duration. Select from (5 seconds or 8 seconds) to specify video length in seconds. Set to 5 seconds as default. Note: 8s not supported for 1080p.
  - Set aspect ratio. Select from (16:9, 4:3, 1:1, 3:4, 9:16). It is set to 16:9 aspect ratio as default.
  - Negative prompt. Type things to avoid in generated images
  - Seed. Random seed number for reproducible generation with fixed seed (e.g. 12345)

2. Generation Modes (Determined by attachments)
- Text-to-Video: Provide a prompt with 0 image attachments.
- Image-to-Video: Provide 1 image attachment.
- Transition: Provide 2 image attachments (first is start frame, second is end frame).

3. Limitations
- The combination of resolution `1080p` and duration `8 seconds` is not supported.
- Only 0, 1, or 2 image attachments are supported.
- Attachments must be images (PNG/JPEG/WEBP/TIFF/BMP/HEIC/GIF).


## Architecture

**Input Modalities:** text

**Output Modalities:** video

**Modality:** text->video


## Technical Details

**Model ID:** `pixverse-v5`

**Object Type:** model

**Created:** 1760645525570

**Owned By:** EmpirioLabs AI

**Root:** pixverse-v5

**API Last Updated:** 2026-10-05 01:48:43.417207
