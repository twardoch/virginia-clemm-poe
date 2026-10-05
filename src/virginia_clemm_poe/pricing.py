# this_file: src/virginia_clemm_poe/pricing.py
"""Normalize explicit Poe prices while preserving currency, units, and provenance."""

import re
from decimal import Decimal
from typing import Literal

import markdown
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

NUMBER = r"\d+(?:,\d{3})*(?:\.\d+)?(?:[eE][+-]?\d+)?"
USD_PATTERN = re.compile(rf"\$\s*({NUMBER})(?:\s*[-–]\s*\$?\s*({NUMBER}))?")
POINT_PATTERN = re.compile(rf"({NUMBER})(?:\s*[-–]\s*({NUMBER}))?\s*\+?\s*(?:points?|pts?)\b", re.IGNORECASE)
UNIT_PATTERN = re.compile(
    r"(?:/|\bper\s+)\s*(?:(\d+(?:,\d{3})*(?:\.\d+)?\s*[kKmM]?)\s*)?([a-z][a-z -]*)", re.IGNORECASE
)
USD_MILLI_CENTS = Decimal(100000)


class PriceRate(BaseModel):
    """One disclosed rate; quantity describes the denominator, not the amount."""

    label: str
    currency: Literal["usd", "points"]
    amount: Decimal = Field(ge=0)
    maximum: Decimal | None = None
    quantity: Decimal = Field(default=Decimal(1), gt=0)
    unit: str
    lower_bound: bool = False
    raw: str
    source: str = "table"


def price_unit(label: str, text: str) -> tuple[Decimal, str]:
    """Read scale and unit from an explicit denominator or a rate-row label."""
    text = re.sub(r"\bmillion\b", "1000000", text, flags=re.IGNORECASE)
    text = re.sub(r"\bthousand\b", "1000", text, flags=re.IGNORECASE)
    match = UNIT_PATTERN.search(text) or UNIT_PATTERN.search(label)
    if not match and re.match(r"^\d+\s+(seconds?|minutes?|images?)$", label, re.IGNORECASE):
        match = UNIT_PATTERN.search("/ " + label)
    quantity = (match[1] or "1").replace(" ", "").replace(",", "") if match else "1"
    scale = Decimal(1000) if quantity.lower().endswith("k") else Decimal(1)
    if quantity.lower().endswith("m"):
        scale = Decimal(1000000)
    denominator = Decimal(quantity.rstrip("kKmM")) * scale
    name = match[2].strip().lower() if match else label.lower()
    name = {"s": "second", "sec": "second", "secs": "second", "img": "image", "chars": "characters"}.get(name, name)
    for word, unit in [
        ("token", "tokens"),
        ("character", "characters"),
        ("megapixel", "megapixel"),
        ("image", "image"),
        ("second", "second"),
        ("minute", "minute"),
        ("search", "search"),
    ]:
        if word in name:
            return denominator, unit
    if any(word in name for word in ("message", "total cost", "initial cost", "request")):
        return denominator, "message"
    return denominator, name or "unit"


def parse_price_text(label: str, text: str, source: str = "table") -> list[PriceRate]:
    """Parse dollars, points, scientific notation, ranges, and official milli-cent markers."""
    normalized = text.replace("\u00a0", " ").replace("\u202f", " ")
    normalized = re.sub(r"\[usd_milli_cents=(\d+)\]", lambda m: "$" + str(Decimal(m[1]) / USD_MILLI_CENTS), normalized)
    # Poe also writes point amounts as `3334 ($0.10)` without the word points.
    normalized = re.sub(rf"({NUMBER})\s*\(\s*\$", r"\1 points ($", normalized)
    quantity, unit = price_unit(label, normalized)
    rates = []
    for currency, pattern in [("usd", USD_PATTERN), ("points", POINT_PATTERN)]:
        for match in pattern.finditer(normalized):
            amount = Decimal(match[1].replace(",", ""))
            maximum = Decimal(match[2].replace(",", "")) if match[2] else None
            rates.append(
                PriceRate(
                    label=label,
                    currency=currency,
                    amount=amount,
                    maximum=maximum,
                    quantity=quantity,
                    unit=unit,
                    lower_bound=bool(
                        maximum is not None
                        or re.search(r"\d\s*\+", normalized)
                        or re.search(r"\bfrom\b", normalized, re.IGNORECASE)
                    ),
                    raw=text,
                    source=source,
                )
            )
    return rates


def parse_rate_tables(html: str, source: str = "table") -> dict:
    """Read every table and retain both raw values and normalized rates, excluding discounts."""
    soup = BeautifulSoup(html, "html.parser")
    for obsolete in soup.select("del, s, strike"):
        obsolete.decompose()
    data, rates = {}, []
    for row in soup.select("table tr, [role=table] [role=row]"):
        cells = row.find_all(["td", "th"], recursive=False) or row.select("[role=cell], [role=columnheader]")
        if len(cells) < 2 or all(cell.name == "th" or cell.get("role") == "columnheader" for cell in cells):
            continue
        label = " ".join(cells[0].get_text(" ", strip=True).split())
        if "discount" in label.lower():
            continue
        values = [cell.get_text(" ", strip=True) for cell in cells[1:]]
        parsed = [rate for value in values for rate in parse_price_text(label, value, source)]
        table = row.find_parent("table")
        headers = [cell.get_text(" ", strip=True) for cell in table.select("tr:first-child th")] if table else []
        preceding = table.find_previous_sibling() if table else None
        context = preceding.get_text(" ", strip=True) if preceding else ""
        duration_context = re.fullmatch(r"(\d+(?:\.\d+)?)\s*seconds?:?", context, re.IGNORECASE)
        if any("duration" in header.lower() for header in headers):
            duration = values[headers.index(next(h for h in headers if "duration" in h.lower())) - 1]
            match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*s", duration)
            if match:
                for rate in parsed:
                    rate.label = f"Video Output ({label}; {duration})"
                    rate.unit, rate.quantity = "second", Decimal(match[1])
        elif any(re.search(r"(?:/|per)\s*(?:video\s+)?second", h, re.IGNORECASE) for h in headers):
            for rate in parsed:
                rate.label, rate.unit = f"Video Output ({label})", "second"
        elif duration_context:
            for rate in parsed:
                rate.label = f"Video Output ({label}; {context})"
                rate.unit, rate.quantity = "second", Decimal(duration_context[1])
        if table and re.search(r"size\s*/?\s*quality", table.get_text(" ", strip=True), re.IGNORECASE):
            headers = [" ".join(cell.get_text(" ", strip=True).split()) for cell in table.select("thead th")]
            parsed = []
            for index, value in enumerate(values, 1):
                for rate in parse_price_text(label, value, source):
                    rate.unit = "image"
                    resolution = headers[index] if index < len(headers) else f"column {index}"
                    rate.label = f"Image Output ({label}; {resolution})"
                    parsed.append(rate)
        if not parsed:
            continue
        key = "Input (text)" if label.lower() == "input" and any(r.unit == "tokens" for r in parsed) else label
        if key.lower() == "output" and any(r.unit == "tokens" for r in parsed):
            key = "Output (text)"
        data[key] = values[0] if len(values) == 1 else values
        rates.extend(rate.model_dump(mode="json") for rate in parsed)
    if rates:
        data["rates"] = rates
    return data


def parse_rate_card(text: str) -> dict:
    """Use Python-Markdown's table extension for Poe's raw structured rate-card fallback."""
    # Poe often omits Markdown's required blank line between prose and a table.
    text = re.sub(r"(?m)^([^\n|][^\n]*)\n(?=\|)", r"\1\n\n", text)
    data = parse_rate_tables(markdown.markdown(text, extensions=["tables"]), source="rate_card")
    if data:
        return data
    rates = []
    section = "Message cost"
    for line in text.splitlines():
        clean = BeautifulSoup(markdown.markdown(line), "html.parser").get_text(" ", strip=True)
        if not clean or re.search(r"\b(free|trial|discount)\b", clean, re.IGNORECASE):
            continue
        if clean.endswith(":"):
            section = clean.rstrip(":").title()
        parsed = parse_price_text(section, clean, source="rate_card_text")
        for rate in parsed:
            if "plus the rates" in clean or "additional costs" in text:
                rate.lower_bound = True
            if section == "Images" and rate.unit == "images":
                rate.unit = "image"
        if parsed:
            data[section] = clean
            rates.extend(rate.model_dump(mode="json") for rate in parsed)
    if rates:
        data["rates"] = rates
    return data
