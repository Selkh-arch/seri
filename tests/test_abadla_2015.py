"""
Regression test for the Abadla 2015 anchor case.

This test verifies that the reference Python implementation reproduces
the published numerical result for the Abadla, late-February 2015
anchor case as reported in section 5.1 of the manuscript:

    P     = 10.79 mm
    A     = 1624 km^2
    f     = 1.30 (winter regime)
    g     = 1.10 (mixed reg + wadi-bottom)
    alpha = 0.68
    => SERI ~ 2353 (perennial-response tier)

If this test ever breaks, either the formula has been changed, the
default coefficients have been changed, or the published value has been
re-calibrated. Any of those events is a backward-incompatibility and
deserves an explicit major version bump.
"""

import math

import pytest

import seri
from seri import Tier


# Published anchor-case inputs (manuscript v8.2, section 5.1).
ABADLA_P_MM = 10.79
ABADLA_A_KM2 = 1624.0
ABADLA_SEASON = 2  # February (winter regime)
ABADLA_SUBSTRATE = "mixed"  # area-weighted reg + wadi-bottom mix
ABADLA_PUBLISHED_SERI = 2353.0


def test_abadla_2015_reproduces_published_value():
    """Re-run the anchor-case calculation and check it lands within 1 % of 2353."""
    result = seri.compute(
        P=ABADLA_P_MM,
        A=ABADLA_A_KM2,
        season=ABADLA_SEASON,
        substrate=ABADLA_SUBSTRATE,
    )
    # The manuscript reports SERI ~ 2353; tolerate <= 1 % numerical drift.
    assert math.isclose(
        result.value, ABADLA_PUBLISHED_SERI, rel_tol=0.01
    ), (
        f"Abadla 2015 SERI = {result.value:.2f}, "
        f"expected ~ {ABADLA_PUBLISHED_SERI:.2f}"
    )


def test_abadla_2015_falls_in_perennial_tier():
    """The anchor case must classify as the PERENNIAL response tier."""
    result = seri.compute(
        P=ABADLA_P_MM,
        A=ABADLA_A_KM2,
        season=ABADLA_SEASON,
        substrate=ABADLA_SUBSTRATE,
    )
    assert result.tier is Tier.PERENNIAL
    assert result.tier_name == "Perennial response"
    # Lower part of the perennial range, as stated in the manuscript.
    assert 2000 <= result.value < 5000


def test_abadla_2015_uses_default_alpha():
    """The default alpha should be the manuscript's working value 0.68."""
    result = seri.compute(
        P=ABADLA_P_MM,
        A=ABADLA_A_KM2,
        season=ABADLA_SEASON,
        substrate=ABADLA_SUBSTRATE,
    )
    assert result.alpha == 0.68
    assert seri.DEFAULT_ALPHA == 0.68


# ---------------------------------------------------------------------------
# Sensitivity envelope (manuscript section 4.2)
# ---------------------------------------------------------------------------
# The manuscript states that with the section 5.1 inputs, the perennial
# tier (2000 <= SERI < 5000) corresponds to alpha in [0.66, 0.78].

@pytest.mark.parametrize("alpha", [0.66, 0.68, 0.70, 0.74, 0.78])
def test_abadla_2015_perennial_tier_robust_to_alpha_in_published_band(alpha):
    """Within [0.66, 0.78] alpha, Abadla 2015 must stay in PERENNIAL tier."""
    result = seri.compute(
        P=ABADLA_P_MM,
        A=ABADLA_A_KM2,
        season=ABADLA_SEASON,
        substrate=ABADLA_SUBSTRATE,
        alpha=alpha,
    )
    assert result.tier is Tier.PERENNIAL, (
        f"alpha={alpha}: SERI={result.value:.0f} -> {result.tier.name} "
        f"(expected PERENNIAL)"
    )


def test_abadla_2015_alpha_below_band_drops_below_perennial():
    """Below the published alpha band, the event drops into a lower tier."""
    result = seri.compute(
        P=ABADLA_P_MM,
        A=ABADLA_A_KM2,
        season=ABADLA_SEASON,
        substrate=ABADLA_SUBSTRATE,
        alpha=0.50,
    )
    # alpha=0.5 should not be in PERENNIAL anymore.
    assert result.tier in (Tier.ANNUAL, Tier.MICROBIAL)


def test_abadla_2015_substrate_mapping_matches_mixed_preset():
    """A 50/50 reg + wadi-bottom mapping should agree with the 'mixed' preset
    to within 5 % (the 'mixed' preset is g=1.10; 50/50 reg+wadi gives 1.225).

    The 'mixed' preset is documented as an area-weighted approximation of the
    Abadla event substrate, not strictly 50/50. This test simply checks that
    a 50/50 mapping gives the *same tier* as the preset.
    """
    via_preset = seri.compute(
        P=ABADLA_P_MM, A=ABADLA_A_KM2, season=2, substrate="mixed"
    )
    via_mapping = seri.compute(
        P=ABADLA_P_MM, A=ABADLA_A_KM2, season=2,
        substrate={"reg": 0.5, "wadi_bottom": 0.5},
    )
    assert via_preset.tier is via_mapping.tier
