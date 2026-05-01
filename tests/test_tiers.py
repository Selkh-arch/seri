"""Tests for seri.tiers."""

import pytest

from seri.tiers import Tier, classify, tier_table


# Boundary cases from Table 1 of the manuscript.
@pytest.mark.parametrize(
    "value, expected",
    [
        (0,        Tier.INERT),
        (50,       Tier.INERT),
        (99.99,    Tier.INERT),
        (100,      Tier.MICROBIAL),
        (250,      Tier.MICROBIAL),
        (499.99,   Tier.MICROBIAL),
        (500,      Tier.ANNUAL),
        (1500,     Tier.ANNUAL),
        (1999.99,  Tier.ANNUAL),
        (2000,     Tier.PERENNIAL),
        (2353,     Tier.PERENNIAL),  # Abadla anchor case
        (4999.99,  Tier.PERENNIAL),
        (5000,     Tier.WADI),
        (10000,    Tier.WADI),
        (14999.99, Tier.WADI),
        (15000,    Tier.REGIONAL),
        (50000,    Tier.REGIONAL),
        (1e6,      Tier.REGIONAL),
    ],
)
def test_classify_boundaries(value, expected):
    assert classify(value) is expected


def test_classify_negative_raises():
    with pytest.raises(ValueError):
        classify(-1)


def test_tier_labels_are_unique_and_human_readable():
    labels = [t.label for t in Tier]
    assert len(labels) == len(set(labels))
    for lbl in labels:
        # No empty labels, no all-uppercase labels.
        assert lbl
        assert lbl != lbl.upper()


def test_tier_descriptions_non_empty():
    for t in Tier:
        assert t.description.strip()


def test_tier_table_shape_and_order():
    rows = tier_table()
    assert len(rows) == 6
    # Lower bounds must be strictly increasing.
    lows = [r[1] for r in rows]
    assert lows == sorted(lows)
    assert lows == [0, 100, 500, 2000, 5000, 15000]


def test_upper_bound_of_top_tier_is_inf():
    assert Tier.REGIONAL.upper_bound == float("inf")
