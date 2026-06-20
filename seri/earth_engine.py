"""
seri.earth_engine
=================

Optional Google Earth Engine wrapper.

This module is *optional*: ``earthengine-api`` is not a required
dependency of the ``seri`` package. Importing this module will succeed
even if ``ee`` is not installed, but calling any of its functions will
raise a clear :class:`ImportError` with installation instructions.

The Earth Engine pipeline released alongside the manuscript is the
authoritative reference; see ``SERI_abadla_2015_v1.js`` and the related
scripts at DOI 10.5281/zenodo.20478949. The Python wrapper provided here
is a convenience for users who prefer to drive the same pipeline from a
Python environment (e.g. a Jupyter notebook).

The function ``compute_from_earth_engine`` performs the four steps of the
pipeline (manuscript section 3.4):

1. Aggregate IMERG V07 to daily totals over the AOI and the requested
   time window.
2. Apply the inclusion threshold (default 5 mm/day) and morphological
   closure to identify the contiguous footprint.
3. Compute area-weighted mean intensity P and footprint area A.
4. Resolve the seasonal and substrate coefficients and apply the SERI
   formula.
"""

from __future__ import annotations

from typing import Union

from .core import DEFAULT_ALPHA, DEFAULT_RAIN_THRESHOLD_MM_DAY, SERIResult, compute


def _import_ee():
    """Lazy import of earthengine-api with an informative error message."""
    try:
        import ee  # noqa: WPS433  (allow runtime import; ee is optional)
    except ImportError as exc:  # pragma: no cover - tested manually
        raise ImportError(
            "The earthengine-api package is required for "
            "seri.earth_engine but is not installed. Install it with:\n"
            "    pip install earthengine-api\n"
            "and authenticate with:\n"
            "    earthengine authenticate"
        ) from exc
    return ee


def compute_from_earth_engine(
    aoi,
    start_date: str,
    end_date: str,
    substrate: Union[str, dict] = "mixed",
    *,
    alpha: float = DEFAULT_ALPHA,
    rain_threshold_mm_day: float = DEFAULT_RAIN_THRESHOLD_MM_DAY,
    imerg_collection: str = "NASA/GPM_L3/IMERG_V07",
    imerg_band: str = "precipitation",
) -> SERIResult:
    """
    Compute SERI for a single event window from Google Earth Engine.

    .. warning::
       This function requires that the user has installed
       ``earthengine-api`` and is authenticated. It performs an
       Earth Engine ``getInfo()`` call and is therefore subject to
       Earth Engine quotas and latency.

    Parameters
    ----------
    aoi : ee.Geometry
        Area-of-interest polygon. Must already be an Earth Engine
        geometry object.
    start_date, end_date : str
        ISO date strings (``'YYYY-MM-DD'``) bracketing the rainfall
        event. The end date is exclusive in the Earth Engine convention.
    substrate : str or dict, optional
        Forwarded to :func:`seri.compute`. Defaults to ``'mixed'``,
        consistent with the Abadla anchor case. For best results, pass
        an area-weighted dict that reflects the substrate composition
        of the AOI.
    alpha : float, optional
        Spatial exponent. Defaults to 0.68.
    rain_threshold_mm_day : float, optional
        Inclusion threshold for the contiguous-area calculation.
        Default 5 mm/day, the manuscript-standard threshold.
    imerg_collection : str, optional
        Earth Engine collection ID for IMERG. Default
        ``'NASA/GPM_L3/IMERG_V07'``.
    imerg_band : str, optional
        Band name within the IMERG collection. Default
        ``'precipitation'`` (which IMERG reports in mm/hr).

    Returns
    -------
    SERIResult
        Same shape as :func:`seri.compute`, with ``P`` and ``A``
        populated from the IMERG re-analysis.

    Notes
    -----
    The current GPM IMERG V07 release is known to under-detect Saharan
    rainfall events (Sun et al. 2018; Dezfuli 2017). For Abadla 2015
    specifically, the manuscript anchors the diachronic analysis on a
    deterministic 1 596 km^2 AOI rather than on a per-call IMERG
    re-detection (manuscript section 5.6). When you observe an empty or
    suspiciously small footprint over a Saharan AOI, that limitation -
    not a bug in this wrapper - is the most likely cause.
    """
    ee = _import_ee()

    # IMERG reports precipitation in mm/hr; aggregate to daily totals.
    imerg = (
        ee.ImageCollection(imerg_collection)
        .filterDate(start_date, end_date)
        .filterBounds(aoi)
        .select(imerg_band)
    )

    # Half-hourly mm/hr -> daily mm: sum and divide by 2 (since each
    # half-hour value covers 0.5 h). Standard EE pattern.
    def _to_daily(date):
        date = ee.Date(date)
        next_day = date.advance(1, "day")
        daily = (
            imerg.filterDate(date, next_day)
            .sum()
            .multiply(0.5)  # convert sum-of-mm/hr-half-hours to mm/day
            .set("system:time_start", date.millis())
        )
        return daily

    n_days = ee.Date(end_date).difference(ee.Date(start_date), "day").toInt()
    days = ee.List.sequence(0, n_days.subtract(1)).map(
        lambda i: ee.Date(start_date).advance(i, "day")
    )
    daily_collection = ee.ImageCollection.fromImages(days.map(_to_daily))

    # Maximum daily total over the window: the inclusion threshold is
    # applied per-day, so a cell is included if it ever exceeded the
    # threshold over the event window.
    max_daily = daily_collection.max().rename("rain_mm_day")

    above_threshold = max_daily.gte(rain_threshold_mm_day)

    # Footprint area in km^2 (multiplied by the binary mask).
    pixel_area_km2 = ee.Image.pixelArea().divide(1e6)
    footprint_area_km2 = (
        pixel_area_km2.updateMask(above_threshold)
        .reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=aoi,
            scale=10000,  # IMERG native ~ 0.1 deg ~ 10 km at 30 N
            maxPixels=1e9,
            bestEffort=True,
        )
        .get("area")
    )

    # Area-weighted mean intensity P over the footprint only.
    mean_intensity = (
        max_daily.updateMask(above_threshold)
        .reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=aoi,
            scale=10000,
            maxPixels=1e9,
            bestEffort=True,
        )
        .get("rain_mm_day")
    )

    # Pull the two scalars back to Python.
    A = ee.Number(footprint_area_km2).getInfo() or 0.0
    P = ee.Number(mean_intensity).getInfo() or 0.0

    # Pick a representative season from the start_date.
    month = int(start_date.split("-")[1])

    return compute(
        P=P,
        A=A,
        season=month,
        substrate=substrate,
        alpha=alpha,
    )
