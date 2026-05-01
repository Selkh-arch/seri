"""
seri.core
=========

Reference implementation of the Spatial Effective Rainfall Index (SERI).

The SERI of a single rainfall event is defined as:

    SERI = P * A**alpha * f(season) * g(substrate)

where
    P     : event mean intensity over the footprint (mm)
    A     : contiguous area receiving rainfall above the inclusion
            threshold (default 5 mm/day) (km^2)
    alpha : sub-linear exponent on the spatial term (dimensionless,
            default 0.68 for the northern Algerian Sahara, pending
            formal calibration; see Selkh, in prep.)
    f     : seasonal coefficient (dimensionless)
    g     : substrate coefficient (dimensionless)

Reference
---------
Selkh, C. (2026). A Century After De Martonne: Why Spatial Coherence
is the Missing Dimension of Aridity in the Hyper-Arid Sahara.
Earth-Science Reviews, in review.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Union

from .coefficients import resolve_season_coefficient, resolve_substrate_coefficient
from .tiers import Tier, classify

# Default value of the spatial exponent for the northern Algerian Sahara.
# This is a working value pending formal empirical calibration on the
# n ~ 150 event archive 2013-2024 (Selkh, in prep.). See manuscript v8.2,
# section 4.2.
DEFAULT_ALPHA: float = 0.68

# Inclusion threshold (mm/day) used by the area-detection pipeline.
# Independently corroborated by Sun et al. (2013).
DEFAULT_RAIN_THRESHOLD_MM_DAY: float = 5.0


@dataclass(frozen=True)
class SERIResult:
    """
    Result container for a single SERI computation.

    Attributes
    ----------
    value : float
        Numerical SERI score (dimensionless).
    tier : Tier
        Operational ecological tier (Table 1 of the manuscript).
    P : float
        Event mean intensity used in the calculation (mm).
    A : float
        Contiguous area used in the calculation (km^2).
    alpha : float
        Spatial exponent used.
    f : float
        Seasonal coefficient used.
    g : float
        Substrate coefficient used.
    """

    value: float
    tier: Tier
    P: float
    A: float
    alpha: float
    f: float
    g: float

    @property
    def tier_name(self) -> str:
        """Human-readable tier label, e.g. 'Perennial response'."""
        return self.tier.label

    @property
    def tier_description(self) -> str:
        """Short description of the typical biological response in this tier."""
        return self.tier.description

    def to_dict(self) -> dict:
        """Return a plain-dict representation, e.g. for JSON export."""
        return {
            "SERI": self.value,
            "tier": self.tier.name,
            "tier_label": self.tier.label,
            "tier_description": self.tier.description,
            "P_mm": self.P,
            "A_km2": self.A,
            "alpha": self.alpha,
            "f_season": self.f,
            "g_substrate": self.g,
        }

    def __repr__(self) -> str:
        return (
            f"SERIResult(value={self.value:.1f}, tier={self.tier.name}, "
            f"P={self.P:g} mm, A={self.A:g} km², α={self.alpha:g}, "
            f"f={self.f:g}, g={self.g:g})"
        )


def compute(
    P: float,
    A: float,
    season: Union[int, str],
    substrate: Union[str, Mapping[str, float]],
    alpha: float = DEFAULT_ALPHA,
) -> SERIResult:
    """
    Compute SERI for a single rainfall event.

    Parameters
    ----------
    P : float
        Event mean intensity over the footprint (mm). Must be >= 0.
    A : float
        Contiguous area receiving rainfall above the inclusion threshold
        (km^2). Must be >= 0.
    season : int or str
        Either a month number (1-12) or one of the season labels
        ``'winter'`` (Oct-Mar), ``'shoulder'`` (Apr-May, Sep) or
        ``'summer'`` (Jun-Aug).
    substrate : str or mapping
        Either a single substrate label (one of ``'hamada'``, ``'reg'``,
        ``'erg'``, ``'wadi_bottom'``, ``'sebkha'``, ``'mixed'``) or a
        mapping ``{label: area_fraction}`` whose values sum to 1.
        ``'mixed'`` is a convenience preset (g = 1.10) reflecting the
        reg + wadi-bottom mix used for the Abadla 2015 anchor case.
    alpha : float, optional
        Sub-linear spatial exponent. Defaults to 0.68 (working value for
        the northern Algerian Sahara pending formal calibration; see
        Selkh, in prep.). Must satisfy 0 < alpha <= 1.

    Returns
    -------
    SERIResult
        A frozen dataclass holding the value, its tier, and the
        coefficients used.

    Raises
    ------
    ValueError
        If any input is out of range or if a mapping does not sum to 1.

    Examples
    --------
    Reproduce the Abadla 2015 anchor case (manuscript section 5.1):

    >>> from seri import compute
    >>> r = compute(P=10.79, A=1624, season=2, substrate='mixed')
    >>> round(r.value)
    2352
    >>> r.tier_name
    'Perennial response'
    """
    # --- input validation ---------------------------------------------------
    if P < 0:
        raise ValueError(f"P (mean intensity) must be >= 0; got {P!r}.")
    if A < 0:
        raise ValueError(f"A (contiguous area) must be >= 0; got {A!r}.")
    if not (0 < alpha <= 1):
        raise ValueError(
            f"alpha must satisfy 0 < alpha <= 1 (sub-linear spatial term); "
            f"got {alpha!r}."
        )

    # --- coefficient resolution --------------------------------------------
    f = resolve_season_coefficient(season)
    g = resolve_substrate_coefficient(substrate)

    # --- formula -----------------------------------------------------------
    # Note: A**0 = 1 by convention; an event of A = 0 yields SERI = 0 below
    # because P is multiplied by A**alpha and the convention here is that
    # an empty footprint (no cell above threshold) means no event.
    if A == 0 or P == 0:
        value = 0.0
    else:
        value = P * (A ** alpha) * f * g

    return SERIResult(
        value=value,
        tier=classify(value),
        P=float(P),
        A=float(A),
        alpha=float(alpha),
        f=float(f),
        g=float(g),
    )


def compute_batch(events, alpha: float = DEFAULT_ALPHA):
    """
    Compute SERI for a batch of events.

    Parameters
    ----------
    events : iterable of mappings
        Each item must contain at least the keys ``P``, ``A``, ``season``
        and ``substrate``. Optional ``alpha`` overrides the global default
        for that event only.
    alpha : float, optional
        Default exponent applied when an event does not specify its own.

    Returns
    -------
    list of SERIResult
        One result per input event, in input order.

    Examples
    --------
    >>> events = [
    ...     {'P': 10.79, 'A': 1624, 'season': 2,  'substrate': 'mixed'},
    ...     {'P': 18.0,  'A': 51,   'season': 7,  'substrate': 'reg'},
    ... ]
    >>> results = compute_batch(events)
    >>> [r.tier.name for r in results]
    ['PERENNIAL', 'INERT']
    """
    out = []
    for ev in events:
        a = ev.get("alpha", alpha)
        out.append(
            compute(
                P=ev["P"],
                A=ev["A"],
                season=ev["season"],
                substrate=ev["substrate"],
                alpha=a,
            )
        )
    return out
