# [vidu](https://poe.com/vidu){ .md-button .md-button--primary }

## Bot Information

**Creator:** @fal

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

**Output Modalities:** video

**Modality:** text,image->video


## Technical Details

**Model ID:** `vidu`

**Object Type:** model

**Created:** 1756292711841

**Owned By:** fal

**Root:** vidu

**API Last Updated:** 2026-10-05 01:48:43.417243
