---
this_file: src_docs/md/pricing-method.md
---

# Comparing prices

The catalogue compares saved public Poe rates. It does not rescrape during a
documentation build. Each model has a point estimate and a pricing tier; original
USD/point observations remain visible on its page. These are reference costs,
not a quote for an arbitrary request.

- Prefer disclosed points per message or per image over a token calculation.
- For text priced by tokens, use **1,000 total tokens**, split 500 input and 500
  output when both rates exist; a single disclosed direction uses 1,000 tokens
  and is labelled partial. Add a disclosed mandatory message fee.
- Character pricing uses **4,000 characters**.
- Image pricing uses one image. Prefer a disclosed 1024×1024 tier; otherwise
  scale megapixels to **1.048576 MP**, respecting explicit integer rounding.
  Output-token estimates use 1,056 tokens for GPT image models (medium quality),
  1,120 for Nano Banana 2 / Gemini 3.1, and a labelled 1,290-token assumption for
  other token-priced image models. Prompt and optional editing input costs are extra.
- Video pricing uses **10 seconds**. Scale seconds/minutes directly. A disclosed
  clip duration is scaled proportionally; an unspecified flat clip assumes **5
  seconds** and is labelled approximate. Seedance output-token prices assume
  1280×720 at 24 fps: width × height × fps × seconds / 1024. Other video-token
  prices use a labelled proxy of 5,792 tokens/second at 720p. Clip limits,
  fixed fees and nonlinear duration pricing can make a real 10-second job differ.
- Dollars are converted only when a point rate for that service is absent.
  Use the median points/dollar ratio from matching positive rates for that bot,
  then the median across the saved catalogue. Match the same service and unit,
  accounting for different denominators. Zero rates do not establish a ratio.
  The table states the current ratio and sample count; each converted cost
  exposes the ratio used. **≈** marks currency or quantity assumptions; **From**
  marks a minimum tier or partial cost. The conversion is an estimate, not a
  subscription exchange rate.

| Tier | Point reference cost |
|---|---|
| 0 | Explicit 0 points **and** $0, without an estimated or partial reference |
| 1 | Positive, up to 9 |
| 2 | Above 9, up to 29 |
| 3 | Above 29, up to 99 |
| 4 | Above 99, up to 299 |
| 5 | Above 299, up to 999 |
| 6 | Above 999, up to 2,999 |
| 7 | Above 2,999 |
| 8 | Known different billing unit or variable chained-bot cost; also unconfirmed zero |
| 9 | No numeric pricing disclosed |

Tiers always use points, even when viewing USD. Filters combine output Modality,
Creator and Tier. A multimodal bot appears in every applicable output filter.
Unknown modality remains unknown; Creator falls back to the saved owner when
the public creator is absent. Prices with different reference units are not
directly interchangeable, so compare within a modality.

The theme uses [FontLab theme 2026](https://i.fontlab.com/fltheme26/) with native
MaterialX navigation and search. FontLab global menu/footer components are omitted.

Image-token assumptions are informed by the official
[OpenAI image cost guide](https://developers.openai.com/api/docs/guides/image-generation),
[Gemini image dimensions](https://ai.google.dev/gemini-api/docs/image-generation)
and [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing).
Seedance's estimate follows the
[BytePlus video-token formula](https://docs.byteplus.com/en/docs/modelark/model-pricing).
Other model families use the proxies described above, with explicit uncertainty.
