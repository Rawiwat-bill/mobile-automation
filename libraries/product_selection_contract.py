"""Case-specific Product Selection category contract.

The helper intentionally evaluates only non-sensitive product-category labels.
It never accepts or logs account numbers and failure messages contain expected
category names only.
"""
from __future__ import annotations

import re
from collections.abc import Iterable


def _normalize(value: object) -> str:
    text = str(value).casefold().replace("–", "-").replace("—", "-")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text).split())


def _is_e_saving(value: str) -> bool:
    normalized = _normalize(value)
    compact = normalized.replace(" ", "")
    return "esaving" in compact or bool(re.search(r"\be\s+savings?\b", normalized))


def _is_plain_saving(value: str) -> bool:
    normalized = _normalize(value)
    return bool(re.search(r"\bsavings?\b", normalized)) and not _is_e_saving(value)


def _matches(actual: str, expected: str) -> bool:
    normalized_expected = _normalize(expected)
    compact_expected = normalized_expected.replace(" ", "")
    if compact_expected in {"esaving", "esavings", "esavingaccount", "esavingsaccount"}:
        return _is_e_saving(actual)
    if normalized_expected in {"saving", "savings", "saving account", "savings account"}:
        return _is_plain_saving(actual)
    return normalized_expected in _normalize(actual)


def validate_product_categories(
    actual_names: Iterable[object] | None,
    expected_categories: Iterable[object] | None,
) -> bool:
    """Fail unless every expected category is represented by the live UI labels."""
    expected = [str(value).strip() for value in (expected_categories or []) if str(value).strip()]
    if not expected:
        return True

    actual = [str(value).strip() for value in (actual_names or []) if str(value).strip()]
    missing = [category for category in expected if not any(_matches(name, category) for name in actual)]
    if missing:
        raise AssertionError(
            "PRODUCT_SELECTION_EXPECTED_CATEGORIES_MISSING=" + ",".join(missing)
        )
    return True
