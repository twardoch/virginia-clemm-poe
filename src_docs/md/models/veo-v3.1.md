# [veo-v3.1](https://poe.com/veo-v3.1){ .md-button .md-button--primary }

## Pricing

### Website Pricing

| Type | Cost |
|------|------|
| Video Output | 6667 points ($0.20) / s |
| Audio + Video Output | 13334 points ($0.40) / s |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| Video Output | USD | 0.20 | 1 second |
| Video Output | POINTS | 6667 | 1 second |
| Audio + Video Output | USD | 0.40 | 1 second |
| Audio + Video Output | POINTS | 13334 | 1 second |

**Last Checked:** 2026-10-05T02:12:26.321814+00:00


## Bot Information

**Creator:** fal

**Description:** Google's Veo-3.1 is an improved version of Veo 3.

Optional parameters:
Set the aspect ratio of the generated image (one of `16:9`, `9:16`).
Set silent to generate a silent video at a lower cost.
Set negative prompt option `blur`, `low resolution`, `poor quality`. (only for T2V).
Set the duration `4s`, `6s`, `8s`, default `8s`. `4s` and `6s` are only supported for text-to-video generation.

Notes:
Pass a single image for image to video tasks. 
Pass two images for a first-frame-to-last-frame video generation task. 
Pass up to 3 images with reference for a reference-to-video task. Reference images will be directly used in the video generation.


## Architecture

**Input Modalities:** text

**Output Modalities:** video

**Modality:** text->video


## Technical Details

**Model ID:** `veo-v3.1`

**Object Type:** model

**Created:** 1760568057558

**Owned By:** fal

**Root:** veo-v3.1

**API Last Updated:** 2026-10-05 01:48:43.417224
