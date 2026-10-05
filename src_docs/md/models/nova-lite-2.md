---
this_file: src_docs/md/models/nova-lite-2.md
---

# [nova-lite-2](https://poe.com/nova-lite-2){ .md-button .md-button--primary }

**Tier 3:** 59.5 points · 1,000 tokens (500 input + 500 output)

[Comparison method and assumptions](../pricing-method.md).

## Pricing

### API Pricing (USD)

| Type | Cost |
|------|------|
| Prompt | $3.838E-7/token |
| Completion | $0.0000031919/token |

### Website Pricing

| Type | Cost |
|------|------|
| Input (Text) | $0.38/1M tokens · 13 points/1k tokens |
| Output (Text) | $3.19/1M tokens · 106 points/1k tokens |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| Input (text) | USD | 0.38 | 1000000 tokens |
| Input (text) | POINTS | 13 | 1000 tokens |
| Output (text) | USD | 3.19 | 1000000 tokens |
| Output (text) | POINTS | 106 | 1000 tokens |

**Last Checked:** 2026-10-05T02:11:30.395162+00:00


## Bot Information

**Creator:** empiriolabsai

**Description:** Amazon Nova 2 Lite is a fast, cost-effective multimodal reasoning model from Amazon that can process text, images, documents, and video, designed for everyday workloads like chatbots, document processing, and business automation. It offers a 1 million token context window, enabling very large, complex inputs in a single request, including long documents and extended video clips (~90 minutes).

Notes: 
- Video file uploads are limited to ~1GB. Also note that reasoning traces are not exposed from AWS.
- Supported file types: JPEG, PNG, GIF, WEBP, PDF, DOCX, TXT, MP4, MOV, MKV, WebM, FLV, MPEG, MPG, WMV, 3GP

Parameter controls available:
- Enable Extended thinking. Enable step-by-step reasoning (default: on).
- Set reasoning effort: Select from  low (faster), medium (balanced) , high (deep analysis). Default: medium (balanced)


## Architecture

**Input Modalities:** text, image, video

**Output Modalities:** text

**Modality:** text,image,video->text


## Technical Details

**Model ID:** `nova-lite-2`

**Object Type:** model

**Created:** 1764827272207

**Owned By:** EmpirioLabs AI

**Root:** nova-lite-2

**API Last Updated:** 2026-10-05 01:48:43.416279
