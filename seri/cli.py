"""
seri.cli
========

Command-line interface for the SERI package.

After ``pip install seri`` (or ``pip install -e .`` from the repo), the
console script ``seri`` becomes available on PATH:

.. code-block:: bash

    seri compute --P 10.79 --A 1624 --month 2 --substrate mixed
    seri demo
    seri tiers
    seri gui
    seri info

The CLI is intentionally minimal: the public Python API
(``seri.compute(...)``) remains the canonical entry point; the CLI is a
convenience layer on top of it for users who prefer a terminal or a
double-clickable launcher.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from . import __version__
from .core import DEFAULT_ALPHA, compute
from .tiers import tier_table


# ---------------------------------------------------------------------------
# Subcommand: compute
# ---------------------------------------------------------------------------
def _cmd_compute(args: argparse.Namespace) -> int:
    """Compute SERI for a single event from CLI flags."""
    try:
        result = compute(
            P=args.P,
            A=args.A,
            season=args.month,
            substrate=args.substrate,
            alpha=args.alpha,
        )
    except (ValueError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(f"SERI value:    {result.value:.2f}")
        print(f"Tier:          {result.tier.name}  ({result.tier_name})")
        print(f"Description:   {result.tier_description}")
        print()
        print(f"Inputs:        P = {result.P} mm, A = {result.A} km^2")
        print(f"Coefficients:  alpha = {result.alpha}, "
              f"f = {result.f}, g = {result.g}")
    return 0


# ---------------------------------------------------------------------------
# Subcommand: demo
# ---------------------------------------------------------------------------
def _cmd_demo(args: argparse.Namespace) -> int:
    """Run the bundled Abadla 2015 demo."""
    # Import lazily so the CLI starts fast on plain `seri --help`.
    import runpy
    from pathlib import Path

    demo_path = Path(__file__).parent.parent / "examples" / "demo_abadla_2015.py"
    if not demo_path.is_file():
        # When installed as a wheel, the examples folder is not part of the
        # installed package; fall back to an inline reproduction of the
        # anchor case so the demo still runs.
        result = compute(P=10.79, A=1624, season=2, substrate="mixed")
        print("Abadla 2015 anchor case (inline fallback):")
        print(f"  SERI = {result.value:.1f}  ->  {result.tier_name}")
        print()
        print("Tip: clone the repository (https://github.com/cselkh/seri)")
        print("for the full multi-section demo script.")
        return 0
    runpy.run_path(str(demo_path), run_name="__main__")
    return 0


# ---------------------------------------------------------------------------
# Subcommand: tiers
# ---------------------------------------------------------------------------
def _cmd_tiers(args: argparse.Namespace) -> int:
    """Print the six operational tiers (manuscript Table 1)."""
    rows = tier_table()
    print("The six operational tiers (manuscript Table 1):\n")
    for name, lo, hi, label in rows:
        bound = f">= {lo:g}" if hi == float("inf") else f"[{lo:g}, {hi:g})"
        print(f"  {name:<10s}  {bound:<18s}  {label}")
    return 0


# ---------------------------------------------------------------------------
# Subcommand: gui
# ---------------------------------------------------------------------------
def _cmd_gui(args: argparse.Namespace) -> int:
    """Launch the bundled Tkinter GUI."""
    try:
        from .gui import main as gui_main
    except ImportError as exc:
        print(f"error: cannot launch GUI: {exc}", file=sys.stderr)
        return 1
    return gui_main()


# ---------------------------------------------------------------------------
# Subcommand: info
# ---------------------------------------------------------------------------
def _cmd_info(args: argparse.Namespace) -> int:
    """Print package and citation info."""
    print(f"SERI - Spatial Effective Rainfall Index")
    print(f"Version:  {__version__}")
    print(f"License:  Apache 2.0")
    print()
    print("Cite this software:")
    print("  Selkh, C. (2026). SERI - Spatial Effective Rainfall Index")
    print("  [Computer software]. Zenodo. doi:10.5281/zenodo.PLACEHOLDER_SERI")
    print()
    print("Cite the concept paper:")
    print("  Selkh, C. (2026). A Century After De Martonne: Why Spatial")
    print("  Coherence is the Missing Dimension of Aridity in the")
    print("  Hyper-Arid Sahara. Earth-Science Reviews, in review.")
    return 0


# ---------------------------------------------------------------------------
# Parser construction
# ---------------------------------------------------------------------------
def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="seri",
        description=(
            "Spatial Effective Rainfall Index - "
            "compute SERI for hyper-arid rainfall events."
        ),
    )
    parser.add_argument(
        "--version", action="version", version=f"seri {__version__}"
    )
    sub = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")

    # compute -----------------------------------------------------------------
    p_compute = sub.add_parser(
        "compute",
        help="Compute SERI for a single event from input parameters.",
        description=(
            "Compute SERI for a single rainfall event. "
            "Reproduces the Abadla 2015 anchor case with the default "
            "values: --P 10.79 --A 1624 --month 2 --substrate mixed."
        ),
    )
    p_compute.add_argument(
        "--P", type=float, required=True,
        help="Event mean intensity over the footprint (mm).",
    )
    p_compute.add_argument(
        "--A", type=float, required=True,
        help="Contiguous area receiving rainfall above 5 mm/day (km^2).",
    )
    p_compute.add_argument(
        "--month", type=int, required=True, choices=range(1, 13), metavar="1..12",
        help="Month number (1=January, 12=December).",
    )
    p_compute.add_argument(
        "--substrate", type=str, required=True,
        choices=["hamada", "reg", "erg", "wadi_bottom", "sebkha", "mixed"],
        help="Substrate label.",
    )
    p_compute.add_argument(
        "--alpha", type=float, default=DEFAULT_ALPHA,
        help=f"Sub-linear spatial exponent (default {DEFAULT_ALPHA}).",
    )
    p_compute.add_argument(
        "--json", action="store_true",
        help="Output as JSON instead of human-readable text.",
    )
    p_compute.set_defaults(func=_cmd_compute)

    # demo --------------------------------------------------------------------
    p_demo = sub.add_parser(
        "demo",
        help="Run the bundled Abadla 2015 demonstration script.",
    )
    p_demo.set_defaults(func=_cmd_demo)

    # tiers -------------------------------------------------------------------
    p_tiers = sub.add_parser(
        "tiers",
        help="Print the six operational tiers and their bounds.",
    )
    p_tiers.set_defaults(func=_cmd_tiers)

    # gui ---------------------------------------------------------------------
    p_gui = sub.add_parser(
        "gui",
        help="Launch the bundled Tkinter graphical interface.",
    )
    p_gui.set_defaults(func=_cmd_gui)

    # info --------------------------------------------------------------------
    p_info = sub.add_parser(
        "info",
        help="Print version and citation information.",
    )
    p_info.set_defaults(func=_cmd_info)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Entry point for the ``seri`` console script."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
