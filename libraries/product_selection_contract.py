"""Case-specific Product Selection category contract.

The helper intentionally evaluates only non-sensitive product-category labels.
It never accepts or logs account numbers and failure messages contain expected
category names only.
"""
from __future__ import annotations

import re
from collections.abc import Iterable


SUPPORTED_PRODUCT_CATEGORIES = ("Saving", "e-Saving")


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
    category_policy: str = "ALL",
) -> bool:
    """Validate the supported product category contract against live UI labels."""
    policy = str(category_policy or "ALL").strip().upper()
    if policy not in {"ALL", "ANY_SUPPORTED"}:
        raise ValueError("PRODUCT_SELECTION_CATEGORY_POLICY_INVALID=" + policy)

    expected = [str(value).strip() for value in (expected_categories or []) if str(value).strip()]
    actual = [str(value).strip() for value in (actual_names or []) if str(value).strip()]

    if policy == "ANY_SUPPORTED":
        supported = expected or list(SUPPORTED_PRODUCT_CATEGORIES)
        if any(
            any(_matches(name, category) for category in supported)
            for name in actual
        ):
            return True
        raise AssertionError(
            "PRODUCT_SELECTION_SUPPORTED_CATEGORIES_MISSING=" + ",".join(supported)
        )

    if not expected:
        return True

    missing = [category for category in expected if not any(_matches(name, category) for name in actual)]
    if missing:
        raise AssertionError(
            "PRODUCT_SELECTION_EXPECTED_CATEGORIES_MISSING=" + ",".join(missing)
        )
    return True
