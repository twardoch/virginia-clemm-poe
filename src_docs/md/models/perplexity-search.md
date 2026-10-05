---
this_file: src_docs/md/models/perplexity-search.md
---

# [perplexity-search](https://poe.com/perplexity-search){ .md-button .md-button--primary }

**Tier 4:** 200 points · per message

[Comparison method and assumptions](../pricing-method.md).

## Pricing

### Website Pricing

| Type | Cost |
|------|------|
| Search Request | 200 ($0.0061) per request |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| Search Request | USD | 0.0061 | 1 message |
| Search Request | POINTS | 200 | 1 message |

**Last Checked:** 2026-10-05T02:11:06.092719+00:00


## Bot Information

**Creator:** empiriolabsai

**Description:** Utilize Perplexity's technology for real-time web search with filtering by domain, language, date and more.
Note: This endpoint does not return an LLM-style response. File upload is not supported.

Parameter Controls Available:
1. General
   - `query` (required): Your search query as a single string
   - `multi_query`: Up to 5 queries separated by newlines for batch searching
   - `max_results` \[1-20\]: Number of search results to return (default 5)
   - `max_tokens` \[5000-100000\]: Total content token budget across all results
   - `max_tokens_per_page` \[256-8192\]: Maximum tokens extracted per individual page

2. Filters
   - `search_domain_filter`: Allow or deny specific domains (prefix with `-` to deny, max 20, no mixing allow/deny)
   - `search_language_filter`: Restrict results by language using ISO 639-1 codes (e.g. `en`, `fr`), comma-separated, max 10
   - `country`: Restrict results by country using ISO 3166-1 alpha-2 code (e.g. `US`, `GB`)

3. Date & Recency
   - `search_recency_filter`: Limit results to `hour`, `day`, `week`, `month`, or `year`
   - `search_after_date_filter` (MM/DD/YYYY): Only return results published after this date (overrides recency)
   - `search_before_date_filter` (MM/DD/YYYY): Only return results published before this date (overrides recency)
   - `last_updated_after_filter` (MM/DD/YYYY): Only return results last updated after this date
   - `last_updated_before_filter` (MM/DD/YYYY): Only return results last updated before this date
   - `display_server_time`: Toggle to include the server timestamp in the response


## Architecture

**Input Modalities:** text

**Output Modalities:** text

**Modality:** text->text


## Technical Details

**Model ID:** `perplexity-search`

**Object Type:** model

**Created:** 1771723986988

**Owned By:** EmpirioLabs AI

**Root:** perplexity-search

**API Last Updated:** 2026-10-05 01:48:43.415907
