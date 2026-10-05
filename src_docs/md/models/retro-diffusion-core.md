---
this_file: src_docs/md/models/retro-diffusion-core.md
---

# [retro-diffusion-core](https://poe.com/retro-diffusion-core){ .md-button .md-button--primary }

**Tier 5:** From 334 points · per image

[Comparison method and assumptions](../pricing-method.md).

## Pricing

### Website Pricing

| Type | Cost |
|------|------|
| Images | 480x480 <-> 512x512 = 1667 points ($0.051) |
| Animations | 48x48 VFX = 3334 points ($0.10) |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| Images | USD | 0.010 | 1 image |
| Images | POINTS | 334 | 1 image |
| Images | USD | 0.020 | 1 image |
| Images | POINTS | 667 | 1 image |
| Images | USD | 0.030 | 1 image |
| Images | POINTS | 1000 | 1 image |
| Images | USD | 0.040 | 1 image |
| Images | POINTS | 1334 | 1 image |
| Images | USD | 0.051 | 1 image |
| Images | POINTS | 1667 | 1 image |
| Animations | USD | 0.10 | 1 animations |
| Animations | POINTS | 3334 | 1 animations |
| Animations | USD | 0.10 | 1 animations |
| Animations | POINTS | 3334 | 1 animations |

**Last Checked:** 2026-10-05T02:12:13.230636+00:00


## Bot Information

**Creator:** retrodiffusion

**Description:** Generate true game ready pixel art in seconds at any resolution between 16x16 and 512x512 across the various styles. Create 48x48 walking animations of sprites using the "animation_four_angle_walking" style! First 50 basic image requests worth of points free! Check out more settings below 👇


Example message: "A cute corgi wearing sunglasses and a party hat"

Settings:
- Set AR: Image size in pixels, larger images cost more. Or aspect ratio like 16:9
- Set style: The name of the style you want to use. Available styles: rd_fast__anime, rd_fast__retro, rd_fast__simple, rd_fast__detailed, rd_fast__game_asset, rd_fast__portrait, rd_fast__texture, rd_fast__ui, rd_fast__item_sheet, rd_fast__mc_texture, rd_fast__mc_item, rd_fast__character_turnaround, rd_fast__1_bit, animation__four_angle_walking, rd_plus__default, rd_plus__retro, rd_plus__watercolor, rd_plus__textured, rd_plus__cartoon, rd_plus__ui_element, rd_plus__item_sheet, rd_plus__character_turnaround, rd_plus__isometric, rd_plus__isometric_asset, rd_plus__topdown_map, rd_plus__top_down_asset
- Seed. Random number, keep the same for consistent generations
- Tile. Creates seamless edges on applicable images
- Tile X. Seamless horizontally only
- Tile Y. Seamless vertically only
- Native. Returns pixel art at native resolution, without upscaling
- Remove background. Automatically remove the background
- Strength. Controls how strong the image generation is. 0.0 for small changes, 1.0 for big changes

Additional notes: All styles have a size range of 48x48 -> 512x512, except for the "mc" styles, which have a size range of 16x16 -> 128x128, and the "animation_four_angle_walking" style, which will only create 48x48 animations.


## Architecture

**Input Modalities:** text

**Output Modalities:** image

**Modality:** text->image


## Technical Details

**Model ID:** `retro-diffusion-core`

**Object Type:** model

**Created:** 1742484693553

**Owned By:** Retro Diffusion

**Root:** retro-diffusion-core

**API Last Updated:** 2026-10-05 01:48:43.417132
