"""
seri.plotting
=============

Standard matplotlib figures for SERI results.

This module is *optional*: ``matplotlib`` is not a hard dependency of
the ``seri`` package. Importing this module without matplotlib installed
will raise a clear :class:`ImportError` with installation instructions.

The two functions exposed here cover the two most common visual needs:

* :func:`plot_tier_bar` - a horizontal tier bar (analogous to
  Fig. 3c / Fig. 5b of the manuscript) marking where a given event sits
  on the operational tier axis.
* :func:`plot_event_summary` - a one-panel summary card for a single
  ``SERIResult`` showing the value, the tier, the inputs and the
  resolved coefficients.
"""

from __future__ import annotations

from typing import Optional

from .core import SERIResult
from .tiers import Tier


def _import_matplotlib():
    try:
        import matplotlib.pyplot as plt  # noqa: WPS433
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "matplotlib is required for seri.plotting but is not installed.\n"
            "Install it with:  pip install matplotlib"
        ) from exc
    return plt


# Default colour scheme for the six tiers (red -> green gradient,
# matching the spirit of Fig. 3c of the manuscript).
TIER_COLOURS = {
    Tier.INERT:     "#a83232",
    Tier.MICROBIAL: "#d97a4f",
    Tier.ANNUAL:    "#e8b94f",
    Tier.PERENNIAL: "#7fb04f",
    Tier.WADI:      "#3f8f3f",
    Tier.REGIONAL:  "#1f5e1f",
}


def plot_tier_bar(
    seri_value: float,
    *,
    label: Optional[str] = None,
    log_scale: bool = True,
    ax=None,
):
    """
    Draw a horizontal tier bar with a marker at ``seri_value``.

    Parameters
    ----------
    seri_value : float
        SERI value to mark (must be > 0 if ``log_scale`` is True).
    label : str, optional
        Annotation drawn above the marker, e.g. ``'Abadla 2015'``.
    log_scale : bool, optional
        Whether the SERI axis is log-scaled. Default True (recommended,
        because the operational tier boundaries span three orders of
        magnitude).
    ax : matplotlib Axes, optional
        Axes to draw into. If None, a new figure is created.

    Returns
    -------
    matplotlib.axes.Axes
        The axes containing the bar.
    """
    plt = _import_matplotlib()

    if ax is None:
        _, ax = plt.subplots(figsize=(9, 1.6))

    # Draw one rectangle per tier, on a log axis if requested.
    # Use 30 as the lower display bound (just below the INERT tier ceiling
    # at 100, generous enough to fit the marker for very small events).
    display_lower = 30.0
    display_upper = 50000.0

    for tier in Tier:
        lo = max(tier.lower_bound, display_lower) if tier == Tier.INERT else tier.lower_bound
        if tier.lower_bound == 0 and log_scale:
            lo = display_lower
        hi = min(tier.upper_bound, display_upper)
        ax.axvspan(lo, hi, color=TIER_COLOURS[tier], alpha=0.85)
        # Tier label centered in the rectangle (geometric mean for log axes).
        if log_scale:
            centre = (lo * hi) ** 0.5
        else:
            centre = 0.5 * (lo + hi)
        ax.text(
            centre,
            0.5,
            tier.label.split()[0].lower(),
            ha="center", va="center",
            fontsize=8, color="white", fontweight="bold",
        )

    if log_scale:
        ax.set_xscale("log")
    ax.set_xlim(display_lower, display_upper)
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.set_xlabel("SERI value (log scale; tier boundaries from Table 1)")

    # Marker.
    ax.axvline(seri_value, color="black", linewidth=1.2)
    ax.plot(seri_value, 1.05, marker="v", color="black",
            markersize=10, clip_on=False)
    if label:
        ax.text(
            seri_value, 1.18,
            f"{label}\nSERI = {seri_value:,.0f}".replace(",", " "),
            ha="center", va="bottom",
            fontsize=9, fontweight="bold",
        )

    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)

    return ax


def plot_event_summary(result: SERIResult, *, ax=None):
    """
    One-panel summary card for a single SERI result.

    Shows the value, the tier (with its description), and a compact
    table of the inputs (P, A, alpha) and resolved coefficients (f, g).
    """
    plt = _import_matplotlib()

    if ax is None:
        fig, ax = plt.subplots(figsize=(7.5, 4))

    ax.axis("off")

    tier_colour = TIER_COLOURS[result.tier]

    ax.text(
        0.02, 0.93,
        f"SERI = {result.value:,.0f}".replace(",", " "),
        fontsize=22, fontweight="bold", transform=ax.transAxes,
    )
    ax.text(
        0.02, 0.81,
        result.tier_name,
        fontsize=14, color=tier_colour,
        fontweight="bold", transform=ax.transAxes,
    )
    ax.text(
        0.02, 0.72,
        result.tier_description,
        fontsize=9, style="italic", color="#444",
        transform=ax.transAxes, wrap=True,
    )

    # Inputs table.
    rows = [
        ("Inputs", ""),
        ("  P (mean intensity)", f"{result.P:g} mm"),
        ("  A (contiguous area)", f"{result.A:g} km²"),
        ("Coefficients", ""),
        ("  alpha", f"{result.alpha:g}"),
        ("  f (season)", f"{result.f:g}"),
        ("  g (substrate)", f"{result.g:g}"),
    ]
    y0 = 0.55
    for i, (k, v) in enumerate(rows):
        weight = "bold" if not k.startswith("  ") else "normal"
        ax.text(0.02, y0 - 0.07 * i, k, fontsize=10,
                fontweight=weight, transform=ax.transAxes)
        ax.text(0.45, y0 - 0.07 * i, v, fontsize=10,
                transform=ax.transAxes)

    # Tier bar inset.
    bar_ax = ax.inset_axes([0.55, 0.05, 0.42, 0.35])
    plot_tier_bar(result.value, ax=bar_ax)
    bar_ax.set_xlabel("SERI value (log)", fontsize=8)

    return ax
