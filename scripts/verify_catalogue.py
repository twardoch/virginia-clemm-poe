#!/usr/bin/env -S uv run
# this_file: scripts/verify_catalogue.py
"""Verify the generated catalogue locally or after publication, without Poe calls."""

import json
from pathlib import Path

import fire
from playwright.sync_api import sync_playwright


def verify(url: str = "http://127.0.0.1:8765", output: str = "/tmp/poe-catalogue-verification.json") -> None:
    """Check rendered content, all filters, themes, responsive width and page errors."""
    errors = []
    report = {"url": url, "checks": []}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page(viewport={"width": 1600, "height": 1000})
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(url.rstrip("/") + "/models/index.html", wait_until="networkidle")
        frame = page.frame_locator(".poe-catalogue")
        frame.locator("tbody tr").first.wait_for()
        data = page.request.get(url.rstrip("/") + "/data/poe_bots.json").json()
        models = data["data"]
        assert len(models) == 501, "Saved catalogue must contain every bot"
        assert frame.locator("tbody tr").count() == len(models), "All models must render"
        assert page.locator("fontlab-menu, fontlab-footer").count() == 0, "FontLab chrome must be absent"
        assert not page.locator(".md-sidebar--secondary").is_visible(), "Catalogue must not display a side ToC"
        assert page.locator("article h2, article h3").count() == 0, "Empty model headings must be removed"
        assert page.locator(".poe-model-links a").count() == 501, "Model links remain available"
        assert page.evaluate("Boolean(window.FLTheme)"), "Shared CDN theme must initialize"
        width = page.locator(".poe-catalogue").bounding_box()
        assert width["x"] + width["width"] >= 1570, "Table must reach the right page edge"
        report["checks"].append("501 models, shared theme without global chrome, wide iframe, no side ToC")
        inner = page.frames[1]
        assert inner.evaluate(
            "modelsData.every(m => JSON.stringify(m.point_estimate) === JSON.stringify(PoePrices.cost(m)) && m.pricing_tier === PoePrices.tier(m))"
        ), "Static and browser estimates/tiers must agree for every model"
        for value in range(10):
            frame.locator("#tierFilter").select_option(str(value))
            actual = frame.locator("tbody tr td:first-child a").all_text_contents()
            expected = [m["id"] for m in models if m["pricing_tier"] == value]
            assert sorted(actual) == sorted(expected), f"Tier {value} filter must match saved assignments"
        frame.locator("#tierFilter").select_option("")
        for selector, values, predicate in [
            (
                "#modalityFilter",
                sorted({v for m in models for v in m.get("architecture", {}).get("output_modalities", [])}),
                lambda m, v: v in m.get("architecture", {}).get("output_modalities", []),
            ),
            (
                "#creatorFilter",
                sorted(
                    {(m.get("bot_info") or {}).get("creator") or m.get("owned_by") or "Not disclosed" for m in models}
                ),
                lambda m, v: ((m.get("bot_info") or {}).get("creator") or m.get("owned_by") or "Not disclosed") == v,
            ),
        ]:
            for value in values:
                frame.locator(selector).select_option(value)
                actual = frame.locator("tbody tr td:first-child a").all_text_contents()
                assert sorted(actual) == sorted(m["id"] for m in models if predicate(m, value)), (
                    f"Filter {selector}={value} must match"
                )
            frame.locator(selector).select_option("")
        sample = next(m for m in models if m.get("architecture", {}).get("output_modalities"))
        modality = sample["architecture"]["output_modalities"][0]
        creator = (sample.get("bot_info") or {}).get("creator") or sample.get("owned_by") or "Not disclosed"
        frame.locator("#modalityFilter").select_option(modality)
        frame.locator("#creatorFilter").select_option(creator)
        frame.locator("#tierFilter").select_option(str(sample["pricing_tier"]))
        expected = [
            m["id"]
            for m in models
            if modality in m.get("architecture", {}).get("output_modalities", [])
            and ((m.get("bot_info") or {}).get("creator") or m.get("owned_by") or "Not disclosed") == creator
            and m["pricing_tier"] == sample["pricing_tier"]
        ]
        assert sorted(frame.locator("tbody tr td:first-child a").all_text_contents()) == sorted(expected), (
            "All three filters combine"
        )
        for selector in ["#modalityFilter", "#creatorFilter", "#tierFilter"]:
            frame.locator(selector).select_option("")
        frame.locator("#currencyFilter").select_option("usd")
        frame.locator("#currencyFilter").select_option("points")
        frame.locator("#searchInput").fill("DeepSeek")
        expected_search = [
            m["id"]
            for m in models
            if "deepseek"
            in (
                m["id"]
                + " "
                + str((m.get("bot_info") or {}).get("description") or "")
                + " "
                + str((m.get("bot_info") or {}).get("creator") or "")
            ).lower()
        ]
        assert sorted(frame.locator("tbody tr td:first-child a").all_text_contents()) == sorted(expected_search), (
            "Search must match IDs, descriptions and creators"
        )
        frame.locator("#searchInput").fill("")
        unknown = sum(m["point_estimate"]["amount"] is None for m in models)
        assert inner.evaluate("n => filteredData.slice(-n).every(m => PoePrices.cost(m).amount === null)", unknown), (
            "Unknowns stay last ascending"
        )
        inner.evaluate("handleSort('cost')")
        assert inner.evaluate("n => filteredData.slice(-n).every(m => PoePrices.cost(m).amount === null)", unknown), (
            "Unknowns stay last descending"
        )
        inner.evaluate("handleSort('cost')")
        report["checks"].append(
            "All ten tiers, all modalities, all creators, combined filters, search, currency and sorting"
        )
        page.locator('[data-md-component="palette"] label:visible').click()
        page.wait_for_function(
            "document.querySelector('.poe-catalogue').contentDocument.documentElement.getAttribute('data-md-color-scheme') === 'slate'"
        )
        assert inner.evaluate("getComputedStyle(document.body).backgroundColor") == "rgb(32, 32, 36)", (
            "Iframe follows parent dark mode"
        )
        page.screenshot(path=str(Path(output).with_suffix(".png")))
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), "Mobile page must not overflow"
        assert frame.locator("#tierFilter").is_visible(), "Mobile filters remain visible"
        page.locator('.md-header label[for="__drawer"]').click()
        assert page.locator("#__drawer").is_checked(), "Native mobile menu works"
        page.locator('label.md-overlay[for="__drawer"]').click(position={"x": 380, "y": 100})
        page.locator('.md-header__button[for="__search"]').click()
        assert page.locator("#__search").is_checked(), "Native local search works"
        page.keyboard.press("Escape")
        report["checks"].append("Dark-mode iframe sync, mobile width, native menu and search")
        assert not errors, f"Browser page errors: {errors}"
        report["conversion"] = data["point_conversion"]
        report["tier_counts"] = {str(t): sum(m["pricing_tier"] == t for m in models) for t in range(10)}
        report["page_errors"] = errors
        browser.close()
    Path(output).write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    fire.Fire(verify)
