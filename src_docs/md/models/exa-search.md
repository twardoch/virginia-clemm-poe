# [exa-search](https://poe.com/exa-search){ .md-button .md-button--primary }

## Pricing

### Website Pricing

| Type | Cost |
|------|------|
| Search (1-25 Results) | 200 ($0.0061) per search |
| Search (26-100 Results) | 1000 ($0.030) per search |
| Content (Text, Highlights, Summary) | 200 ($0.0061) per page/feature |
| Code Search | 200 ($0.0061) per 1k tokens |

All parsed rates (both currencies):

| Service | Currency | Amount | Per |
|---|---|---|---|
| Search (1-25 results) | USD | 0.0061 | 1 search |
| Search (26-100 results) | USD | 0.030 | 1 search |
| Content (Text, Highlights, Summary) | USD | 0.0061 | 1 page |
| Code Search | USD | 0.0061 | 1000 tokens |

**Last Checked:** 2026-10-05T02:11:29.858144+00:00


## Bot Information

**Creator:** empiriolabsai

**Description:** Utilize Exa's technology for searching web pages, finding similar web pages, crawling, and more.
Note: This endpoint does not return an LLM-style response (visit the following if you want an LLM-style response: https://poe.com/Exa-Answer or https://poe.com/Exa-Research). File upload is not supported. 

Parameter Controls Available:
1. Operation Mode
   - Default: Web Search
   - Find Similar pages. For finding similar pages.
   - Get page contents. For getting page contents.
   - Code search. For code search.

2. Search Settings (search operation)
   - Search Type: Select from Auto (Intelligent), Instant (Sub-150ms), Neural (Embeddings), Deep Search (Exa 2.1) and Fast (Streamlined). Default: Auto (Intelligent)
   - Show Full Content. Toggle to display full page content in results
   - Include domains. Include comma-separated domains to include
   - Include text. Input text that must appear (up to 5 words)
   - Exclude text. Input text that must NOT appear (up to 5 words)
  
3. Common Search Settings (search & similar operations)
   - Number of results: Select from 1 to 100 to set number of results to return. This is set to 10 by default.
   - Category Filter: All Categories, Company, Research Paper, News, PDF, Github, Tweet, Personal Site, LinkedIn Profile, Financial Report. This is set to None by default
   - Exclude domains. Include comma-separated domains to exclude

4. Date Filters (search operation)
   - Start Crawl Date. Results crawled after this date (ISO 8601)
   - End Crawl Date. Results crawled before this date (ISO 8601)
   - Start Published Date. Content published after this date (ISO 8601)
   - End Published Date. Content published before this date (ISO 8601)

5. Content Options (search, similar, & contents operations)
   - Return Text. Toggle to fetch page text content (default: on)
   - Max Characters. Set number to limit text length (empty = unlimited)
   - Include HTML Tags. Toggle `on` to preserve HTML structure. (default: off)
   - Return Highlights. Toggle `on` to get AI-selected key snippets. (default: off)
   - Sentences per highlight. Set sentences per highlight from 1 to 10. (default: 3)
   - Highlights per page. Set highlights per result from 1 to 10. (default: 3)
   - Highlights query. Set text to guide highlight selection
   - Return Summary. Toggle `on` to get AI-generated summaries. (default: off)
   - Summary query. Set text to guide summary generation

6. Advanced Options (search, similar, & contents operations)
   - Livecrawl Mode: Fallback (Cache first), Never (Cache only), Always (Fresh Only), Preferred (Fresh Preferred). Default: Fallback
   - Subpages to crawl. Set number of linked subpages to crawl from 0 to 10. (default: 0)
   - Subpage Target. Set text to find specific subpages matching keyword

7. Code Search Controls (code operation)
   - `--code_tokens Response Length. Set maximum length of code search results. Select from Dynamic (Optimal), 5000 tokens (Standard), 10000 tokens (Extended), 20000 tokens (Maximum). This is set to Dynamic as default.


## Architecture

**Input Modalities:** text

**Output Modalities:** text

**Modality:** text->text


## Technical Details

**Model ID:** `exa-search`

**Object Type:** model

**Created:** 1764132329592

**Owned By:** EmpirioLabs AI

**Root:** exa-search

**API Last Updated:** 2026-10-05 01:48:43.416265
