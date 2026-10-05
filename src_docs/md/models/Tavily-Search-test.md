# [Tavily-Search-test](https://poe.com/Tavily-Search-test){ .md-button .md-button--primary }

## Bot Information

**Creator:** @empiriolabsai

**Description:** Utilize Tavily's technology to search web pages and to crawl, extract, and map URLs.
Note: File upload is not supported.

Parameter controls available:
1. Operation Modes
- Default: Search (no `--operation_mode` needed)
- If crawling a website: `--operation_mode Crawl`
- If extracting content from URLs: `--operation_mode Extract`
- If mapping a website structure: `--operation_mode Map`
2. Search Configuration (Search Mode)
- `--search_depth \[basic|advanced|fast|ultra-fast\]`: Depth of search (basic=standard, advanced=high quality, fast=low latency, ultra-fast=lowest latency)
- `--search_chunks_per_source \[1-3\]`: Max relevant chunks per source (Advanced depth only)
- `--search_topic \[general|news|finance\]`: Category of search
- `--max_results \[1-20\]`: Number of results to return
- `--time_range \[none|day|week|month|year\]`: Filter results by publish/update date
- `--start_date "YYYY-MM-DD"`: Filter results after this date
- `--end_date "YYYY-MM-DD"`: Filter results before this date
- `--country \[country_code\]`: Boost results from a specific country (General topic only)
- `--include_domains "domain1,domain2"`: Comma-separated domains to include
- `--exclude_domains "domain1,domain2"`: Comma-separated domains to exclude
- `--include_answer \[false|basic|advanced\]`: Include an LLM-generated answer
- `--include_raw_content \[false|markdown|text\]`: Include full page content
- `--include_images true`: Include related images
- `--include_image_descriptions true`: Add descriptive text for each image
- `--include_favicon true`: Include favicon URL for each result
- `--auto_parameters true`: Let Tavily optimize parameters automatically
3. Crawl Configuration (Crawl Mode)
- `--crawl_limit \[1-100\]`: Maximum number of pages to crawl
- `--crawl_max_depth \[1-5\]`: How far from base URL to explore
- `--crawl_max_breadth \[1-50\]`: Max links to follow per page
- `--crawl_extract_depth \[basic|advanced\]`: Depth of content extraction
- `--crawl_format \[markdown|text\]`: Format of extracted content
- `--crawl_instructions "text"`: Natural language instructions for intelligent crawling
- `--crawl_chunks_per_source \[1-5\]`: Max relevant chunks per source (with instructions)
- `--crawl_select_paths "regex"`: Regex patterns for paths to include
- `--crawl_exclude_paths "regex"`: Regex patterns for paths to exclude
- `--crawl_select_domains "regex"`: Regex patterns for domains to include
- `--crawl_exclude_domains "regex"`: Regex patterns for domains to exclude
- `--crawl_allow_external true`: Include external domain links
- `--crawl_include_images true`: Include images from crawled pages
- `--crawl_include_favicon true`: Include favicon URL for each result
- `--crawl_timeout \[10-150\]`: Max time to wait for crawl operation (seconds)
4. Extract Configuration (Extract Mode)
- `--extract_depth \[basic|advanced\]`: Depth of content extraction
- `--extract_format \[markdown|text\]`: Format of extracted content
- `--extract_query "text"`: User intent for reranking extracted content chunks
- `--extract_chunks_per_source \[1-5\]`: Max relevant chunks per source (with query)
- `--extract_include_images true`: Include images from extracted pages
- `--extract_include_favicon true`: Include favicon URL for each result
- `--extract_timeout \[1-60\]`: Max time per URL extraction (seconds)
5. Map Configuration (Map Mode)
- `--map_limit \[1-100\]`: Maximum number of pages to map
- `--map_depth \[1-5\]`: Depth of mapping traversal
- `--map_breadth \[1-50\]`: Max links to follow per page
- `--map_instructions "text"`: Natural language instructions for intelligent mapping
- `--map_select_paths "regex"`: Regex patterns for paths to include
- `--map_exclude_paths "regex"`: Regex patterns for paths to exclude
- `--map_select_domains "regex"`: Regex patterns for domains to include
- `--map_exclude_domains "regex"`: Regex patterns for domains to exclude
- `--map_allow_external true`: Include external domain links
- `--map_timeout \[10-150\]`: Max time to wait for map operation (seconds)


## Architecture

**Input Modalities:** Unknown

**Output Modalities:** Unknown

**Modality:** unknown


## Technical Details

**Model ID:** `Tavily-Search-test`

**Object Type:** bot

**Created:** Unknown

**Owned By:** empiriolabsai

**Root:** Tavily-Search-test

**API Last Updated:** Not listed in API
