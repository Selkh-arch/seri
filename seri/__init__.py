"""
seri - Spatial Effective Rainfall Index
========================================

Reference Python implementation of the Spatial Effective Rainfall Index
(SERI), an event-scale ecological-effectiveness metric for hyper-arid
environments.

    SERI = P * A**alpha * f(season) * g(substrate)

Quick start
-----------

>>> import seri
>>> result = seri.compute(P=10.79, A=1624, season=2, substrate='mixed')
>>> print(result)  # doctest: +ELLIPSIS
SERIResult(value=2352..., tier=PERENNIAL, ...)
>>> result.tier_name
'Perennial response'

How to cite
-----------
If you use SERI in your research, please cite both the software and
the concept paper:

    Selkh, C. (2026). SERI - Spatial Effective Rainfall Index
    [Computer software]. Zenodo. doi:10.5281/zenodo.20000268

    Selkh, C. (2026). A Century After De Martonne: Why Spatial Coherence
    is the Missing Dimension of Aridity in the Hyper-Arid Sahara.
    Earth-Science Reviews, in review.

License
-------
Apache License 2.0. See the LICENSE file at the root of the repository.
"""

from .core import (
    DEFAULT_ALPHA,
    DEFAULT_RAIN_THRESHOLD_MM_DAY,
    SERIResult,
    compute,
    compute_batch,
)
from .tiers import Tier, classify, tier_table
from .coefficients import (
    SEASON_COEFFICIENT,
    SUBSTRATE_COEFFICIENT,
    resolve_season_coefficient,
    resolve_substrate_coefficient,
)

__version__ = "1.0.2"

__all__ = [
    # core
    "compute",
    "compute_batch",
    "SERIResult",
    "DEFAULT_ALPHA",
    "DEFAULT_RAIN_THRESHOLD_MM_DAY",
    # tiers
    "Tier",
    "classify",
    "tier_table",
    # coefficients
    "SEASON_COEFFICIENT",
    "SUBSTRATE_COEFFICIENT",
    "resolve_season_coefficient",
    "resolve_substrate_coefficient",
    # version
    "__version__",
]
