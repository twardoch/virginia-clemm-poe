---
this_file: src_docs/md/models/Image-Photo.md
---

# [Image-Photo](https://poe.com/Image-Photo){ .md-button .md-button--primary }

**Tier 8:** From 1 points · per message

[Comparison method and assumptions](../pricing-method.md).

## Pricing

### Website Pricing

| Type | Cost |
|------|------|
| Message Cost | Script bots cost 1 point per message, plus the rates of any other bots it calls. |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| Message cost | POINTS | From 1 | 1 message |

**Last Checked:** 2026-10-05T02:09:11.457228+00:00


## Bot Information

**Creator:** OpenSourceLab

**Description:** Hyperrealistic photo and image generator for professional use. Adjust numerous aspects, such as colors, composition, lighting, textures or specific details like object positioning, perspective and depth.  It can also transform images (image to image), which will consume additional points.

How to use:
1. Upload an image (photo, render, screenshot, artwork) or send an image prompt.
2. Add transformation flags to your message and combine multiple flags for complex edits (optional).
3. Reupload results to continue refining or stacking transformations.

Tips for best results:
- Combine multiple flags instead of repeating uploads.
- Use small increments for brightness, contrast, and saturation.
- Stack geometry changes before color or effects.
- Reupload outputs to iteratively refine details.
- For advanced transformations, be explicit and precise.

Geometric flags:
`--rotate 90`
`--mirror`
`--flip`
`--resize 800x600`
`--crop 10,10,500,500`

Color flags:
`--brightness 20`
`--contrast 30`
`--saturation 50`
`--grayscale`
`--sepia`
`--invert`
`--hue 180`
`--colorize blue`

Effect flags:
`--blur 5`
`--sharpen 3`
`--edge`
`--emboss`
`--pixelate 10`
`--filter vintage`

Examples:
- YouTube Thumbnail: `--resize 1280x720 --contrast 25 --sharpen 4`
- Instagram Post: `--resize 1080x1080 --saturation 30`
- Instagram Story: `--resize 1080x1920 --brightness 10`
- Website Banner `--resize 1920x600 --contrast 20`
- Facebook/Instagram Ad: `--resize 1080x1080` `--brightness 12` `--contrast 28` `--saturation 22` `--sharpen 4`
- E-Commerce Ad: `--brightness 8` `--contrast 18` `--saturation 12` `--filter clean`
- Cinematic Brand ad: `--contrast 25` `--saturation -10` `--colorize teal` `--filter cinematic`


## Architecture

**Input Modalities:** Unknown

**Output Modalities:** Unknown

**Modality:** unknown


## Technical Details

**Model ID:** `Image-Photo`

**Object Type:** bot

**Created:** Unknown

**Owned By:** OpenSourceLab

**Root:** Image-Photo

**API Last Updated:** Not listed in API
