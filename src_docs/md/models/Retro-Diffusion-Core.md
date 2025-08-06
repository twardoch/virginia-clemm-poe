# [Retro-Diffusion-Core](https://poe.com/Retro-Diffusion-Core){ .md-button .md-button--primary }

## Bot Information

**Creator:** @retrodiffusion

**Description:** Generate true game ready pixel art in seconds at any resolution between 16x16 and 512x512 across the various styles. Create 48x48 walking animations of sprites using the "animation_four_angle_walking" style! First 50 basic image requests worth of points free! Check out more settings below 👇


Example message: "A cute corgi wearing sunglasses and a party hat --ar 128:128 --style rd_fast__portrait"

Settings:
--ar <width>:<height> (Image size in pixels, larger images cost more. Or aspect ratio like 16:9)
--style <style_name> (The name of the style you want to use. Available styles: rd_fast__anime, rd_fast__retro, rd_fast__simple, rd_fast__detailed, rd_fast__game_asset, rd_fast__portrait, rd_fast__texture, rd_fast__ui, rd_fast__item_sheet, rd_fast__mc_texture, rd_fast__mc_item, rd_fast__character_turnaround, rd_fast__1_bit, animation__four_angle_walking, rd_plus__default, rd_plus__retro, rd_plus__watercolor, rd_plus__textured, rd_plus__cartoon, rd_plus__ui_element, rd_plus__item_sheet, rd_plus__character_turnaround, rd_plus__isometric, rd_plus__isometric_asset, rd_plus__topdown_map, rd_plus__top_down_asset)
--seed (Random number, keep the same for consistent generations)
--tile (Creates seamless edges on applicable images)
--tilex (Seamless horizontally only)
--tiley (Seamless vertically only)
--native (Returns pixel art at native resolution, without upscaling)
--removebg (Automatically remove the background)
--iw <decimal between 0.0 and 1.0> (Controls how strong the image generation is. 0.0 for small changes, 1.0 for big changes)

Additional notes: All styles have a size range of 48x48 -> 512x512, except for the "mc" styles, which have a size range of 16x16 -> 128x128, and the "animation_four_angle_walking" style, which will only create 48x48 animations.

**Extra:** Powered by a server managed by @retrodiffusion. Learn more


## Architecture

**Input Modalities:** text

**Output Modalities:** image

**Modality:** text->image


## Technical Details

**Model ID:** `Retro-Diffusion-Core`

**Object Type:** model

**Created:** 1742484693553

**Owned By:** poe

**Root:** Retro-Diffusion-Core
