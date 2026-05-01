"""
seri.coefficients
=================

Seasonal and substrate coefficients of SERI.

The seasonal coefficient ``f(season)`` captures the strong annual cycle
of evaporative demand on the Saharan margin (PET varies by ~4x between
January and July at Adrar).

The substrate coefficient ``g(substrate)`` captures infiltration / runoff
partitioning across the dominant geomorphic units of the Algerian Sahara
(Pouget 1980; Halitim 1988; Cantón et al. 2011).

Both coefficient families are dimensionless. The values are
regionally-specific to the northern Algerian Sahara and are intended for
joint refinement with alpha in the empirical calibration phase
(companion paper, Selkh in prep.).
"""

from __future__ import annotations

from typing import Mapping, Union

# ---------------------------------------------------------------------------
# Seasonal coefficient
# ---------------------------------------------------------------------------
# Manuscript section 3.4 / 4.3, piecewise-constant formulation.
# Continuous f(PET) = exp(-PET / PET_ref) is reserved for SERI-2 (section 6.4).

SEASON_COEFFICIENT = {
    "winter":   1.30,  # Oct, Nov, Dec, Jan, Feb, Mar
    "shoulder": 0.65,  # Apr, May, Sep
    "summer":   0.35,  # Jun, Jul, Aug
}

_MONTH_TO_SEASON = {
    1:  "winter", 2:  "winter", 3:  "winter",
    4:  "shoulder", 5: "shoulder",
    6:  "summer",  7: "summer",  8: "summer",
    9:  "shoulder",
    10: "winter", 11: "winter", 12: "winter",
}


def resolve_season_coefficient(season: Union[int, str]) -> float:
    """
    Return the seasonal coefficient ``f`` for a given month or season label.

    Parameters
    ----------
    season : int or str
        Either a month number (1-12) or one of ``'winter'``,
        ``'shoulder'``, ``'summer'``.

    Returns
    -------
    float
        The dimensionless seasonal coefficient.

    Examples
    --------
    >>> resolve_season_coefficient(2)
    1.3
    >>> resolve_season_coefficient('summer')
    0.35
    """
    if isinstance(season, str):
        key = season.strip().lower()
        if key not in SEASON_COEFFICIENT:
            raise ValueError(
                f"Unknown season label {season!r}. "
                f"Valid labels: {sorted(SEASON_COEFFICIENT)}."
            )
        return SEASON_COEFFICIENT[key]

    if isinstance(season, int):
        if season not in _MONTH_TO_SEASON:
            raise ValueError(
                f"Month must be in 1..12; got {season!r}."
            )
        return SEASON_COEFFICIENT[_MONTH_TO_SEASON[season]]

    raise TypeError(
        f"`season` must be an int (month) or a str (season label); "
        f"got {type(season).__name__}."
    )


# ---------------------------------------------------------------------------
# Substrate coefficient
# ---------------------------------------------------------------------------
# Manuscript section 3.3 / 4.4. Values informed by published infiltration /
# runoff measurements for North African arid soils.

SUBSTRATE_COEFFICIENT = {
    "hamada":      0.55,  # crusted plateau, low infiltration
    "reg":         0.85,  # desert pavement over sandy matrix
    "erg":         1.25,  # sandy dunes, high infiltration
    "wadi_bottom": 1.60,  # alluvial fines concentrating runoff
    "sebkha":      0.30,  # saline-evaporative depression
}

# ---------------------------------------------------------------------------
# Abadla 2015 mixed-substrate composition
# ---------------------------------------------------------------------------
# The Abadla 2015 anchor case (manuscript section 5.1) used an area-weighted
# mean substrate coefficient g = 1.10 over the IMERG footprint, dominated by
# desert pavement (reg) with a substantial alluvial-fines (wadi-bottom)
# component along the lower Saoura wadi axis. Solving algebraically:
#
#     1.10 = 0.85 * x + 1.60 * (1 - x)   =>   x = 2/3
#
# the implied composition is approximately 67 % reg + 33 % wadi-bottom,
# consistent with the proportions visible in the field photography of Fig. 1
# (alluvial wadi axes interspersed with reg surfaces).
#
# Exposing this composition explicitly (rather than hard-coding g = 1.10
# as an opaque "magic number") makes the derivation auditable: anyone can
# verify that g falls out of the documented composition, and the convenience
# label 'mixed' is no longer a bare scalar but a derived quantity.

ABADLA_MIXED_COMPOSITION: Mapping[str, float] = {
    "reg":         2.0 / 3.0,
    "wadi_bottom": 1.0 / 3.0,
}

# Convenience alias: the 'mixed' label is shorthand for the Abadla
# composition above. Numerically equal to 1.10 (manuscript section 5.1).
# New code is encouraged to pass an explicit area-weighted mapping for
# traceability, but the alias is retained for backward compatibility with
# v1.0.0 examples and tests.
SUBSTRATE_COEFFICIENT["mixed"] = (
    SUBSTRATE_COEFFICIENT["reg"] * ABADLA_MIXED_COMPOSITION["reg"]
    + SUBSTRATE_COEFFICIENT["wadi_bottom"] * ABADLA_MIXED_COMPOSITION["wadi_bottom"]
)

# Aliases tolerated for the wadi-bottom class (avoid hyphen / dash issues
# when users pass the label by hand).
_SUBSTRATE_ALIASES = {
    "wadi-bottom": "wadi_bottom",
    "wadibottom":  "wadi_bottom",
    "wadi":        "wadi_bottom",
}


def _normalise_substrate_key(key: str) -> str:
    k = key.strip().lower().replace(" ", "_")
    return _SUBSTRATE_ALIASES.get(k, k)


def resolve_substrate_coefficient(
    substrate: Union[str, Mapping[str, float]],
    *,
    fraction_tol: float = 1e-3,
) -> float:
    """
    Return the substrate coefficient ``g``.

    Two input modes are supported:

    1. A single label (``str``), e.g. ``'reg'`` or ``'wadi_bottom'``.
    2. A mapping ``{label: area_fraction}`` whose values sum to 1
       (within ``fraction_tol``). The returned coefficient is the
       area-weighted mean of the per-class coefficients - exactly the
       convention used in section 3.4 of the manuscript.

    Parameters
    ----------
    substrate : str or Mapping[str, float]
        See above.
    fraction_tol : float, optional
        Tolerance on the sum of fractions when ``substrate`` is a
        mapping. Default ``1e-3``.

    Returns
    -------
    float
        The dimensionless substrate coefficient.

    Examples
    --------
    >>> resolve_substrate_coefficient('reg')
    0.85
    >>> # half reg (0.85) + half wadi-bottom (1.60) = 1.225
    >>> round(resolve_substrate_coefficient({'reg': 0.5, 'wadi_bottom': 0.5}), 3)
    1.225
    """
    if isinstance(substrate, str):
        key = _normalise_substrate_key(substrate)
        if key not in SUBSTRATE_COEFFICIENT:
            raise ValueError(
                f"Unknown substrate label {substrate!r}. "
                f"Valid labels: {sorted(SUBSTRATE_COEFFICIENT)}."
            )
        return SUBSTRATE_COEFFICIENT[key]

    if isinstance(substrate, Mapping):
        if not substrate:
            raise ValueError("Substrate mapping is empty.")
        total = 0.0
        weighted = 0.0
        for raw_key, fraction in substrate.items():
            key = _normalise_substrate_key(raw_key)
            if key not in SUBSTRATE_COEFFICIENT:
                raise ValueError(
                    f"Unknown substrate label {raw_key!r} in mapping. "
                    f"Valid labels: {sorted(SUBSTRATE_COEFFICIENT)}."
                )
            if fraction < 0:
                raise ValueError(
                    f"Negative fraction {fraction!r} for substrate {raw_key!r}."
                )
            weighted += SUBSTRATE_COEFFICIENT[key] * fraction
            total += fraction
        if abs(total - 1.0) > fraction_tol:
            raise ValueError(
                f"Substrate fractions must sum to 1 (within {fraction_tol}); "
                f"got sum = {total:g}."
            )
        return weighted

    raise TypeError(
        f"`substrate` must be a str or a Mapping; "
        f"got {type(substrate).__name__}."
    )
