# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# virginia-clemm-poe

A Python package providing programmatic access to Poe.com model data with pricing information.

## 1. Overview

Virginia Clemm Poe is a companion tool for Poe.com's API (introduced August 25, 2024) that fetches and maintains comprehensive model data including pricing information. The package provides both a Python API for querying model data and a CLI for updating the dataset.

## 2. Features

- **Model Data Access**: Query Poe.com models by various criteria including ID, name, and other attributes
- **Pricing Information**: Automatically scrapes and syncs pricing data for all available models
- **Pydantic Models**: Fully typed data models for easy integration
- **CLI Interface**: Fire-based CLI for updating data and searching models
- **Browser Automation**: Uses external PlaywrightAuthor package for reliable web scraping

## 3. Installation

```bash
pip install virginia-clemm-poe
```

## 4. Usage

### 4.1. Python API

```python
from virginia_clemm_poe import api

# Search for models
models = api.search_models(query="claude")

# Get model by ID
model = api.get_model_by_id("claude-3-opus")

# Access pricing information
if model.pricing:
    print(f"Input cost: {model.pricing.details['Input (text)']}")
```

### 4.2. CLI

```bash
# Set up browser for web scraping
virginia-clemm-poe setup

# Update model data with pricing information
POE_API_KEY=your_key virginia-clemm-poe update --pricing

# Update all model data
POE_API_KEY=your_key virginia-clemm-poe update --all

# Search for models
virginia-clemm-poe search "gpt-4"
```

## 5. Data Structure

Model data includes:
- Basic model information (ID, name, capabilities)
- Detailed pricing structure:
  - Input costs (text and image)
  - Bot message costs
  - Chat history pricing
  - Cache discount information
- Timestamps for data freshness

## 6. Requirements

- Python 3.12+
- Chrome or Chromium browser (automatically managed by PlaywrightAuthor)
- Poe API key (set as `POE_API_KEY` environment variable)

## 7. Development

This package uses:
- `uv` for dependency management
- `httpx` for API requests
- `playwrightauthor` for browser automation (external package)
- `pydantic` for data models
- `fire` for CLI interface
- `rich` for terminal UI
- `loguru` for logging

# OLD CODE

```bash
# Update models without existing pricing data
POE_API_KEY=your_key ./old/poe_models_updater.py

# Force update all models (including those with pricing)
POE_API_KEY=your_key ./old/poe_models_updater.py --force

# Use custom output file
POE_API_KEY=your_key ./old/poe_models_updater.py --output custom_models.json

# Enable verbose logging
POE_API_KEY=your_key ./old/poe_models_updater.py --verbose
```


1. **Chrome/Chromium Required**: The scraper requires Chrome or Chromium to be installed for web scraping via Chrome DevTools Protocol (CDP). This is now handled automatically by PlaywrightAuthor.

2. **API Key**: Requires a Poe API key set as `POE_API_KEY` environment variable.

3. **File Locations**: The old code is currently in the `old/` folder

4. **PlaywrightAuthor**: This package now uses the external PlaywrightAuthor package located at `external/playwrightauthor/` for all browser management functionality.

# Software Development Rules

## 8. Pre-Work Preparation

### 8.1. Before Starting Any Work
- **ALWAYS** read `WORK.md` in the main project folder for work progress
- Read `README.md` to understand the project
- STEP BACK and THINK HEAVILY STEP BY STEP about the task
- Consider alternatives and carefully choose the best option
- Check for existing solutions in the codebase before starting

### 8.2. Project Documentation to Maintain
- `README.md` - purpose and functionality
- `CHANGELOG.md` - past change release notes (accumulative)
- `PLAN.md` - detailed future goals, clear plan that discusses specifics
- `TODO.md` - flat simplified itemized `- [ ]`-prefixed representation of `PLAN.md`
- `WORK.md` - work progress updates

## 9. General Coding Principles

### 9.1. Core Development Approach
- Iterate gradually, avoiding major changes
- Focus on minimal viable increments and ship early
- Minimize confirmations and checks
- Preserve existing code/structure unless necessary
- Check often the coherence of the code you're writing with the rest of the code
- Analyze code line-by-line

### 9.2. Code Quality Standards
- Use constants over magic numbers
- Write explanatory docstrings/comments that explain what and WHY
- Explain where and how the code is used/referred to elsewhere
- Handle failures gracefully with retries, fallbacks, user guidance
- Address edge cases, validate assumptions, catch errors early
- Let the computer do the work, minimize user decisions
- Reduce cognitive load, beautify code
- Modularize repeated logic into concise, single-purpose functions
- Favor flat over nested structures

## 10. Tool Usage (When Available)

### 10.1. Additional Tools
- If we need a new Python project, run `curl -LsSf https://astral.sh/uv/install.sh | sh; uv venv --python 3.12; uv init; uv add fire rich; uv sync`
- Use `tree` CLI app if available to verify file locations
- Check existing code with `.venv` folder to scan and consult dependency source code
- Run `DIR="."; uvx codetoprompt --compress --output "$DIR/llms.txt"  --respect-gitignore --cxml --exclude "*.svg,.specstory,*.md,*.txt,ref,testdata,*.lock,*.svg" "$DIR"` to get a condensed snapshot of the codebase into `llms.txt`

## 11. File Management

### 11.1. File Path Tracking
- **MANDATORY**: In every source file, maintain a `this_file` record showing the path relative to project root
- Place `this_file` record near the top:
- As a comment after shebangs in code files
- In YAML frontmatter for Markdown files
- Update paths when moving files
- Omit leading `./`
- Check `this_file` to confirm you're editing the right file

## 12. Python-Specific Guidelines

### 12.1. PEP Standards
- PEP 8: Use consistent formatting and naming, clear descriptive names
- PEP 20: Keep code simple and explicit, prioritize readability over cleverness
- PEP 257: Write clear, imperative docstrings
- Use type hints in their simplest form (list, dict, | for unions)

### 12.2. Modern Python Practices
- Use f-strings and structural pattern matching where appropriate
- Write modern code with `pathlib`
- ALWAYS add "verbose" mode loguru-based logging & debug-log
- Use `uv add` 
- Use `uv pip install` instead of `pip install`
- Prefix Python CLI tools with `python -m` (e.g., `python -m pytest`)

### 12.3. CLI Scripts Setup
For CLI Python scripts, use `fire` & `rich`, and start with:
```python
#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["PKG1", "PKG2"]
# ///
# this_file: PATH_TO_CURRENT_FILE
```

### 12.4. Post-Edit Python Commands
```bash
fd -e py -x uvx autoflake -i {}; fd -e py -x uvx pyupgrade --py312-plus {}; fd -e py -x uvx ruff check --output-format=github --fix --unsafe-fixes {}; fd -e py -x uvx ruff format --respect-gitignore --target-version py312 {}; python -m pytest;
```

## 13. Post-Work Activities

### 13.1. Critical Reflection
- After completing a step, say "Wait, but" and do additional careful critical reasoning
- Go back, think & reflect, revise & improve what you've done
- Don't invent functionality freely
- Stick to the goal of "minimal viable next version"

### 13.2. Documentation Updates
- Update `WORK.md` with what you've done and what needs to be done next
- Document all changes in `CHANGELOG.md`
- Update `TODO.md` and `PLAN.md` accordingly

## 14. Work Methodology

### 14.1. Virtual Team Approach
Be creative, diligent, critical, relentless & funny! Lead two experts:
- **"Ideot"** - for creative, unorthodox ideas
- **"Critin"** - to critique flawed thinking and moderate for balanced discussions

Collaborate step-by-step, sharing thoughts and adapting. If errors are found, step back and focus on accuracy and progress.

### 14.2. Continuous Work Mode
- Treat all items in `PLAN.md` and `TODO.md` as one huge TASK
- Work on implementing the next item
- Review, reflect, refine, revise your implementation
- Periodically check off completed issues
- Continue to the next item without interruption

## 15. Special Commands

### 15.1. `/plan` Command - Transform Requirements into Detailed Plans

When I say "/plan [requirement]", you must:

1. **DECONSTRUCT** the requirement:
- Extract core intent, key features, and objectives
- Identify technical requirements and constraints
- Map what's explicitly stated vs. what's implied
- Determine success criteria

2. **DIAGNOSE** the project needs:
- Audit for missing specifications
- Check technical feasibility
- Assess complexity and dependencies
- Identify potential challenges

3. **RESEARCH** additional material: 
- Repeatedly call the `perplexity_ask` and request up-to-date information or additional remote context
- Repeatedly call the `context7` tool and request up-to-date software package documentation
- Repeatedly call the `codex` tool and request additional reasoning, summarization of files and second opinion

4. **DEVELOP** the plan structure:
- Break down into logical phases/milestones
- Create hierarchical task decomposition
- Assign priorities and dependencies
- Add implementation details and technical specs
- Include edge cases and error handling
- Define testing and validation steps

5. **DELIVER** to `PLAN.md`:
- Write a comprehensive, detailed plan with:
 - Project overview and objectives
 - Technical architecture decisions
 - Phase-by-phase breakdown
 - Specific implementation steps
 - Testing and validation criteria
 - Future considerations
- Simultaneously create/update `TODO.md` with the flat itemized `- [ ]` representation

**Plan Optimization Techniques:**
- **Task Decomposition:** Break complex requirements into atomic, actionable tasks
- **Dependency Mapping:** Identify and document task dependencies
- **Risk Assessment:** Include potential blockers and mitigation strategies
- **Progressive Enhancement:** Start with MVP, then layer improvements
- **Technical Specifications:** Include specific technologies, patterns, and approaches

### 15.2. `/report` Command

1. Read all `./TODO.md` and `./PLAN.md` files
2. Analyze recent changes
3. Document all changes in `./CHANGELOG.md`
4. Remove completed items from `./TODO.md` and `./PLAN.md`
5. Ensure `./PLAN.md` contains detailed, clear plans with specifics
6. Ensure `./TODO.md` is a flat simplified itemized representation

### 15.3. `/work` Command

1. Read all `./TODO.md` and `./PLAN.md` files and reflect
2. Write down the immediate items in this iteration into `./WORK.md`
3. Work on these items
4. Think, contemplate, research, reflect, refine, revise
5. Be careful, curious, vigilant, energetic
6. Verify your changes and think aloud
7. Consult, research, reflect
8. Periodically remove completed items from `./WORK.md`
9. Tick off completed items from `./TODO.md` and `./PLAN.md`
10. Update `./WORK.md` with improvement tasks
11. Execute `/report`
12. Continue to the next item

## 16. Additional Guidelines

- Ask before extending/refactoring existing code that may add complexity or break things
- Work tirelessly without constant updates when in continuous work mode
- Only notify when you've completed all `PLAN.md` and `TODO.md` items

## 17. Command Summary

- `/plan [requirement]` - Transform vague requirements into detailed `PLAN.md` and `TODO.md`
- `/report` - Update documentation and clean up completed tasks
- `/work` - Enter continuous work mode to implement plans
- You may use these commands autonomously when appropriate

**TLDR: `virginia-clemm-poe`**

This repository contains the source code for `virginia-clemm-poe`, a Python package designed to provide programmatic access to a comprehensive dataset of AI models available on Poe.com. Its primary function is to act as a companion tool to the official Poe API by fetching, maintaining, and enriching model data, with a special focus on scraping and storing detailed pricing information, which is not available through the API alone.

**Core Functionality:**

1.  **Data Aggregation:** It fetches the list of all available models from the Poe.com API.
2.  **Web Scraping:** It uses `playwright` to control a headless Chrome/Chromium browser to navigate to each model's page on Poe.com and scrape detailed information that isn't in the API response. This includes:
    *   **Pricing Data:** Captures the cost for various operations (e.g., per-message, text input, image input).
    *   **Bot Metadata:** Extracts the bot's creator, description, and other descriptive text.
3.  **Local Dataset:** It stores this aggregated and scraped data in a local JSON file (`src/virginia_clemm_poe/data/poe_models.json`). This allows the package's API to provide instant access to the data without needing to perform network requests for every query.
4.  **Data Access:** It provides two primary ways for users to interact with the data:
    *   A **Python API** (`api.py`) for developers to programmatically search, filter, and retrieve model information within their own applications.
    *   A **Command-Line Interface (CLI)** (`__main__.py`) for end-users to easily update the local dataset, search for models, and list model information directly from the terminal.

**Technical Architecture:**

*   **Language:** Python 3.12+
*   **Data Modeling:** `pydantic` is used extensively in `models.py` to define strongly-typed and validated data structures for models, pricing, and bot information (`PoeModel`, `Pricing`, `BotInfo`).
*   **HTTP Requests:** `httpx` is used for efficient asynchronous communication with the Poe API.
*   **Web Scraping:** `playwright` automates the browser to handle dynamic web content and extract data from the Poe website. `browser_manager.py` handles the setup and management of the browser instance.
*   **CLI:** `python-fire` is used to create the user-friendly command-line interface from the methods in the `updater.py` and `api.py` modules.
*   **UI/Output:** `rich` is used to provide formatted and colorized output in the terminal, enhancing readability.
*   **Dependency Management:** The project uses `uv` for fast and modern package management, configured in `pyproject.toml`.
*   **Logging:** `loguru` provides flexible and powerful logging.

**Key Modules:**

*   `src/virginia_clemm_poe/api.py`: The main entry point for the Python API. Provides functions like `search_models()`, `get_model_by_id()`, etc.
*   `src/virginia_cĺemm_poe/updater.py`: Contains the core logic for updating the model database. It orchestrates fetching data from the API, scraping the website, and saving the results.
*   `src/virginia_clemm_poe/models.py`: Defines the Pydantic models that structure the entire dataset.
*   `src/virginia_clemm_poe/__main__.py`: The entry point that exposes the functionality to the command line via `fire`.
*   `src/virginia_clemm_poe/browser_manager.py`: Manages the lifecycle of the Playwright browser used for scraping.
*   `src/virginia_clemm_poe/data/poe_models.json`: The canonical, version-controlled dataset that the package reads from.
