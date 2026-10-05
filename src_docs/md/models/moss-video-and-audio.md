---
this_file: src_docs/md/models/moss-video-and-audio.md
---

# [moss-video-and-audio](https://poe.com/moss-video-and-audio){ .md-button .md-button--primary }

**Tier 7:** From 56,640 points · per 10 seconds video

[Comparison method and assumptions](../pricing-method.md).

## Pricing

### Website Pricing

| Type | Cost |
|------|------|
| 360P | 5664 ($0.17) |
| 720P | 93145 ($2.82) |
| Fast | 2167 ($0.066) |
| Quality | 4334 ($0.13) |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| Video Output (360p) | USD | 0.17 | 1 second |
| Video Output (360p) | POINTS | 5664 | 1 second |
| Video Output (720p) | USD | 2.82 | 1 second |
| Video Output (720p) | POINTS | 93145 | 1 second |
| Fast | USD | 0.066 | 1 fast |
| Fast | POINTS | 2167 | 1 fast |
| Quality | USD | 0.13 | 1 quality |
| Quality | POINTS | 4334 | 1 quality |

**Last Checked:** 2026-10-05T02:11:09.541404+00:00


## Bot Information

**Creator:** empiriolabsai

**Description:** MOSS Video and Audio (MOVA) is an open-source foundation model developed by OpenMOSS that generates synchronized, high-fidelity video and audio in a single end-to-end inference step. Built on a 32-billion parameter Mixture-of-Experts (MoE) architecture, it employs an asymmetric dual-tower design to achieve precise lip-synchronization and eliminate the error accumulation found in traditional cascaded systems. 

This model is hosted by EmpirioLabs.ai and is exclusive to the Poe platform.

Learn more: https://mosi.cn/models/mova

Notes:
- Generations may take upwards of 20 minutes to complete.
- Image-to-Video generations will likely yield superior results.
- Supported image upload file types: .jpg, .jpeg, .png, .webp, .heic, .heif, .bmp, .tiff, .tif, .gif
- Only 1 image attachment is supported (first frame), and video attachments are not supported.

Parameter controls available:
1. Generation
- Resolution `360p` or q720p` (default: 360p)
- Aspect ratio `landscape` or `portrait` or `square` (default: landscape; auto-detected for uploaded images)
- Duration \[2-8\] video length in seconds (default: 4)
- t2v quality 1fast` or `quality` (default: quality; only for text-to-video)

2. Advanced
- Inference steps \[10-50\] more steps = higher quality but slower (default: 25, step: 5)
- CFG scale \[1.0-10.0\] prompt adherence strength, higher = more literal (default: 5.0, step: 0.5)
- Sigma_shift \[1.0-10.0\] noise schedule shift, 360p only (default: 5.0, step: 0.5)
- Seed \[number\] for reproducibility, omit for random
- Negative prompt "your negative prompt" leave blank for optimized default


## Architecture

**Input Modalities:** text

**Output Modalities:** video

**Modality:** text->video


## Technical Details

**Model ID:** `moss-video-and-audio`

**Object Type:** model

**Created:** 1771382022972

**Owned By:** EmpirioLabs AI

**Root:** moss-video-and-audio

**API Last Updated:** 2026-10-05 01:48:43.415922
