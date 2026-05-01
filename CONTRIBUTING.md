# Contributing to SERI

Thank you for your interest in SERI. We welcome contributions in
the form of bug reports, documentation improvements, new examples,
and code patches.

This document describes the conventions for contributing. By
participating, you agree to abide by the project's
Code of Conduct (see CODE_OF_CONDUCT.md).

## Quick links

- Bug reports and feature requests: open an issue on
  https://github.com/Selkh-arch/seri/issues
- Security issues: see SECURITY.md - please do not open a public
  issue for security matters.
- Questions about the science: the manuscript on Zenodo is the
  authoritative reference; the email of the corresponding author is
  in CITATION.cff.

## Reporting a bug

Please include:

1. The version of SERI you are using (`seri --version`).
2. The version of Python (`python --version`).
3. Your operating system.
4. A minimal reproducible example: the shortest piece of code that
   triggers the bug.
5. The full error message and traceback.

## Proposing a code change

For bug fixes and small improvements, the standard GitHub flow is
welcome:

1. Fork the repository.
2. Create a feature branch (`git checkout -b fix/short-description`).
3. Make your change. Add at least one regression test.
4. Run the full test suite locally:
       pip install -e ".[dev]"
       pytest -v
   All 77+ tests must pass.
5. Commit with a clear, imperative-mood message
   (e.g. "Fix segfault in compute_batch when N=1").
6. Open a pull request against `main`.

For substantive scientific changes - different default value of
alpha, new tier boundaries, changes to f or g coefficients - please
open an issue first to discuss the rationale and link to the
supporting evidence.

## Style

- Formatting: code is formatted with `black` (line length 100).
- Linting: code passes `ruff check`.
- Docstrings: numpydoc-style with at least one runnable doctest.
- Tests: every new feature comes with at least one regression test.

## How to bump the default alpha

The default value of alpha (currently 0.68 in seri/core.py) is
intentionally tied to a published calibration. Changing
DEFAULT_ALPHA is a major version bump (v1 -> v2). It must be
accompanied by:

1. A paragraph in CHANGELOG.md explaining the new calibration source.
2. An updated reference test in tests/test_abadla_2015.py.
3. A short discussion in the README.

The same rules apply to changes in tier boundaries and substrate or
seasonal coefficients.

## Code of conduct

This project follows the Contributor Covenant 2.1. See
CODE_OF_CONDUCT.md. Reports of unacceptable behavior may be sent to
chouaib342@univ-adrar.edu.dz.