---
this_file: src_docs/md/models/seedance-1.0-pro-fast.md
---

# [seedance-1.0-pro-fast](https://poe.com/seedance-1.0-pro-fast){ .md-button .md-button--primary }

**Tier 7:** ≈ 7,200.144 points · per 10 seconds video (assumed 720p, 24 fps)

[Comparison method and assumptions](../pricing-method.md).

## Pricing

### Website Pricing

| Type | Cost |
|------|------|
| Video Output | 33334 points ($1.01) / million video tokens |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| Video Output | USD | 1.01 | 1000000 tokens |
| Video Output | POINTS | 33334 | 1000000 tokens |

**Last Checked:** 2026-10-05T02:12:29.621453+00:00


## Bot Information

**Creator:** Bytedance

**Description:** Seedance Pro Fast is a faster version of Seedance 1.0 Pro that balances speed, quality and cost. Seedance is a video generation model with text-to-video and image-to-video capabilities. It achieves breakthroughs in semantic understanding and prompt following.

Optional prompts:
Set the aspect ratio (available values: `21:9`, `16:9`, `4:3`, `1:1`, `3:4`, `9:16`). Set to `16:9` as default.
Set resolution (one of `480p`,`720p`,`1080p` to set the video resolution. Set to `1080p` as default.
Set video duration (3s to 12s). Set to `5s` as default.

Notes:
Number of video tokens calculated for pricing is approximately: `height * width * fps * duration / 1024).
File attachment accepted: jpeg, png, webp


## Architecture

**Input Modalities:** text, image

**Output Modalities:** video

**Modality:** text,image->video


## Technical Details

**Model ID:** `seedance-1.0-pro-fast`

**Object Type:** model

**Created:** 1761334162620

**Owned By:** Bytedance

**Root:** seedance-1.0-pro-fast

**API Last Updated:** 2026-10-05 01:48:43.417247
