# [perplexity-adv-deep-research](https://poe.com/perplexity-adv-deep-research){ .md-button .md-button--primary }

## Bot Information

**Creator:** @empiriolabsai

**Description:** Perplexity Advanced Deep Research is designed for institutional-grade inquiry, leveraging the powerful reasoning of Claude Opus 4.6 to deliver sophisticated analysis and maximum depth. With enhanced tool access and extensive source coverage, it is the ideal choice for complex tasks requiring rigorous, comprehensive research.

Supported file types: PNG, JPEG, WEBP, GIF, PDF, DOCX, TXT

Parameter controls available:
1. General
- Reasoning effort \[low/medium/high\]: Level of reasoning depth (default: high)
- Max output tokens \[10000-16000\]: Maximum response length in tokens (default: 10000)
- Max tokens per page \[4096-16384\]: Max tokens extracted per search result page (default: 4096)

2. Search Filters
- Search domain filter \[domains\]: Comma-separated domains to include/exclude. Prefix with '-' to exclude. Max 20. (e.g., "nature.com, arxiv.org, -pinterest.com")
- Search language filter \[codes\]: Comma-separated ISO 639-1 language codes. Max 10. (e.g., "en, fr, de")

3. Date & Recency
- Search after date \[MM/DD/YYYY\]: Only include sources published after this date
- Search before date \[MM/DD/YYYY\]: Only include sources published before this date
- Search recency filter \[none/day/week/month/year\]: Relative time filter (cannot be combined with specific dates)

4. Location
- Country \[code\]: Two-letter ISO 3166-1 country code (e.g., "US", "FR", "JP")
- Region \[name\]: State or province (e.g., "California")
- City \[name\]: City name (e.g., "San Francisco")
- Latitude \[decimal\]: Latitude (must be provided with longitude and country)
- Longitude \[decimal\]: Longitude (must be provided with latitude and country)


## Architecture

**Input Modalities:** text

**Output Modalities:** text

**Modality:** text->text


## Technical Details

**Model ID:** `perplexity-adv-deep-research`

**Object Type:** model

**Created:** 1770838387525

**Owned By:** EmpirioLabs AI

**Root:** perplexity-adv-deep-research

**API Last Updated:** 2026-10-05 01:48:43.415886
