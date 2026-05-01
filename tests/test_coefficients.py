"""Tests for seri.coefficients."""

import pytest

from seri.coefficients import (
    SEASON_COEFFICIENT,
    SUBSTRATE_COEFFICIENT,
    resolve_season_coefficient,
    resolve_substrate_coefficient,
)


# ---------------------------------------------------------------------------
# Seasonal coefficient
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "month, expected",
    [
        (1, 1.30), (2, 1.30), (3, 1.30),
        (10, 1.30), (11, 1.30), (12, 1.30),
        (4, 0.65), (5, 0.65), (9, 0.65),
        (6, 0.35), (7, 0.35), (8, 0.35),
    ],
)
def test_resolve_month_to_season_coefficient(month, expected):
    assert resolve_season_coefficient(month) == expected


@pytest.mark.parametrize(
    "label, expected",
    [
        ("winter", 1.30),
        ("WINTER", 1.30),
        (" winter ", 1.30),
        ("shoulder", 0.65),
        ("summer", 0.35),
    ],
)
def test_resolve_label_to_season_coefficient(label, expected):
    assert resolve_season_coefficient(label) == expected


def test_resolve_season_invalid_label_raises():
    with pytest.raises(ValueError):
        resolve_season_coefficient("autumn")


def test_resolve_season_invalid_month_raises():
    with pytest.raises(ValueError):
        resolve_season_coefficient(0)
    with pytest.raises(ValueError):
        resolve_season_coefficient(13)


def test_resolve_season_invalid_type_raises():
    with pytest.raises(TypeError):
        resolve_season_coefficient(2.5)


def test_season_coefficients_match_manuscript_3_4():
    # Spot-check the canonical values reported in section 3.4.
    assert SEASON_COEFFICIENT["winter"] == 1.30
    assert SEASON_COEFFICIENT["shoulder"] == 0.65
    assert SEASON_COEFFICIENT["summer"] == 0.35


# ---------------------------------------------------------------------------
# Substrate coefficient
# ---------------------------------------------------------------------------

def test_substrate_coefficients_match_manuscript_3_3():
    assert SUBSTRATE_COEFFICIENT["hamada"] == 0.55
    assert SUBSTRATE_COEFFICIENT["reg"] == 0.85
    assert SUBSTRATE_COEFFICIENT["erg"] == 1.25
    assert SUBSTRATE_COEFFICIENT["wadi_bottom"] == 1.60
    assert SUBSTRATE_COEFFICIENT["sebkha"] == 0.30
    # Convenience preset for the Abadla anchor case.
    assert SUBSTRATE_COEFFICIENT["mixed"] == 1.10


def test_substrate_aliases():
    assert resolve_substrate_coefficient("wadi-bottom") == 1.60
    assert resolve_substrate_coefficient("Wadi Bottom") == 1.60
    assert resolve_substrate_coefficient("wadibottom") == 1.60


def test_substrate_mapping_area_weighted_mean():
    # 50/50 reg + wadi-bottom -> 0.5*0.85 + 0.5*1.60 = 1.225
    g = resolve_substrate_coefficient({"reg": 0.5, "wadi_bottom": 0.5})
    assert g == pytest.approx(1.225, abs=1e-9)


def test_substrate_mapping_must_sum_to_one():
    with pytest.raises(ValueError):
        resolve_substrate_coefficient({"reg": 0.4, "erg": 0.4})


def test_substrate_negative_fraction_raises():
    with pytest.raises(ValueError):
        resolve_substrate_coefficient({"reg": -0.1, "erg": 1.1})


def test_substrate_unknown_label_raises():
    with pytest.raises(ValueError):
        resolve_substrate_coefficient("playa")


def test_substrate_empty_mapping_raises():
    with pytest.raises(ValueError):
        resolve_substrate_coefficient({})
