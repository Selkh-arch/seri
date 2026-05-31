"""
seri.tiers
==========

The six operational ecological tiers of SERI (Table 1 of the manuscript).

The tier boundaries are calibrated against field observations across the
El Bayadh - Bechar/Abadla - Timimoun-North transect, 2013-2024. They are
regionally specific to the northern Algerian Sahara; transfer to other
hyper-arid systems requires regional re-calibration (see manuscript
section 6.2).
"""

from __future__ import annotations

from enum import Enum
from typing import List, Tuple


class Tier(Enum):
    """
    Six operational ecological tiers.

    The numerical ``value`` carried by each member is its lower bound
    (inclusive), so the tier of a SERI score can also be inspected via
    :func:`seri.tiers.classify`.
    """

    INERT = 0
    MICROBIAL = 100
    ANNUAL = 500
    PERENNIAL = 2000
    WADI = 5000
    REGIONAL = 15000

    @property
    def label(self) -> str:
        return _TIER_LABELS[self]

    @property
    def description(self) -> str:
        return _TIER_DESCRIPTIONS[self]

    @property
    def lower_bound(self) -> float:
        return float(self.value)

    @property
    def upper_bound(self) -> float:
        """Upper bound (exclusive). ``inf`` for the top tier."""
        return _TIER_UPPER_BOUNDS[self]


_TIER_LABELS = {
    Tier.INERT: "Ecologically inert",
    Tier.MICROBIAL: "Microbial activation",
    Tier.ANNUAL: "Annual germination",
    Tier.PERENNIAL: "Perennial response",
    Tier.WADI: "Wadi activation",
    Tier.REGIONAL: "Regional recharge",
}

_TIER_DESCRIPTIONS = {
    Tier.INERT: (
        "No measurable response; event dissipates by evaporation."
    ),
    Tier.MICROBIAL: (
        "Ephemeral biological soil-crust activation; "
        "no vascular plant signal."
    ),
    Tier.ANNUAL: (
        "Germination of therophytes and short-lived ephemerals; "
        "transient NDVI bump."
    ),
    Tier.PERENNIAL: (
        "Leaf-flush of established perennials; "
        "sustained NDVI anomaly 30-90 days."
    ),
    Tier.WADI: (
        "Ephemeral flow in primary wadis; recharge of shallow aquifers; "
        "multi-month vegetation response."
    ),
    Tier.REGIONAL: (
        "Exceptional event; significant deep-aquifer recharge; "
        "multi-year vegetation memory."
    ),
}

_TIER_UPPER_BOUNDS = {
    Tier.INERT: 100.0,
    Tier.MICROBIAL: 500.0,
    Tier.ANNUAL: 2000.0,
    Tier.PERENNIAL: 5000.0,
    Tier.WADI: 15000.0,
    Tier.REGIONAL: float("inf"),
}


# Ordered list of tiers from lowest to highest, used for the bisect-style
# classification below.
_ORDERED_TIERS: List[Tier] = sorted(Tier, key=lambda t: t.value)


def classify(seri_value: float) -> Tier:
    """
    Return the operational tier corresponding to a numerical SERI value.

    The convention is:
        * SERI <  100   -> INERT
        * SERI <  500   -> MICROBIAL
        * SERI <  2000  -> ANNUAL
        * SERI <  5000  -> PERENNIAL
        * SERI <  15000 -> WADI
        * SERI >= 15000 -> REGIONAL

    Negative values are not physically meaningful and raise ValueError.

    Examples
    --------
    >>> classify(2353).name
    'PERENNIAL'
    >>> classify(0).name
    'INERT'
    >>> classify(99.9).name
    'INERT'
    >>> classify(100).name
    'MICROBIAL'
    """
    if seri_value < 0:
        raise ValueError(
            f"SERI value must be non-negative; got {seri_value!r}."
        )

    # Walk down from the top tier so the first match wins.
    for tier in reversed(_ORDERED_TIERS):
        if seri_value >= tier.value:
            return tier
    # Fallback (cannot actually happen because INERT.value == 0).
    return Tier.INERT


def tier_table() -> List[Tuple[str, float, float, str]]:
    """
    Return the full tier table as a list of tuples.

    Each row is ``(tier_name, lower_bound, upper_bound, label)``.
    Useful for printing or for embedding in plots / reports.
    """
    rows = []
    for t in _ORDERED_TIERS:
        rows.append((t.name, t.lower_bound, t.upper_bound, t.label))
    return rows
