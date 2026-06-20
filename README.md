# SERI — Spatial Effective Rainfall Index

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python ≥ 3.9](https://img.shields.io/badge/python-≥3.9-blue.svg)](https://www.python.org/)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.20000268-blue)](https://doi.org/10.5281/zenodo.20478949)

Reference Python implementation of the **Spatial Effective Rainfall Index (SERI)** —
an event-scale ecological-effectiveness metric for hyper-arid environments
introduced in Selkh (2026).

---

## How to cite

If you use SERI in your research, please cite **both** the software and
the concept paper:

**Software**
```
Selkh, C. (2026). SERI — Spatial Effective Rainfall Index
[Computer software]. Zenodo.
https://doi.org/10.5281/zenodo.20478949
```

**Concept paper**
```
Selkh, C. (2026). A Century After De Martonne: Why Spatial Coherence
is the Missing Dimension of Aridity in the Hyper-Arid Sahara.
Earth-Science Reviews, in review.
```

A ready-to-paste BibTeX entry is provided in [`CITATION.cff`](CITATION.cff)
and via the **Cite this repository** button at the top of this page.

---

## What is SERI?

Classical aridity and drought indices (De Martonne 1926; SPI; SPEI;
UNEP-AI) treat precipitation as a scalar quantity. In hyper-arid
environments, two events of identical station-measured intensity can
produce radically different ecological outcomes depending on whether
the rainfall is confined to a small convective cell or distributed
contiguously over a frontal-system footprint of several thousand square
kilometres.

SERI elevates the **contiguous spatial extent** of a rainfall event to a
first-class variable in the quantification of its ecological efficacy:

```
SERI = P · A^α · f(season) · g(substrate)
```

| Symbol | Meaning | Unit |
|--------|---------|------|
| `P` | Event mean intensity over the footprint | mm |
| `A` | Contiguous area receiving rainfall ≥ 5 mm/day | km² |
| `α` | Sub-linear exponent on the spatial term (default 0.68 ¹) | – |
| `f` | Seasonal coefficient (winter 1.30, shoulder 0.65, summer 0.35) | – |
| `g` | Substrate coefficient (hamada 0.55 → wadi-bottom 1.60) | – |

¹ Working value pending formal calibration on the *n* ≈ 150 event archive
2013–2024; see Selkh, in prep.

The index is operationally classified into **six tiers**, from
*Ecologically inert* (SERI < 100) to *Regional recharge* (SERI ≥ 15 000).

---

## Installation

```bash
pip install seri
```

That's all you need for the core API. Optional extras:

```bash
pip install "seri[plot]"        # add matplotlib for figures
pip install "seri[earthengine]" # add the Google Earth Engine wrapper
pip install "seri[all]"         # everything
```

### Windows: double-click launchers

If you prefer not to open a terminal, the [`scripts/`](scripts/)
directory contains five `.bat` files, double-clickable from File
Explorer:

| File | Purpose |
|---|---|
| `install.bat` | First-time setup. Installs SERI + tests it. |
| `run-gui.bat` | Opens the SERI calculator window (Tkinter). |
| `run-demo.bat` | Runs the bundled Abadla 2015 demonstration. |
| `run-notebook.bat` | Launches Jupyter on the demo notebook. |
| `run-tests.bat` | Re-runs the 73-test suite. |

The first time, run `install.bat` once; afterwards you can use any of
the others directly. See [`scripts/README.md`](scripts/README.md) for
details.

### Command line

After installation, the `seri` command is available on PATH:

```bash
seri compute --P 10.79 --A 1624 --month 2 --substrate mixed
seri compute --P 10.79 --A 1624 --month 2 --substrate mixed --json
seri demo
seri tiers
seri gui          # open the graphical interface
seri info         # version and citation info
```

---

## Quick start

Reproduce the **Abadla 2015** anchor case from the manuscript (§ 5.1):

```python
import seri

result = seri.compute(
    P=10.79,           # mean intensity (mm)
    A=1624,            # contiguous area (km²)
    season=2,          # February → winter regime
    substrate="mixed", # area-weighted reg + wadi-bottom mix
)

print(result)
# SERIResult(value=2352.6, tier=PERENNIAL, P=10.79 mm, A=1624 km², α=0.68, f=1.3, g=1.1)

print(result.tier_name)
# 'Perennial response'

print(result.tier_description)
# 'Leaf-flush of established perennials; sustained NDVI anomaly 30-90 days.'
```

A batch version is available for archives:

```python
events = [
    {"P": 10.79, "A": 1624, "season":  2, "substrate": "mixed"},
    {"P": 18.0,  "A":   51, "season":  7, "substrate": "reg"},   # convective cell
    {"P": 25.0,  "A": 8000, "season": 11, "substrate": "wadi_bottom"},
]
for r in seri.compute_batch(events):
    print(f"  SERI = {r.value:>7.0f}   →   {r.tier_name}")
```

For a complete walk-through with figures, see
[`examples/notebook_demo.ipynb`](examples/notebook_demo.ipynb).

---

## The six ecological tiers

| SERI value | Tier | Typical biological response |
|---|---|---|
| < 100 | Ecologically inert | No measurable response; event dissipates by evaporation. |
| 100 – 500 | Microbial | Ephemeral biological soil-crust activation. |
| 500 – 2 000 | Annual germination | Therophytes and short-lived ephemerals. |
| 2 000 – 5 000 | Perennial response | Leaf-flush of established perennials; NDVI anomaly 30–90 d. |
| 5 000 – 15 000 | Wadi activation | Ephemeral flow, shallow-aquifer recharge. |
| ≥ 15 000 | Regional recharge | Exceptional event; deep-aquifer recharge. |

These thresholds are calibrated for the Algerian Sahara transect
El Bayadh – Béchar/Abadla – Timimoun-North. Transfer to other hyper-arid
systems (Atacama, Namib, Karakum, Rub' al-Khali) requires regional
re-calibration of the coefficients (see manuscript § 6.2).

---

## Optional Earth Engine wrapper

If you have `earthengine-api` installed and authenticated, you can run
the full pipeline end-to-end from a Python session:

```python
import ee
import seri.earth_engine as see

ee.Initialize()

aoi = ee.Geometry.Rectangle([-3.0715, 30.9064, -2.4085, 31.1336])  # Abadla AOI

result = see.compute_from_earth_engine(
    aoi=aoi,
    start_date="2015-02-22",
    end_date="2015-03-02",
    substrate="mixed",
)
print(result)
```

> ⚠️ The current GPM IMERG V07 release is known to under-detect Saharan
> rainfall events (Sun *et al.* 2018; Dezfuli 2017). For the Abadla
> anchor case specifically, the manuscript anchors the diachronic
> analysis on a deterministic 1 596 km² AOI rather than per-call IMERG
> re-detection (manuscript § 5.6).

---

## Roadmap

| Version | Scope | Status |
|---|---|---|
| **v1.0** (this release) | Public reference implementation of SERI-1 (concept paper) | ✅ |
| v1.1 | Event-archive helpers, ROC plotting against SPI/SPEI | planned |
| v2.0 (**SERI-2**) | Continuous `f(PET) = exp(−PET / PET_ref)` from ERA5-Land | planned |
| v3.0 (**SERI-S**) | Satellite-only `A` from MSG/SEVIRI cloud-top temperature | planned |
| v4.0 (**SERI-P**) | Climate-projection extension on CMIP6 (SSP2-4.5 / SSP5-8.5) | planned |

The empirical calibration of α with bootstrap confidence intervals on
the 2013–2024 archive (n ≈ 150) is reported in the **companion paper**
(Selkh, in preparation).

---

## Contributing

Pull requests are welcome for:
- Bug fixes in the reference implementation
- Documentation improvements
- New examples or notebooks

For substantive scientific changes (different default α, new tier
boundaries, changes to the f or g coefficients), please open an issue
first to discuss the rationale.

---

## License

Apache License 2.0 — see [LICENSE](LICENSE).

This permissive licence allows commercial and non-commercial use,
redistribution and modification, **provided that proper attribution to
the original author is preserved**.

---

## Acknowledgements

This software accompanies a decade of field campaigns 2013–2024 across
the Algerian Sahara transect supported by Université Ahmed Draia
d'Adrar. NASA, JAXA and the Climate Hazards Center (UC Santa Barbara)
are acknowledged for free public access to the GPM IMERG, MODIS
MOD13A3 and CHIRPS products on which the pipeline depends.
