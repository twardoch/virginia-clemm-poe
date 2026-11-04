---
this_file: issues/342-results.md
---

# Issue 342: bots ranked by saved price

**Gemma-4-31B is explicitly free. GPT-5-nano is the cheapest paid text bot for the reference workload: 7 points for 500 input + 500 output tokens.** Among image bots with a disclosed per-image price, GPT-Image-1-Mini starts at 167 points for a low-quality 1024×1024 output. Among video bots with time-based pricing, Wan-2.6 Flash starts at 750 points/second, restricted to image/reference-to-video without audio.

## Sources and scope

Prepared 2026-11-03 from [issue 342](342.md) and the saved [package JSON snapshot](https://github.com/twardoch/virginia-clemm-poe/blob/4c2fe87ffa33a1a711d297c0570a1e2824285f39/src/virginia_clemm_poe/data/poe_bots.json), using `pricing.scraped.details.rates` and the surrounding `rate_card`. Its SHA-256 is `ca9af865b54f8c56f3ab06cf5f457e2690042a3af95b2693b39a04b060c06e71`. The source has 492 bots; matched website-price observations run from **2026-10-22 12:59:41.933961 to 2026-10-22 13:46:12.135618 UTC on 22 October 2026**. These are historical observations, not live quotes.

The issue contains **120 entries, 116 distinct bots**. Four image bots appear in both Text and Image: Nano-Banana-2-Lite, Nano-Banana-2.1, Nano-Banana-2 and Nano-Banana-Pro. They appear once here under image pricing. Qwen-Image-2, Qwen-Image-2-Pro and Seedream-4.5 also move from Text to image pricing. Five additional handles occur only in description links; they are included below and marked **†**. In total, **121 distinct handles are accounted for: 118 matched and three absent**.

Every numeric table is sorted cheapest first by points, with alphabetical ties. Comparisons use the same workload within each table. Token-priced media stay separate where the JSON gives no reliable tokens-per-image or tokens-per-second conversion. No single whole-job ranking across text, images and video can be inferred from these units.

Points and USD are calculated independently from the saved website rates; rounded currencies can give slightly different orders. USD is the rate-card value, not a conversion from purchased subscription points. API prices, optional search/tools, cached-input discounts, image/audio/video inputs and extra reasoning tokens are excluded unless a row explicitly includes them. Longer contexts, output settings and task length can change actual charges.

## Text: 500 input + 500 output tokens

**Formula:** `(input points/1k + output points/1k) / 2 + mandatory message fee`. These are uncached text-only requests without tools, at the lowest disclosed context tier. All input/output columns are points per 1,000 tokens; the fee is points per message. Gemma uses its explicit zero per-message rate.

| Bot | Input /1k | Output /1k | Fee | Reference points | Reference USD |
| --- | --- | --- | --- | --- | --- |
| [Gemma-4-31B](https://poe.com/gemma-4-31b) | 0 | 0 | 0 | 0 | $0 |
| [GPT-5-nano](https://poe.com/gpt-5-nano) | 2 | 12 | 0 | 7 | $0.000202 |
| [Claude-Haiku-5.5](https://poe.com/claude-haiku-5.5) | 4 | 17 | 0 | 10.5 | $0.000305 |
| [GPT-6-Luna](https://poe.com/GPT-6-Luna) | 4 | 17 | 0 | 10.5 | $0.000305 |
| [DeepSeek-V3.2](https://poe.com/deepseek-v3.2) | 9 | 13 | 0 | 11 | $0.00032 |
| [Qwen3.8-Flash-EL](https://poe.com/qwen3.8-flash-el) † | 6 | 16 | 0 | 11 | $0.000315 |
| [Seed-2.0-Mini](https://poe.com/seed-2.0-mini) | 5 | 17 | 0 | 11 | $0.00032 |
| [GPT-4o-mini](https://poe.com/gpt-4o-mini) | 5 | 18 | 0 | 11.5 | $0.000345 |
| [GPT-OSS-120B](https://poe.com/gpt-oss-120b) | 5 | 20 | 0 | 12.5 | $0.00038 |
| [Hy3](https://poe.com/hy3) | 5 | 20 | 0 | 12.5 | $0.000365 |
| [Mistral-Small-4](https://poe.com/mistral-small-4) | 5 | 20 | 0 | 12.5 | $0.000375 |
| [DeepSeek-v3.1](https://poe.com/deepseek-v3.1) | 7 | 27 | 0 | 17 | $0.000505 |
| [GPT-5.6-Luna](https://poe.com/GPT-5.6-Luna) | 6 | 36 | 0 | 21 | $0.000635 |
| [GPT-5.4-Nano](https://poe.com/gpt-5.4-nano) | 6 | 38 | 0 | 22 | $0.00066 |
| [MiniMax-M2.1](https://poe.com/minimax-m2.1) | 10 | 40 | 0 | 25 | $0.000755 |
| [MiniMax-M2.5](https://poe.com/minimax-m2.5) | 10 | 40 | 0 | 25 | $0.000755 |
| [MiniMax-M3](https://poe.com/minimax-m3) | 10 | 40 | 0 | 25 | $0.000755 |
| [DeepSeek-V4-Flash](https://poe.com/deepseek-v4-flash) | 15 | 44 | 0 | 29.5 | $0.000885 |
| [Gemini-3.1-Flash-Lite](https://poe.com/gemini-3.1-flash-lite) | 9 | 50 | 0 | 29.5 | $0.000885 |
| [GPT-4.1-mini](https://poe.com/gpt-4.1-mini) | 12 | 48 | 0 | 30 | $0.000905 |
| [GPT-5-mini](https://poe.com/gpt-5-mini) | 8 | 60 | 0 | 34 | $0.001025 |
| [Qwen3.5-Omni-Flash](https://poe.com/qwen3.5-omni-flash) | 13 | 73 | 0 | 43 | $0.0013 |
| [Gemini-3-Flash](https://poe.com/gemini-3-flash) | 14 | 80 | 0 | 47 | $0.00141 |
| [Gemini-3.5-Flash-Lite](https://poe.com/gemini-3.5-flash-lite) | 10 | 84 | 0 | 47 | $0.001415 |
| [GLM-4.6](https://poe.com/glm-4.6) | 20 | 74 | 0 | 47 | $0.001415 |
| [Seed-2.0-Lite](https://poe.com/seed-2.0-lite) | 11 | 84 | 0 | 47.5 | $0.001425 |
| [Grok-4.20-Multi-Agent](https://poe.com/grok-4.20-multi-agent) | 42 | 84 | 0 | 63 | $0.001895 |
| [Grok-4.3](https://poe.com/grok-4.3) | 42 | 84 | 0 | 63 | $0.001895 |
| [Seed-2.0-Pro](https://poe.com/seed-2.0-pro) | 21 | 125 | 0 | 73 | $0.00221 |
| [Gemini-3.6-Flash](https://poe.com/gemini-3.6-flash) | 25 | 125 | 0 | 75 | $0.002275 |
| [Gemini-3.7-Flash](https://poe.com/gemini-3.7-flash) | 25 | 125 | 0 | 75 | $0.002275 |
| [Gemini-3.8-Flash](https://poe.com/gemini-3.8-flash) | 25 | 125 | 0 | 75 | $0.002275 |
| [GPT-5.4-Mini](https://poe.com/gpt-5.4-mini) | 23 | 135 | 0 | 79 | $0.002385 |
| [Kimi-K2.6](https://poe.com/kimi-k2.6) | 32 | 134 | 0 | 83 | $0.0025 |
| [Kimi-K2.7-Code](https://poe.com/kimi-k2.7-code) | 32 | 134 | 0 | 83 | $0.0025 |
| [Claude-Haiku-4.5](https://poe.com/claude-haiku-4.5) | 29 | 142 | 0 | 85.5 | $0.002575 |
| [DeepSeek-V4-Pro](https://poe.com/deepseek-v4-pro) | 44 | 132 | 0 | 88 | $0.002665 |
| [Muse-Spark-1.1](https://poe.com/Muse-Spark-1.1) | 42 | 142 | 0 | 92 | $0.002775 |
| [GLM-5.2](https://poe.com/glm-5.2) | 50 | 150 | 0 | 100 | $0.003035 |
| [Grok-4.5](https://poe.com/grok-4.5) | 67 | 200 | 0 | 133.5 | $0.00404 |
| [Grok-4.6](https://poe.com/grok-4.6) | 67 | 200 | 0 | 133.5 | $0.00404 |
| [Grok-4.7](https://poe.com/grok-4.7) | 67 | 200 | 0 | 133.5 | $0.00404 |
| [GPT-4.1](https://poe.com/gpt-4.1) | 60 | 240 | 0 | 150 | $0.004545 |
| [Qwen3.5-Omni-Plus](https://poe.com/qwen3.5-omni-plus) | 47 | 277 | 0 | 162 | $0.00485 |
| [GPT-5](https://poe.com/gpt-5) | 38 | 300 | 0 | 169 | $0.005115 |
| [GPT-5.1](https://poe.com/gpt-5.1) | 38 | 300 | 0 | 169 | $0.005115 |
| [Gemini-3.5-Flash](https://poe.com/gemini-3.5-flash) | 50 | 300 | 0 | 175 | $0.005305 |
| [GPT-4o](https://poe.com/gpt-4o) | 75 | 300 | 0 | 187.5 | $0.005625 |
| [GPT-4o-Aug](https://poe.com/gpt-4o-aug) | 75 | 300 | 0 | 187.5 | $0.00568 |
| [Claude-Sonnet-5](https://poe.com/Claude-Sonnet-5) | 67 | 334 | 0 | 200.5 | $0.00606 |
| [Claude-Sonnet-5.5](https://poe.com/claude-sonnet-5.5) | 67 | 334 | 0 | 200.5 | $0.00606 |
| [GPT-6-Sol](https://poe.com/GPT-6-Sol) | 67 | 334 | 0 | 200.5 | $0.00606 |
| [GPT-6.1-Sol](https://poe.com/GPT-6.1-Sol) | 67 | 334 | 0 | 200.5 | $0.00606 |
| [GPT-5.6-Terra](https://poe.com/GPT-5.6-Terra) | 60 | 360 | 0 | 210 | $0.006365 |
| [Qwen3.5-Plus-EL](https://poe.com/qwen3.5-plus-el) | 12 | 74 | 167 | 210 | $0.006395 |
| [Gemini-3.1-Pro](https://poe.com/gemini-3.1-pro) | 67 | 400 | 0 | 233.5 | $0.00707 |
| [GPT-5.2](https://poe.com/gpt-5.2) | 53 | 420 | 0 | 236.5 | $0.00716 |
| [Claude-Sonnet-4.5](https://poe.com/claude-sonnet-4.5) | 85 | 425 | 0 | 255 | $0.00773 |
| [Claude-Sonnet-4.6](https://poe.com/claude-sonnet-4.6) | 85 | 425 | 0 | 255 | $0.00773 |
| [GPT-5.4](https://poe.com/gpt-5.4) | 75 | 450 | 0 | 262.5 | $0.007955 |
| [Qwen3.5-Flash-EL](https://poe.com/qwen3.5-flash-el) | 3 | 13 | 334 | 342 | $0.01023 |
| [GPT-5.6-Sol](https://poe.com/GPT-5.6-Sol) | 120 | 667 | 0 | 393.5 | $0.01192 |
| [Claude-Opus-5.5](https://poe.com/Claude-Opus-5.5) | 134 | 667 | 0 | 400.5 | $0.01212 |
| [Gemini-4-Argon](https://poe.com/Gemini-4-Argon) | 134 | 667 | 0 | 400.5 | $0.01212 |
| [Muse-Wonder-1.0](https://poe.com/muse-wonder-1.0) † | 134 | 667 | 0 | 400.5 | $0.01212 |
| [Claude-Opus-4.5](https://poe.com/claude-opus-4.5) | 142 | 709 | 0 | 425.5 | $0.012875 |
| [Claude-Opus-4.6](https://poe.com/claude-opus-4.6) | 142 | 709 | 0 | 425.5 | $0.012875 |
| [Claude-Opus-4.7](https://poe.com/claude-opus-4.7) | 142 | 709 | 0 | 425.5 | $0.012875 |
| [Claude-Opus-4.8](https://poe.com/claude-opus-4.8) | 142 | 709 | 0 | 425.5 | $0.012875 |
| [Claude-Opus-5](https://poe.com/Claude-Opus-5) | 167 | 834 | 0 | 500.5 | $0.01515 |
| [GPT-5.5](https://poe.com/GPT-5.5) | 150 | 900 | 0 | 525 | $0.01591 |
| [GPT-6-Astra](https://poe.com/GPT-6-Astra) | 300 | 1,500 | 0 | 900 | $0.02727 |
| [Claude-Fable-5](https://poe.com/Claude-Fable-5) | 334 | 1,667 | 0 | 1,000.5 | $0.030305 |
| [Claude-Fable-5.1](https://poe.com/Claude-Fable-5.1) | 334 | 1,667 | 0 | 1,000.5 | $0.030305 |
| [Perplexity-Sonar-Pro](https://poe.com/perplexity-sonar-pro) | 240 | 1,200 | 480 | 1,200 | $0.03665 |
| [GPT-5-Pro](https://poe.com/gpt-5-pro) | 450 | 3,600 | 0 | 2,025 | $0.061365 |
| [GPT-5.2-Pro](https://poe.com/gpt-5.2-pro) | 630 | 5,040 | 0 | 2,835 | $0.08591 |
| [GPT-5.4-Pro](https://poe.com/gpt-5.4-pro) | 900 | 5,400 | 0 | 3,150 | $0.095455 |
| [GPT-5.5-Pro](https://poe.com/GPT-5.5-Pro) | 900 | 5,400 | 0 | 3,150 | $0.095455 |

Qwen3.5-Plus-EL adds **167 points/message** and Qwen3.5-Flash-EL adds **334**; omitting these would make their ranking misleading. Perplexity-Sonar-Pro includes its **480-point low-context base fee**; medium/high tiers add 320/640 points to this example. Qwen Omni uses the Text / Image / Video input row and Text Only output row; its separately priced audio and search modes are excluded. Mistral-Small-4 uses its text rates, not its optional 9,333-point image tool; search and code tools are also extra. GPT-4o uses its text-chat input rate, not its separate image-generation input rate.

At another input/output ratio the order can change: DeepSeek-V3.2 and Qwen3.8-Flash-EL tie at 11 points here, but DeepSeek has cheaper output (13 versus 16 points/1k) and more expensive input (9 versus 6). Output-heavy requests favour DeepSeek; input-heavy requests favour Qwen. The issue also records higher context pricing for Qwen3.5-Plus-EL (>256k) and Seed-2.0-Lite/Pro (>128k).

## Images: disclosed per-image or per-message output

Sorted by the cheapest disclosed output option. A per-message row retains that unit; the saved quote does not establish the number of images returned. Prompt/input-image charges and editing surcharges are extra. These rows compare entry prices, not equal quality or resolution.

| Bot | Output points | Output USD | Billing unit | Selected setting |
| --- | --- | --- | --- | --- |
| [GPT-Image-1-Mini](https://poe.com/gpt-image-1-mini) | 167 | $0.005 | per image | Low quality, 1024×1024 |
| [GPT-Image-1.5](https://poe.com/gpt-image-1.5) | 262 | $0.0078 | per image | Low quality, 1024×1024 |
| [FLUX-2-Dev](https://poe.com/flux-2-dev) | 500 | $0.015 | per image | Cheapest disclosed output option |
| [Grok-Imagine-Image](https://poe.com/grok-imagine-image) | 667 | $0.02 | per image | Cheapest disclosed output option |
| [Seedream-4.0](https://poe.com/seedream-4.0) | 1,000 | $0.03 | per message | Cheapest disclosed output option |
| [Wan2.7-Image](https://poe.com/wan2.7-image) | 1,000 | $0.03 | per image | Standard; Pro is 2,500 points/image |
| [Qwen-Image-2](https://poe.com/qwen-image-2) | 1,167 | $0.035 | per message | Cheapest disclosed output option |
| [Seedream-5.0-Lite](https://poe.com/seedream-5.0-lite) | 1,167 | $0.035 | per message | Cheapest disclosed output option |
| [Ideogram-v2a](https://poe.com/ideogram-v2a) | 1,300 | $0.039 | per message | Cheapest disclosed output option |
| [Seedream-4.5](https://poe.com/seedream-4.5) | 1,334 | $0.04 | per message | Cheapest disclosed output option |
| [Ideogram-v2](https://poe.com/ideogram-v2) | 1,900 | $0.058 | per message | Cheapest disclosed output option |
| [FLUX-2-Flex](https://poe.com/flux-2-flex) | 2,000 | $0.061 | per image | Cheapest disclosed output option |
| [Qwen-Image-2-Pro](https://poe.com/qwen-image-2-pro) | 2,500 | $0.076 | per message | Cheapest disclosed output option |
| [Flux-Kontext-Max](https://poe.com/flux-kontext-max) | 2,667 | $0.081 | per message | Cheapest disclosed output option |

GPT-Image-1.5 defaults to high quality according to the issue: its saved high-quality 1024×1024 price is **3,994 points**, versus **262** at low quality. GPT-Image-1-Mini is **367** at medium and **1,200** at high quality for 1024×1024. High-fidelity editing adds **2,000** points for GPT-Image-1.5 and **400** for GPT-Image-1-Mini. FLUX-2-Dev adds 500 points per input image; FLUX-2-Flex adds 2,000 points per input megapixel. Grok-Imagine-Image adds 67 points per input image.

### Images billed by output tokens

The JSON does not specify image-token counts for the chosen resolution. These are **per 1,000 output image tokens**, not full-image prices; prompt and any text output are extra.

| Bot | Points /1k image tokens | USD /1k image tokens |
| --- | --- | --- |
| [Nano-Banana-2-Lite](https://poe.com/nano-banana-2-lite) | 1,000 | $0.0303 |
| [Nano-Banana-2.1](https://poe.com/nano-banana-2.1) | 1,000 | $0.0303 |
| [Nano-Banana-2](https://poe.com/nano-banana-2) | 2,000 | $0.06061 |
| [Nano-Banana-Pro](https://poe.com/nano-banana-pro) | 4,000 | $0.12121 |

### Images billed by megapixel

| Bot | Saved output rate | Saved input rate | Limitation |
| --- | --- | --- | --- |
| [FLUX-2-Pro](https://poe.com/flux-2-pro) | 1,000 points ($0.030) / first output MP | 500 points ($0.015) / input MP | Additional output-MP pricing is absent; no full 1024×1024 (1.048576 MP) quote is inferred. |

### Image bots whose saved output label is inconsistent

| Bot | Saved text input /1k | Saved image input /1k | Saved **text-labelled** output /1k |
| --- | --- | --- | --- |
| [GPT-Image-2](https://poe.com/gpt-image-2) | 167 points ($0.00505) | 267 points ($0.00808) | 1,000 points ($0.03030) |
| [GPT-Image-2.5-Flare](https://poe.com/GPT-Image-2.5-Flare) | 167 points ($0.00505) | 267 points ($0.00808) | 1,000 points ($0.03030) |
| [GPT-Image-2.5-Sunburst](https://poe.com/GPT-Image-2.5-Sunburst) | 167 points ($0.00505) | 267 points ($0.00808) | 1,000 points ($0.03030) |

These three bots are described as image generators, but the JSON labels their output **Output (text)** and has no explicit image-output price or image-token conversion. They cannot be reliably ranked by whole-image cost from this snapshot; the output label is preserved rather than silently reinterpreted.

## Video: cost normalised to 10 seconds

Use `10 × points/second`; clip-priced rows preserve their duration context. This is a duration-normalised comparison, **not a promise that every bot offers a 10-second clip**. Settings differ: cheapest resolution/mode/audio choice is shown. Input/reference charges are extra. Wan-2.6 reference-to-video bills input video duration as well as output duration.

| Bot | Points /10s | USD /10s | Selected setting and qualifications |
| --- | --- | --- | --- |
| [Wan-2.6](https://poe.com/wan-2.6) | 7,500 | $0.225 | Flash 720p, without audio; I2V/R2V only. Standard 720p: 30,000 points/10s. |
| [Veo-3.1-Lite](https://poe.com/veo-3.1-lite) | 15,000 | $0.5 | 720p; duration-normalised amount; issue requires 8s for 1080p. |
| [Pixverse-v5](https://poe.com/pixverse-v5) | 15,334 | $0.46 | 360p/540p, 5s clip costs 7,667; doubled for comparison, not a 10s quote. |
| [Grok-Imagine-Video](https://poe.com/grok-imagine-video) | 16,670 | $0.51 | Video output only; add 67 points per input image. |
| [Wan-2.5](https://poe.com/wan-2.5) | 16,670 | $0.51 | 480p; 720p costs 33,340 points/10s. |
| [Kling-2.5-Turbo-Pro](https://poe.com/kling-2.5-turbo-pro) | 23,340 | $0.71 | Video output. |
| [Pixverse-v5.6](https://poe.com/pixverse-v5.6) | 25,667 | $0.78 | Actual 10s 360p/540p clip, without audio; 5s costs 11,667. |
| [Wan-2.7](https://poe.com/wan-2.7) | 33,330 | $1 | 720p; 1080p costs 50,000 points/10s. |
| [Veo-v3.1-Fast](https://poe.com/veo-v3.1-fast) † | 33,340 | $1 | Video output; audio + video costs 50,000 points/10s. |
| [Veo-3.1-Fast](https://poe.com/veo-3.1-fast) | 45,000 | $1.35 | Normalised from per-second rate; issue permits 4/6/8s clips. |
| [Kling-O3](https://poe.com/kling-o3) | 56,000 | $1.7 | Standard text/image, no sound; 4K costs 175,000 points/10s. |
| [Kling-v3-Pro](https://poe.com/kling-v3-pro) | 74,670 | $2.3 | Without audio; with audio costs 112,000 points/10s. |

Pixverse-v5.6 has duration-specific prices: the actual 10s silent 360p/540p quote is **25,667 points**. Scaling its 5s price to 23,334 points would understate that quote. Pixverse-v5 offers 5s/8s clips in the issue; its 15,334-point figure is only two times the cheapest 5s price.

### Video billed by output tokens

| Bot | Points /1k video tokens | USD /1k video tokens |
| --- | --- | --- |
| [Seedance-2-Fast](https://poe.com/seedance-2-fast) | 374 | $0.011 |
| [Seedance-2.0](https://poe.com/seedance-2.0) | 467 | $0.014 |
| [Gemini-Omni-1.1-Flash](https://poe.com/gemini-omni-1.1-flash) | 584 | $0.01768 |

The saved rates provide no dependable conversion to clip duration for these three bots. Seedance-2-Fast is cheaper than Seedance-2.0 **per output token**. The issue description separately estimates 10,300 tokens/second at 480p and 22,100 at 720p for both Seedance variants; applying those description estimates to the JSON point rates gives Fast **3,852.2 / 8,265.4 points per second**, versus standard **4,809.1 / 10,320.7**. These are conditional estimates, excluded from the time-priced ranking. The issue’s Fast dollar estimate uses $0.0112/1k tokens, whereas the saved JSON rounds that rate to $0.011; the table preserves the JSON value. Gemini-Omni-1.1-Flash has no duration conversion in the issue or its saved rate card.

## Agents: incomplete or task-dependent totals

| Bot | Saved points | Saved USD | Interpretation |
| --- | --- | --- | --- |
| [Interpreter](https://poe.com/interpreter) | 1 / message **plus called bots** | Not disclosed | Wrapper fee only; the total depends on which bots it calls. |
| [Manus](https://poe.com/manus) | Lite typically 47,667–86,667; Standard 95,334–173,334; Max 173,334–303,334 | Lite $1.44–2.63; Standard $2.89–5.25; Max $5.25–9.19 | Typical task ranges, not floors or ceilings; the card says actual cost may fall below or exceed them. |

## Missing from the saved JSON

| Handle in the issue | Where mentioned | Result |
| --- | --- | --- |
| GPT-6.1-Terra | Text entry and GPT-5.6-Terra description | No matching record; no price inferred from an older Terra model. |
| GPT-Image-1 † | GPT-4o description | No matching standalone record; GPT-4o’s embedded image rate card is not substituted for it. |
| Ideogram-v2A-Turbo † | Ideogram-v2a description | No matching record; no price inferred from Ideogram-v2a. |

## Verification

All 116 distinct catalogue entries and five additional description-link handles are covered. Matching is case-insensitive and exact otherwise; links use the JSON’s canonical IDs. The three absent handles and three image bots with inconsistent output labels are explicitly identified. The source JSON and issue are unchanged.

The report calculations use decimal arithmetic; displayed USD values are rounded to six decimal places. An independent audit of the saved Markdown verified **121/121 handles exactly once**, recomputed **all 112 ranked rows** from source rates, and checked ascending order in all five ranked tables. Checks include mandatory Qwen fees, Perplexity’s base fee, Qwen Omni heading context, Mistral text versus tool pricing, GPT-4o text versus image pricing, Pixverse duration context and duplicate removal. The existing `uvx hatch test` run passed **231 tests**, but its coverage gate failed: **64.97% against 85% required**. The existing JavaScript pricing checks also passed **18/18**. No live prices or browser generation were checked.
