# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
No change to the scientific formula, default coefficients, tier boundaries,
or computed results.

### Fixed
- Web calculator: added the missing "microbial" label to the six-tier scale
  bar (the 100-500 SERI tier was previously unlabeled).

## [1.0.2] — 2026-05-31
Released on Zenodo — version DOI 10.5281/zenodo.20478949
(software concept DOI 10.5281/zenodo.20000268). The package is cited via the
concept DOI, which always resolves to the latest version.
## [1.0.1] — 2026-05-31

Maintenance release: packaging, metadata, and continuous-integration fixes.
No change to the scientific formula, default coefficients, tier boundaries,
or any computed result; the 73 unit tests are unchanged and all pass.

### Fixed
- Software DOI corrected throughout the package to the SERI code deposit
  (10.5281/zenodo.20000268); earlier files referenced the SaharaFlora Pro
  deposit (…19535545) by mistake.
- Repository URLs corrected to https://github.com/Selkh-arch/seri.
- Removed unused imports and placeholder f-strings flagged by ruff; the
  package now passes `ruff check` cleanly.

### Added
- Continuous integration: `.github/workflows/tests.yml` (ruff lint + pytest
  on Python 3.9–3.12).
- Release automation: `.github/workflows/release-to-pypi.yml` using PyPI
  Trusted Publishing (OIDC). See the README for the one-time PyPI setup.

## [1.0.0] — 2026-04-30

First public release accompanying the SERI concept paper
(Selkh, *Earth-Science Reviews*, in review).

### Added
- `seri.compute()` — single-event SERI calculation with input validation.
- `seri.compute_batch()` — batch helper for event archives.
- `seri.SERIResult` — immutable result dataclass exposing the value, the
  tier and all coefficients used.
- `seri.Tier` — enum of the six operational ecological tiers, with
  human-readable labels and descriptions.
- `seri.classify()` — map a numerical SERI value to its tier.
- `seri.SEASON_COEFFICIENT`, `seri.SUBSTRATE_COEFFICIENT` — published
  default coefficient values (manuscript §§ 3.3, 3.4, 4.3, 4.4).
- `seri.coefficients.resolve_season_coefficient()` — accepts month
  numbers (1-12) or season labels.
- `seri.coefficients.resolve_substrate_coefficient()` — accepts a
  single label or an area-weighted mapping.
- `seri.earth_engine.compute_from_earth_engine()` — optional wrapper
  around the GPM IMERG V07 detection pipeline.
- `seri.plotting.plot_tier_bar()` — horizontal tier bar (Fig. 3c style).
- `seri.plotting.plot_event_summary()` — one-panel summary card.
- **`seri` console script** — CLI with `compute`, `demo`, `tiers`,
  `gui` and `info` subcommands. Created automatically by
  `pip install seri` (becomes `seri.exe` on Windows).
- **`seri-gui` console script** — direct shortcut to the graphical
  interface.
- **Tkinter GUI** (`seri.gui`) — minimal single-window calculator with
  P, A, month, substrate and α inputs and a coloured tier-bar result
  panel. Pre-filled with the Abadla 2015 anchor case.
- **Windows `.bat` launchers** (`scripts/`) — `install.bat`,
  `run-gui.bat`, `run-demo.bat`, `run-notebook.bat`, `run-tests.bat`
  for double-click usage on Windows.
- Regression test on the Abadla 2015 anchor case (manuscript § 5.1)
  that asserts SERI ≈ 2353 within 1 % numerical drift.
- Sensitivity tests covering the published α band [0.66, 0.78].
- Boundary tests on all five tier transitions.
- 73 unit tests in total.

### Notes
- The default value `α = 0.68` is a *working value* pending the formal
  empirical calibration on the *n* ≈ 150 event archive 2013–2024
  reported in the companion paper (Selkh, in prep.). The companion paper
  will publish α with bootstrap confidence intervals; future minor
  releases (v1.x) of this package will update the default value
  accordingly, with the change documented here and in the README.
- The substrate coefficients are informed by the published
  infiltration / runoff literature for North African arid soils
  (Pouget 1980; Halitim 1988; Cantón *et al.* 2011); systematic in-situ
  calibration is part of the on-going programme.
- Tier boundaries are calibrated for the northern Algerian Sahara;
  transfer to other hyper-arid systems requires regional re-calibration
  (manuscript § 6.2).

[1.0.1]: https://github.com/Selkh-arch/seri/releases/tag/v1.0.1
[1.0.0]: https://github.com/Selkh-arch/seri/releases/tag/v1.0.0
