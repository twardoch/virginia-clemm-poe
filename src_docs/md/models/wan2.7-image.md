# [wan2.7-image](https://poe.com/wan2.7-image){ .md-button .md-button--primary }

## Bot Information

**Creator:** @empiriolabsai

**Description:** Wan2.7 Image is Alibaba's Wan 2.7 series image generation and editing model, supporting text-to-image, image editing, interactive editing with bounding boxes, and cohesive image set generation from a single prompt. The Pro variant supports up to 4K output resolution with enhanced quality, while the Standard variant offers faster generation at lower cost.

Notes:
- This model is served from the Singapore region.
- Upload 1-9 images to enable image editing mode. Without images, the bot operates in text-to-image generation mode.
- Responses may take 10-60 seconds depending on resolution, number of images, model variant, and whether thinking mode is enabled.
- Prompt has a max of 5,000 characters.

Attachments (Image Editing Mode):
- Attach 1-9 images (JPEG, PNG, BMP, WEBP) with a text instruction to edit them.
- Input image resolution must be between 240-8000 pixels per side with an aspect ratio between 1:8 and 8:1.
- Maximum file size per image: 20 MB.
- Multi-image editing: Reference images by order (e.g. "Spray the graffiti from image 2 onto the car in image 1").
- Interactive editing: Use bounding boxes to specify regions on images for targeted edits (e.g. "Place the object from image 1 in the selected area of image 2").
- Supported operations: style transfer, object placement, graffiti/texture application, scene blending, background replacement, multi-reference composition, and more.

This bot supports optional parameters for additional customization.


## Architecture

**Input Modalities:** text

**Output Modalities:** image

**Modality:** text->image


## Technical Details

**Model ID:** `wan2.7-image`

**Object Type:** model

**Created:** 1775077688892

**Owned By:** EmpirioLabs AI

**Root:** wan2.7-image

**API Last Updated:** 2026-10-05 01:48:43.415912
