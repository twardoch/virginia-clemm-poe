# [gemini-3.1-flash-tts](https://poe.com/gemini-3.1-flash-tts){ .md-button .md-button--primary }

## Bot Information

**Creator:** @empiriolabsai

**Description:** Gemini 3.1 Flash TTS is Google’s most controllable text-to-speech model yet, designed to turn text into natural-sounding audio with precise control over style, tone, pace, and delivery. It uses new Audio Tags to make voices feel more expressive and customizable for narration, assistants, and other voice experiences.

Notes:
- Text and style prompt limited to 4,000 bytes each (8,000 bytes combined)
- Max output duration: approximately 10 minutes
- Multi-speaker requires SpeakerName: text format (example: Alice: Hi! Bob: Hello, must be on new lines)
- The model auto-detects the input language. The Language setting is a hint to help choose the right voice/accent, the model may override it if the text is in a different language.

Expressive Audio Tags:
- Use inline in your text to control delivery
- Emotion/tone: \[whispers\], \[shouts\], \[laughs\], \[cries\], \[sighs\], \[gasps\], \[groans\], \[scoffs\], \[sarcasm\], \[deadpan\], \[cheerful\], \[sad\], \[angry\], \[fearful\], \[surprised\], \[disgusted\], \[confused\], \[nervous\], \[bored\], \[excited\], \[relieved\], \[hopeful\], \[proud\], \[shy\], \[sincere\], \[playful\], \[serious\], \[tender\], \[dramatic\], \[monotone\], \[warm\], \[cold\]
- Pace/speed: \[slow\], \[fast\], \[extremely fast\], \[extremely slow\], \[normal pace\]
- Pauses: \[short pause\], \[long pause\], \[pause\], \[breath\]
- Emphasis/delivery: \[emphasis\], \[softly\], \[loudly\], \[high pitch\], \[low pitch\], \[rising tone\], \[falling tone\]
- Example: "\[whispers\] I have a secret. \[normal pace\] But first, let me explain."

This bot supports optional parameters for additional customization.


## Architecture

**Input Modalities:** text

**Output Modalities:** audio

**Modality:** text->audio


## Technical Details

**Model ID:** `gemini-3.1-flash-tts`

**Object Type:** model

**Created:** 1776295398177

**Owned By:** EmpirioLabs AI

**Root:** gemini-3.1-flash-tts

**API Last Updated:** 2026-10-05 01:48:43.418822
