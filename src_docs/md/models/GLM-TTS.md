# [GLM-TTS](https://poe.com/GLM-TTS){ .md-button .md-button--primary }

## Pricing

### Website Pricing

| Type | Cost |
|------|------|
| Fast (Int8) | 6806 ($0.21) / 1k chars |
| Quality (Fp16) | 6976 ($0.21) / 1k chars |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| Fast (INT8) | USD | 0.21 | 1000 characters |
| Quality (FP16) | USD | 0.21 | 1000 characters |

**Last Checked:** 2026-10-05T02:08:57.744410+00:00


## Bot Information

**Creator:** empiriolabsai

**Description:** GLM-TTS is a high-quality, LLM-based text-to-speech system that supports zero-shot voice cloning from 3–10 seconds of audio and text-to-speech synthesis. It provides controllable, emotion-expressive speech via multi-reward reinforcement learning, with phoneme-level control and strong performance on the seed-tts-eval benchmark.

This model is hosted by EmpirioLabs.ai and is exclusive to the Poe platform.

Notes:
- Supported audio upload types: WAV, MP3, OGG, FLAC, AAC, M4A, WebM
- The max TTS length is 5000 characters
- Generations may take upwards of 5-10 minutes to complete

Parameter controls available:
1. Voice
- Default: `--voice emma` (Emma - English Female)
- `--voice james` (James - US Male)
- `--voice arthur` (Arthur - UK Male)
- `--voice xiaomei` (Xiaomei - Chinese Female)
- `--voice zhigang` (Zhigang - Chinese Male)
- `--voice custom` for voice cloning (requires audio upload)

2. Audio Output
- `--output_format mp3` (default, smaller file) or `--output_format wav` (lossless, larger file)
- `--speed \[0.5-2.0\]` speech rate multiplier (default 1.0)

3. Advanced
- `--model_quality quality` (FP16 - better, default) or `--model_quality fast` (INT8 - quicker)
- `--sample_rate 24000` (24 kHz, default) or `--sample_rate 16000` (16 kHz)
- `--volume \[0.1-2.0\]` output volume multiplier (default 1.0)
- `--seed \[1-999999\]` for reproducible results (leave empty for random)
- `--use_cache true` (default) or `--use_cache false` to disable caching
- '-optimize_input true' (default) or '--optimize_input false' to skip text optimization


## Architecture

**Input Modalities:** Unknown

**Output Modalities:** Unknown

**Modality:** unknown


## Technical Details

**Model ID:** `GLM-TTS`

**Object Type:** bot

**Created:** Unknown

**Owned By:** empiriolabsai

**Root:** GLM-TTS

**API Last Updated:** Not listed in API
