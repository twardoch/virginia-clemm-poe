# [Vidu](https://poe.com/Vidu){ .md-button .md-button--primary }

## Pricing

| Type | Cost |
|------|------|
| Initial Points Cost | Variable points |
| Image To Video Output | 6667 points / video |
| Reference To Video Output | 13334 points / video |
| Start And End Frame To Video Output | 6667 points / video |
| Standard Template To Video Output | 6667 points / video |
| Premium Template To Video Output | 10000 points / video |
| Advanced Template To Video Output | 16667 points / video |

**Last Checked:** 2025-09-20 11:48:02.341982


## Bot Information

**Creator:** @fal

**Description:** The Vidu Video Generation Bot creates videos using images and text prompts. You can generate videos in four modes: 
(1) Image-to-Video: send 1 image with a prompt, 
(2) Start-to-End Frame: send 2 images with a prompt for transition videos, 
(3) Reference-to-Video: send up to 3 images with the `--reference` flag for guidance, and 
(4) Template-to-Video: use `--template` to apply pre-designed templates (1-3 images required, pricing varies by template). 

Number of images required varies by template: `dynasty_dress` and `shop_frame` accept 1-2 images, `wish_sender` requires exactly 3 images, all other templates accept only 1 image.

The bot supports aspect ratios `--aspect` (16:9, 1:1, 9:16), set movement amplitude `--movement-amplitude`, and accepts PNG, JPEG, and WEBP formats. 
Tasks are mutually exclusive (e.g., you cannot combine start-to-end frame and reference-to-video).
Duration is limited to 5 seconds.

**Extra:** Powered by a server managed by @fal. Learn more


## Architecture

**Input Modalities:** text

**Output Modalities:** text

**Modality:** text->text


## Technical Details

**Model ID:** `Vidu`

**Object Type:** model

**Created:** 1756292711841

**Owned By:** poe

**Root:** Vidu
