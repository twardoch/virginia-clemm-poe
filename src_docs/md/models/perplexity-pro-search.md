---
this_file: src_docs/md/models/perplexity-pro-search.md
---

# [perplexity-pro-search](https://poe.com/perplexity-pro-search){ .md-button .md-button--primary }

**Tier 6:** 1,994 points · 1,000 tokens (500 input + 500 output) + message fee

[Comparison method and assumptions](../pricing-method.md).

## Pricing

### Website Pricing

| Type | Cost |
|------|------|
| Base Fee (Low Context) | 1214 ($0.037) |
| Base Fee (Medium Context) | 1560 ($0.047) |
| Base Fee (High Context) | 1907 ($0.058) |
| Input Tokens | 260 ($0.0079) per 1,000 tokens |
| Output Tokens | 1300 ($0.039) per 1,000 tokens |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| Base Fee (Low Context) | USD | 0.037 | 1 base fee (low context) |
| Base Fee (Low Context) | POINTS | 1214 | 1 base fee (low context) |
| Base Fee (Medium Context) | USD | 0.047 | 1 base fee (medium context) |
| Base Fee (Medium Context) | POINTS | 1560 | 1 base fee (medium context) |
| Base Fee (High Context) | USD | 0.058 | 1 base fee (high context) |
| Base Fee (High Context) | POINTS | 1907 | 1 base fee (high context) |
| Input Tokens | USD | 0.0079 | 1000 tokens |
| Input Tokens | POINTS | 260 | 1000 tokens |
| Output Tokens | USD | 0.039 | 1000 tokens |
| Output Tokens | POINTS | 1300 | 1000 tokens |

**Last Checked:** 2026-10-05T02:11:54.624372+00:00


## Bot Information

**Creator:** empiriolabsai

**Description:** Perplexity Pro Search turns Sonar Pro into a full agentic researcher that autonomously chains web searches, and fetches full pages while streaming its live reasoning. It dynamically adapts its strategy for complex queries, far beyond standard Sonar Pro's single search. 

Parameter controls available:
1. Search Configuration
   - Search Context Size (low, medium, high\] adjusts search depth (affects cost and comprehensiveness)
   - Stream mode full switches from concise reasoning display to traditional streaming

2. Content Filtering
   - Search mode academic restricts results to academic sources
   - Search mode sec limits to SEC filings only
   - Search domain filter example.com,nasa.gov` includes only specified domains (max 20)
   - Search domain filter -pinterest.com,-spam.com` excludes domains (prefix with `-`)
   - Search language filter e.g.`en,fr,de` filters by ISO 639-1 language codes (max 10, two-letter codes)

3. Date and Recency Filters
   - Search recency filter (day, week, month, year) filters by relative time from today
   - Search after date `MM/DD/YYYY` and `Search before date `MM/DD/YYYY` for exact publication dates
   - Note: Specific dates and recency filters are mutually exclusive (dates take priority)
   - Last updated after filter `MM/DD/YYYY` and Last updated before filter `MM/DD/YYYY` filter by last modified date

4. Location-Based Search
   - Country e.g `US` sets two-letter ISO 3166-1 country code for localized results
   - Region e.g. `California` specifies state/province (requires country)
   - City e.g. "San Francisco" narrows to city level (requires country)
   - Latitude -37.7749 Longitude -122.4194 for precise coordinate-based search (requires country)

5. Media Results
   - Return images includes images in search results with inline previews
   - Image domain filter wikimedia.org,-getty.com` filters image sources (max 10, prefix `-` to exclude)
   - Image format filter e.g. jpg,png,webp restricts to specific formats (gif, jpg, png, webp supported)
   - Return videos includes embedded video previews (YouTube videos render as iframes)


## Architecture

**Input Modalities:** text

**Output Modalities:** text

**Modality:** text->text


## Technical Details

**Model ID:** `perplexity-pro-search`

**Object Type:** model

**Created:** 1763705720172

**Owned By:** EmpirioLabs AI

**Root:** perplexity-pro-search

**API Last Updated:** 2026-10-05 01:48:43.416928
