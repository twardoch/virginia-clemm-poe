# [gpt-audio-1.5](https://poe.com/gpt-audio-1.5){ .md-button .md-button--primary }

## Bot Information

**Creator:** @binaai

**Description:** OpenAI's gpt-audio-1.5 model, brought to Poe as a server bot! This model accepts text and audio inputs and can respond with natural-sounding speech. Learn more at https://platform.openai.com/docs/models/gpt-audio-1.5.

When audio output is on, responses include both a voice recording and a text transcript. When audio output is off, one of the messages in the conversation must include an audio file attachment (audio in previous messages from either you or the bot is fine).

Optional parameters:
- enable_audio_output: either true or false to control whether responses are spoken aloud (default: true)
- voice: the name of a voice for voice outputs: "alloy", "ash", "ballad", "cedar", "coral", "echo", "fable", "marin", "nova", "onyx", "sage", or "shimmer" (default: marin)
- auto_max_tokens: Let the model decide the max number of tokens to output (enabled by default). Disable this option to manually specify a token limit between 10 and 16,384 using the max_tokens parameter.


## Architecture

**Input Modalities:** text

**Output Modalities:** audio

**Modality:** text->audio


## Technical Details

**Model ID:** `gpt-audio-1.5`

**Object Type:** model

**Created:** 1772683680804

**Owned By:** Bina AI

**Root:** gpt-audio-1.5

**API Last Updated:** 2026-10-05 01:48:43.416011
