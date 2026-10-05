---
this_file: src_docs/md/models/SoulX-Podcast.md
---

# [SoulX-Podcast](https://poe.com/SoulX-Podcast){ .md-button .md-button--primary }

**Tier 6:** 1,956 points · per 4,000 characters

[Comparison method and assumptions](../pricing-method.md).

## Pricing

### Website Pricing

| Type | Cost |
|------|------|
| Base | 489 ($0.015) / 1k chars |
| Dialect | 489 ($0.015) / 1k chars |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| Base | USD | 0.015 | 1000 characters |
| Base | POINTS | 489 | 1000 characters |
| Dialect | USD | 0.015 | 1000 characters |
| Dialect | POINTS | 489 | 1000 characters |

**Last Checked:** 2026-10-05T02:09:55.653105+00:00


## Bot Information

**Creator:** empiriolabsai

**Description:** SoulX-Podcast is an open-source AI voice model developed by Soul AI Lab designed to generate realistic, long-form, multi-speaker podcast dialogues. It features advanced paralinguistic controls that simulate natural human elements like laughter and sighs, while supporting zero-shot voice cloning across Mandarin, English, and various Chinese dialects. 

Learn more: https://soul-ailab.github.io/soulx-podcast/

This model is hosted by EmpirioLabs.ai and is exclusive to the Poe platform.

Notes:
- Generations may take up to 30 minutes to complete.
- Generations are capped at 20k words (~2 hours of audio).
- Large audio files (>50mb) will be linked instead of previewed in the Poe message field due to their size. 

Parameter controls available:
1. Voice Configuration
- `--voice_s\[1-4\] \[arthur/james/lj/xiaomei/zhigang\]`: Selects preset voice for specific speaker number
- If cloning voice: Select `Custom Voice` option for speaker and upload audio

2. Model Settings
- `--model \[base/dialect\]`: partial to 'base' (English/Mandarin) or 'dialect' (+ Sichuan, Henan, Cantonese)
- `--output_format \[mp3/wav\]`: 'wav' for lossless quality, 'mp3' for smaller file size

3. Advanced Generation
- `--temperature \[0.1-2.0\]`: Controls randomness in generation (default 0.6)
- `--repetition_penalty \[1.0-2.0\]`: Penalizes repetitive output (default 1.25)
- `--seed \[number\]`: Number for reproducible results (default 42)

4. Sampling Controls
- `--top_k \[1-500\]`: Limits vocabulary to top K probable tokens (default 100)
- `--top_p \[0.1-1.0\]`: Limits vocabulary to cumulative probability P (default 0.9)


## Architecture

**Input Modalities:** Unknown

**Output Modalities:** Unknown

**Modality:** unknown


## Technical Details

**Model ID:** `SoulX-Podcast`

**Object Type:** bot

**Created:** Unknown

**Owned By:** empiriolabsai

**Root:** SoulX-Podcast

**API Last Updated:** Not listed in API
