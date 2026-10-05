# [gpt-image-1-mini](https://poe.com/gpt-image-1-mini){ .md-button .md-button--primary }

## Pricing

### Website Pricing

| Type | Cost |
|------|------|
| Input (Text) | $1.8 /1M tokens · 60 points/1k tokens |
| Input (Images) | $2.25 /1M tokens · 75 points/1k tokens |
| High Fidelity Editing | $0.012 · 400 points |
| Low | 167 points ($0.005) · 200 points ($0.006) · 200 points ($0.006) |
| Medium | 367 points ($0.011) · 500 points ($0.015) · 500 points ($0.015) |
| High | 1200 points ($0.036) · 1734 points ($0.052) · 1734 points ($0.052) |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| Input (text) | USD | 1.8 | 1000000 tokens |
| Input (text) | POINTS | 60 | 1000 tokens |
| Input (images) | USD | 2.25 | 1000000 tokens |
| Input (images) | POINTS | 75 | 1000 tokens |
| High fidelity editing | USD | 0.012 | 1 high fidelity editing |
| High fidelity editing | POINTS | 400 | 1 high fidelity editing |
| Image Output (low; 1:1 (1024x1024)) | USD | 0.005 | 1 image |
| Image Output (low; 1:1 (1024x1024)) | POINTS | 167 | 1 image |
| Image Output (low; 3:2 (1536x1024)) | USD | 0.006 | 1 image |
| Image Output (low; 3:2 (1536x1024)) | POINTS | 200 | 1 image |
| Image Output (low; 2:3 (1024x1536)) | USD | 0.006 | 1 image |
| Image Output (low; 2:3 (1024x1536)) | POINTS | 200 | 1 image |
| Image Output (medium; 1:1 (1024x1024)) | USD | 0.011 | 1 image |
| Image Output (medium; 1:1 (1024x1024)) | POINTS | 367 | 1 image |
| Image Output (medium; 3:2 (1536x1024)) | USD | 0.015 | 1 image |
| Image Output (medium; 3:2 (1536x1024)) | POINTS | 500 | 1 image |
| Image Output (medium; 2:3 (1024x1536)) | USD | 0.015 | 1 image |
| Image Output (medium; 2:3 (1024x1536)) | POINTS | 500 | 1 image |
| Image Output (high; 1:1 (1024x1024)) | USD | 0.036 | 1 image |
| Image Output (high; 1:1 (1024x1024)) | POINTS | 1200 | 1 image |
| Image Output (high; 3:2 (1536x1024)) | USD | 0.052 | 1 image |
| Image Output (high; 3:2 (1536x1024)) | POINTS | 1734 | 1 image |
| Image Output (high; 2:3 (1024x1536)) | USD | 0.052 | 1 image |
| Image Output (high; 2:3 (1024x1536)) | POINTS | 1734 | 1 image |

**Last Checked:** 2026-10-05T02:12:16.506938+00:00


## Bot Information

**Creator:** openai

**Description:** OpenAI's model that powers image generation in ChatGPT, offering exceptional prompt adherence, level of detail, and quality. It supports editing, restyling, and combining images attached to the latest user query. 

Optional parameters:
- Aspect ratio of the output image (options: 1:1, 3:2, 2:3). 
- Quality. Image resolution (options: high, medium, low).
- Mask. Indicates that the last attached image is a mask for in-painting (editing specific regions). The mask must match the dimensions of the base image, with transparent (zero-alpha) areas showing which parts to edit.


## Architecture

**Input Modalities:** text, image

**Output Modalities:** image

**Modality:** text,image->image


## Technical Details

**Model ID:** `gpt-image-1-mini`

**Object Type:** model

**Created:** 1756235580926

**Owned By:** OpenAI

**Root:** gpt-image-1-mini

**API Last Updated:** 2026-10-05 01:48:43.417143
