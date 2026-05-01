"""
SERI v1.0 — quick demo
======================

Run with::

    python examples/demo_abadla_2015.py

This script reproduces the headline numerical result of the SERI concept
paper (Selkh 2026, Earth-Science Reviews, in review) and exercises the
main features of the public API.

Expected output (key line):

    SERI(Abadla 2015) = 2352.6  →  PERENNIAL (Perennial response)
"""

from __future__ import annotations

import seri


def header(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


# ---------------------------------------------------------------------------
# 1. The Abadla 2015 anchor case (manuscript §5.1)
# ---------------------------------------------------------------------------
header("1. Abadla 2015 anchor case — reproduction of the published value")

result = seri.compute(
    P=10.79,            # mean intensity (mm)
    A=1624,             # contiguous footprint (km²)
    season=2,           # February → winter regime
    substrate="mixed",  # area-weighted reg + wadi-bottom mix
)

print(f"Inputs:        P = 10.79 mm, A = 1624 km²")
print(f"Coefficients:  α = {result.alpha}, f = {result.f}, g = {result.g}")
print(f"SERI value:    {result.value:.1f}   (manuscript §5.1: ~2353)")
print(f"Tier:          {result.tier.name} — {result.tier_name}")
print(f"Description:   {result.tier_description}")


# ---------------------------------------------------------------------------
# 2. Diagnostic separation — Fig. 3 of the manuscript
# ---------------------------------------------------------------------------
header("2. Diagnostic separation: convective cell vs frontal system")

print("Two synthetic events with similar peak intensity (~17-18 mm)")
print("but very different spatial coherence:\n")

event_a = seri.compute(P=18.0, A=51,   season=7, substrate="reg")
event_b = seri.compute(P=17.0, A=1281, season=2, substrate="mixed")

print(f"  Event A (summer convective cell, 51 km²):")
print(f"      SERI = {event_a.value:>6.0f}   →   {event_a.tier_name}")
print(f"  Event B (winter frontal system, 1281 km²):")
print(f"      SERI = {event_b.value:>6.0f}   →   {event_b.tier_name}")
print()
print("→ identical scalar P, but SERI separates them by several tiers,")
print("  driven entirely by the explicit spatial-coherence term A^α.")


# ---------------------------------------------------------------------------
# 3. Batch processing
# ---------------------------------------------------------------------------
header("3. Batch processing of an event archive")

events = [
    {"P": 10.79, "A": 1624, "season":  2, "substrate": "mixed"},
    {"P":  8.0,  "A":  300, "season": 11, "substrate": "reg"},
    {"P": 18.0,  "A":   51, "season":  7, "substrate": "reg"},
    {"P": 25.0,  "A": 8000, "season":  3, "substrate": "wadi_bottom"},
    {"P":  3.0,  "A":  100, "season":  6, "substrate": "hamada"},
]

print(f"{'P (mm)':>8}  {'A (km²)':>9}  {'month':>6}  {'substrate':>13}  "
      f"{'SERI':>9}  tier")
print("-" * 72)
for ev, r in zip(events, seri.compute_batch(events)):
    print(f"{ev['P']:>8.2f}  {ev['A']:>9.0f}  {ev['season']:>6d}  "
          f"{ev['substrate']:>13s}  {r.value:>9.1f}  {r.tier_name}")


# ---------------------------------------------------------------------------
# 4. Sensitivity to α (manuscript §4.2)
# ---------------------------------------------------------------------------
header("4. Sensitivity of the Abadla 2015 case to the spatial exponent α")

print("Manuscript §4.2 reports that the perennial-response classification")
print("is robust for α ∈ [0.66, 0.78]:\n")

for alpha in [0.50, 0.60, 0.66, 0.68, 0.72, 0.78, 0.85]:
    r = seri.compute(P=10.79, A=1624, season=2, substrate="mixed", alpha=alpha)
    marker = "✓ PERENNIAL" if r.tier is seri.Tier.PERENNIAL else "✗ " + r.tier.name
    print(f"  α = {alpha:.2f}   SERI = {r.value:>7.0f}   {marker}")


# ---------------------------------------------------------------------------
# 5. Area-weighted substrate mixing
# ---------------------------------------------------------------------------
header("5. Area-weighted substrate mixing (manuscript §3.4)")

# Same rainfall event, but with explicit area-weighted substrate composition.
mixes = {
    "Pure hamada (crusted plateau)":           {"hamada": 1.0},
    "Pure reg (desert pavement)":              {"reg": 1.0},
    "70 % reg + 30 % wadi-bottom":             {"reg": 0.7, "wadi_bottom": 0.3},
    "50 % reg + 50 % wadi-bottom":             {"reg": 0.5, "wadi_bottom": 0.5},
    "Pure wadi-bottom (alluvial fines)":       {"wadi_bottom": 1.0},
}

for label, mix in mixes.items():
    r = seri.compute(P=10.79, A=1624, season=2, substrate=mix)
    print(f"  {label:<42s}  g = {r.g:.3f}  SERI = {r.value:>6.0f}   {r.tier.name}")


# ---------------------------------------------------------------------------
# 6. Tier table
# ---------------------------------------------------------------------------
header("6. The six operational tiers (manuscript Table 1)")

for row in seri.tier_table():
    name, lo, hi, label = row
    if hi == float("inf"):
        bound = f"≥ {lo:.0f}"
    else:
        bound = f"[{lo:.0f}, {hi:.0f})"
    print(f"  {name:<10s}  {bound:<18s}  {label}")


print()
print("=" * 72)
print("End of demo.")
print()
print("Cite this software:")
print("  Selkh, C. (2026). SERI — Spatial Effective Rainfall Index")
print("  [Computer software]. Zenodo. doi:10.5281/zenodo.PLACEHOLDER_SERI")
print("=" * 72)
