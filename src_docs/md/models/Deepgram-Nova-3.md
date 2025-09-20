# [Deepgram-Nova-3](https://poe.com/Deepgram-Nova-3){ .md-button .md-button--primary }

## Pricing

| Type | Cost |
|------|------|
| Initial Points Cost | 631+ points |
| Transcription | 631 points |

**Last Checked:** 2025-09-20 12:09:01.219207


## Bot Information

**Creator:** @empiriolabsai

**Description:** Transcribe audio files using Speech-to-Text technology with the Deepgram Nova-3 model, featuring multi-language support and advanced customizable settings.

[1] Basic Features: 
Use `--generate_pdf true` to generate a PDF file of the transcription, 
Use `--diarize true` to identify different speakers in the audio. This will automatically enable utterances.
Use `--smart_format false` to disable automatic format text for improved readability including punctuation and paragraphs. This feature is enabled by default.

[2] Advanced Features:
Use `--dictation true` to convert spoken commands for punctuation into their respective marks (e.g., 'period' becomes '.'). This will automatically enable punctuation.
Use `--measurements true` to format spoken measurement units into abbreviations
Use `--profanity_filter true` to replace profanity with asterisks
Use `--redact_pci true` to redact payment card information
Use `--redact_pii true` to redact personally identifiable information
Use `--utterances true` to segment speech into meaningful semantic units
Use `--paragraphs false` to disable paragraphs feature. This feature split audio into paragraphs to improve transcript readability. This will automatically enable punctuation. This is enabled by default.
Use `--punctuate false` to disable punctuate feature. This feature add punctuation and capitalization to your transcript. This is enabled by default.
Use `--numerals false` to disable numerals feature. This feature convert numbers from written format to numerical format

[3] Languages Supported:
Auto-detect (Default)
English
Spanish
French
German
Italian
Portuguese
Japanese
Chinese
Hindi
Russian
Dutch

[4] Key Terms `--keyterm` to enter important terms to improve recognition accuracy, separated by commas. English only, Limited to 500 tokens total.

**Extra:** Powered by a server managed by @empiriolabsai. Learn more


## Architecture

**Input Modalities:** text

**Output Modalities:** text

**Modality:** text->text


## Technical Details

**Model ID:** `Deepgram-Nova-3`

**Object Type:** model

**Created:** 1753875390474

**Owned By:** poe

**Root:** Deepgram-Nova-3
