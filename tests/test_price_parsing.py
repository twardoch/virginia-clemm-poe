# this_file: tests/test_price_parsing.py
"""Evidence-based normalization across Poe rate-card formats."""

import json
from decimal import Decimal
from pathlib import Path

import pytest

from virginia_clemm_poe.pricing import parse_price_text, parse_rate_card, parse_rate_tables


@pytest.mark.parametrize(
    "text,currency,amount,quantity,unit",
    [
        ("$2.02/1M tokens", "usd", "2.02", "1000000", "tokens"),
        ("67 points/1k tokens", "points", "67", "1000", "tokens"),
        ("$1.2e-6/token", "usd", "0.0000012", "1", "tokens"),
        ("1,750 points/message", "points", "1750", "1", "message"),
        ("$0.00/message", "usd", "0", "1", "message"),
        ("0 points/message", "points", "0", "1", "message"),
        ("850 points ($0.026) / megapixel", "usd", "0.026", "1", "megapixel"),
        ("[usd_milli_cents=1000] points / 1k characters", "usd", "0.01", "1000", "characters"),
        ("3334 ($0.10) / 1000 characters", "points", "3334", "1000", "characters"),
        ("60000 points ($1.82) / million video tokens", "points", "60000", "1000000", "tokens"),
    ],
)
def test_price_text_retains_currency_decimal_and_unit(text, currency, amount, quantity, unit):
    rate = next(r for r in parse_price_text("Total cost", text) if r.currency == currency)
    assert rate.amount == Decimal(amount) and rate.quantity == Decimal(quantity), (
        "Amounts and denominators must remain exact"
    )
    assert rate.unit == unit, "Token, media, and flat units must remain distinct"


def test_ranges_and_minimum_prices_are_not_exact_prices():
    rate = parse_price_text("Image Output", "$0.10–$0.25/image")[0]
    assert rate.amount == Decimal("0.10") and rate.maximum == Decimal("0.25"), "Ranges must retain their bounds"
    assert rate.lower_bound, "A range minimum must not appear as an exact charge"
    assert parse_price_text("Initial cost", "100+ points")[0].lower_bound, "Plus indicates a starting cost"


@pytest.mark.parametrize(
    "text", ["90% discount on cached chat", "No rate available", "", "Free trial for a limited time"]
)
def test_non_price_text_does_not_become_a_zero_price(text):
    assert parse_price_text("Output", text) == [], "Discounts, missing values, and marketing claims are not prices"


def test_multi_table_rates_keep_input_output_base_fee_and_both_currencies():
    html = (
        "<table><tr><th>Type</th><th>USD</th><th>Points</th></tr>"
        "<tr><td>Input</td><td>$2/1M tokens</td><td>67 points/1k tokens</td></tr>"
        "<tr><td>Output (text)</td><td>$10/1M tokens</td><td>334 points/1k tokens</td></tr></table>"
        "<table><tr><td>Bot message</td><td>$0.05/message</td><td>1,650 points/message</td></tr></table>"
    )
    result = parse_rate_tables(html)
    assert len(result["rates"]) == 6, "All tables and both currencies must survive extraction"
    assert result["Input (text)"] == ["$2/1M tokens", "67 points/1k tokens"], "Token input maps to the typed field"
    assert "Output (text)" in result, "Output token prices must not be ignored"


def test_markdown_rate_card_recovers_missing_rendered_table():
    result = parse_rate_card(
        "Cost overview:\n\n| Service | Rate |\n|---|---|\n| Image Output | 850 points ($0.026) / megapixel |"
    )
    assert len(result["rates"]) == 2, "A raw rate card must recover prices when UI rendering fails"
    assert result["rates"][0]["source"] == "rate_card", "Fallback provenance must be explicit"


def test_prose_script_rates_are_lower_bounds_and_promotional_points_are_excluded():
    result = parse_rate_card(
        "First 12,500 points of generations are free!\n"
        "Interpreter costs 1 point per message, plus the rates of any other bots it calls."
    )
    assert len(result["rates"]) == 1, "A temporary allowance must not become a service charge"
    assert result["rates"][0]["amount"] == "1" and result["rates"][0]["lower_bound"], (
        "Chained bot calls make the base fee a lower bound"
    )


def test_quality_matrix_prices_are_images_and_struck_out_prices_are_ignored():
    result = parse_rate_tables(
        "<table><tr><th>Size / Quality</th><th>1:1</th></tr>"
        "<tr><td>low</td><td><del>$0.02</del>328 points ($0.0098)</td></tr></table>"
    )
    assert len(result["rates"]) == 2, "Obsolete prices must not be used"
    assert all(r["unit"] == "image" for r in result["rates"]), "Matrix prices describe output images"


def test_label_denominators_and_positive_exponents_are_preserved():
    assert parse_price_text("5 seconds", "$3")[0].quantity == 5, "A five-second clip is not a one-second price"
    assert parse_price_text("Per 1,000 words scanned", "20 points")[0].quantity == 1000, "Label denominators matter"
    assert not parse_price_text("Total cost", "$1e+2/message")[0].lower_bound, (
        "Positive exponents are not minimum markers"
    )


def test_video_duration_and_cost_per_second_headers_define_denominators():
    result = parse_rate_card("| Resolution | Duration | Points |\n|---|---|---|\n| 720p | 5s | 100 ($0.003) |")
    assert all(r["unit"] == "second" and r["quantity"] == "5" for r in result["rates"]), (
        "Video duration column defines rate denominator"
    )
    result = parse_rate_card("| Resolution | Cost/Second |\n|---|---|\n| 480p | 1910 ($0.058) |")
    assert all(r["unit"] == "second" for r in result["rates"]), "Column heading must preserve per-second billing"


def test_every_observed_rate_card_retains_the_catalogue_coverage():
    folder = Path(__file__).resolve().parents[1] / "issues/330-pricing-evidence"
    evidence = list(folder.glob("*.json"))
    assert len(evidence) == 501, "The dated fixture covers every bot"
    known = 0
    for path in evidence:
        row = json.loads(path.read_text())
        parsed = parse_rate_tables("".join(row.get("tables", [])))
        if not parsed:
            for card in row.get("rate_cards", []):
                parsed.update(parse_rate_card(card.get("rateMenuMarkdown", "")))
        known += bool(parsed.get("rates"))
    assert known == 483, "The parser must recover every disclosed rate in the full dated snapshot"


def test_cards_without_blank_lines_and_duration_sections_keep_their_units():
    result = parse_rate_card(
        "Cost overview:\n| Service | Rate |\n|---|---|\n| Image Output | 85 points ($0.0026) / message |"
    )
    assert all(r["label"] == "Image Output" for r in result["rates"]), (
        "Missing blank lines must not discard service labels"
    )
    result = parse_rate_card("**10 seconds:**\n\n| Resolution | Cost |\n|---|---|\n| 720p | 100 ($0.003) |")
    assert all(r["unit"] == "second" and r["quantity"] == "10" for r in result["rates"]), (
        "Duration headings apply to the following table"
    )
