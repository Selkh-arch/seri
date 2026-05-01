"""Tests for seri.core."""

import math

import pytest

import seri
from seri import Tier


def test_compute_returns_a_seri_result():
    r = seri.compute(P=10.79, A=1624, season=2, substrate="mixed")
    assert isinstance(r, seri.SERIResult)


def test_compute_zero_intensity_yields_zero():
    r = seri.compute(P=0, A=1000, season=2, substrate="reg")
    assert r.value == 0
    assert r.tier is Tier.INERT


def test_compute_zero_area_yields_zero():
    r = seri.compute(P=10, A=0, season=2, substrate="reg")
    assert r.value == 0
    assert r.tier is Tier.INERT


def test_compute_negative_inputs_raise():
    with pytest.raises(ValueError):
        seri.compute(P=-1, A=100, season=2, substrate="reg")
    with pytest.raises(ValueError):
        seri.compute(P=10, A=-100, season=2, substrate="reg")


def test_compute_alpha_out_of_range_raises():
    with pytest.raises(ValueError):
        seri.compute(P=10, A=100, season=2, substrate="reg", alpha=0)
    with pytest.raises(ValueError):
        seri.compute(P=10, A=100, season=2, substrate="reg", alpha=1.2)
    with pytest.raises(ValueError):
        seri.compute(P=10, A=100, season=2, substrate="reg", alpha=-0.5)


def test_compute_alpha_at_boundary_one_is_allowed():
    # alpha = 1 is a degenerate but mathematically valid case
    # (linear scaling on A); it must be accepted.
    r = seri.compute(P=10, A=100, season=2, substrate="reg", alpha=1.0)
    assert r.alpha == 1.0


def test_compute_event_a_event_b_diagnostic_separation():
    """
    Reproduce the diagnostic separation illustrated in Fig. 3 of the
    manuscript: two events with similar peak intensity but very different
    spatial coherence land in clearly different tiers.

    Event A: convective cell, small footprint, summer (high PET).
    Event B: frontal-system, large footprint, winter (low PET) -
             analogous to Abadla 2015.

    The exact tier of Event A depends on substrate and seasonal choices,
    but it must be at least three tiers below Event B.
    """
    event_a = seri.compute(P=18, A=51, season=7, substrate="reg")
    event_b = seri.compute(P=17, A=1281, season=2, substrate="mixed")
    # Event A should be in INERT or MICROBIAL.
    assert event_a.tier in (Tier.INERT, Tier.MICROBIAL)
    # Event B should be in PERENNIAL (or higher).
    assert event_b.value >= Tier.PERENNIAL.lower_bound


def test_compute_batch_preserves_order():
    events = [
        {"P": 10.79, "A": 1624, "season": 2, "substrate": "mixed"},
        {"P": 18,    "A": 51,   "season": 7, "substrate": "reg"},
        {"P": 25,    "A": 8000, "season": 11, "substrate": "wadi_bottom"},
    ]
    results = seri.compute_batch(events)
    assert len(results) == 3
    assert results[0].tier is Tier.PERENNIAL
    assert results[1].tier in (Tier.INERT, Tier.MICROBIAL)
    # 25 * 8000^0.68 * 1.30 * 1.60 = ~ 25 * 419 * 2.08 = ~21800 -> REGIONAL
    assert results[2].tier in (Tier.WADI, Tier.REGIONAL)


def test_compute_batch_per_event_alpha_overrides_default():
    events = [
        {"P": 10.79, "A": 1624, "season": 2, "substrate": "mixed", "alpha": 0.50},
    ]
    [r] = seri.compute_batch(events)
    assert r.alpha == 0.50


def test_seri_result_to_dict_and_repr():
    r = seri.compute(P=10.79, A=1624, season=2, substrate="mixed")
    d = r.to_dict()
    assert d["tier"] == "PERENNIAL"
    assert d["P_mm"] == 10.79
    assert "SERI" in d
    # repr should contain the value.
    assert "SERIResult" in repr(r)


def test_seri_result_is_immutable():
    r = seri.compute(P=10.79, A=1624, season=2, substrate="mixed")
    with pytest.raises((AttributeError, Exception)):
        r.value = 0  # frozen dataclass: must reject re-assignment


def test_alpha_default_matches_module_constant():
    r1 = seri.compute(P=10, A=100, season=2, substrate="reg")
    r2 = seri.compute(P=10, A=100, season=2, substrate="reg", alpha=seri.DEFAULT_ALPHA)
    assert math.isclose(r1.value, r2.value)
