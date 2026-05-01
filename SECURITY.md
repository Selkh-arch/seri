# Security policy

## Reporting a security or scientific-correctness issue

If you discover a security vulnerability or a scientific-correctness
issue in SERI (for example, a numerical bug that produces incorrect
SERI values, an Earth Engine pipeline that does not match the
manuscript methodology, or any issue that could affect the integrity
of published results), please report it privately rather than opening
a public issue.

Email: chouaib342@univ-adrar.edu.dz

Subject line suggestion: "[SERI security] short description".

Please include:

1. The version of SERI affected (`seri --version`).
2. A minimal reproducer if possible.
3. Your assessment of the impact.

We aim to acknowledge security reports within 7 days and publish a
fix or mitigation within 30 days for confirmed issues. Reporters who
prefer to remain anonymous in any public advisory should say so
explicitly in their initial email.

## Supported versions

The latest released version on PyPI is the only officially supported
release. We will fix confirmed security issues there as quickly as
possible.

## Scope

In-scope:

* Numerical bugs that change the SERI value or its tier classification.
* Departures of the implementation from the published methodology.
* Vulnerabilities that allow code execution, file disclosure, or
  privilege escalation when the package is used as documented.

Out-of-scope:

* Issues in third-party dependencies (please report them upstream).
* Misconfigurations of the user's Earth Engine account or local
  Python environment.
* Performance limitations that do not affect numerical correctness.