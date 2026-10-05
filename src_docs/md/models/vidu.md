---
this_file: src_docs/md/models/vidu.md
---

# [vidu](https://poe.com/vidu){ .md-button .md-button--primary }

**Tier 7:** From ≈ 13,334 points · per 10 seconds video (assumed 5s clip)

[Comparison method and assumptions](../pricing-method.md).

## Pricing

### Website Pricing

| Type | Cost |
|------|------|
| Image To Video Output | 6667 points ($0.20) / video |
| Reference To Video Output | 13334 points ($0.40) / video |
| Start And End Frame To Video Output | 6667 points ($0.20) / video |
| Standard Template To Video Output | 6667 points ($0.20) / video |
| Premium Template To Video Output | 10000 points ($0.30) / video |
| Advanced Template To Video Output | 16667 points ($0.51) / video |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| Image to Video Output | USD | 0.20 | 1 video |
| Image to Video Output | POINTS | 6667 | 1 video |
| Reference to Video Output | USD | 0.40 | 1 video |
| Reference to Video Output | POINTS | 13334 | 1 video |
| Start and End Frame to Video Output | USD | 0.20 | 1 video |
| Start and End Frame to Video Output | POINTS | 6667 | 1 video |
| Standard Template to Video Output | USD | 0.20 | 1 video |
| Standard Template to Video Output | POINTS | 6667 | 1 video |
| Premium Template to Video Output | USD | 0.30 | 1 video |
| Premium Template to Video Output | POINTS | 10000 | 1 video |
| Advanced Template to Video Output | USD | 0.51 | 1 video |
| Advanced Template to Video Output | POINTS | 16667 | 1 video |

**Last Checked:** 2026-10-05T02:12:28.981838+00:00


## Bot Information

**Creator:** fal

**Description:** The Vidu Video Generation Bot creates videos using images and text prompts. You can generate videos in four modes: 
(1) Image-to-Video: send 1 image with a prompt, 
(2) Start-to-End Frame: send 2 images with a prompt for transition videos, 
(3) Reference-to-Video: send up to 3 images with the reference image parameter for guidance, and 
(4) Template-to-Video: use `--template` to apply pre-designed templates (1-3 images required, pricing varies by template). 

Number of images required varies by template: `dynasty_dress` and `shop_frame` accept 1-2 images, `wish_sender` requires exactly 3 images, all other templates accept only 1 image.

The bot supports aspect ratios (16:9, 1:1, 9:16), set movement amplitude, and accepts PNG, JPEG, and WEBP formats. 
Tasks are mutually exclusive (e.g., you cannot combine start-to-end frame and reference-to-video).
Duration is limited to 5 seconds.


## Architecture

**Input Modalities:** text, image

**Output Modalities:** image, video

**Modality:** text+image->image+video


## Technical Details

**Model ID:** `vidu`

**Object Type:** model

**Created:** 1756292711841

**Owned By:** fal

**Root:** vidu

**API Last Updated:** 2026-10-05 01:48:43.417243
