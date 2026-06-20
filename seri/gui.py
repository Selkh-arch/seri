"""
seri.gui
========

Minimal Tkinter graphical interface for SERI.

The GUI is intentionally tiny: one window, the four required inputs
(P, A, month, substrate), an optional alpha override, a "Compute" button
and a coloured result panel showing the SERI value, the tier and the
description.

Tkinter is part of the Python standard library on all major platforms
(it ships with the official Windows installer), so this GUI adds no new
dependency.

Launch with:

    seri gui                # (after pip install seri)
    python -m seri.gui      # works without console-script entry point
"""

from __future__ import annotations

import sys

from . import __version__
from .core import DEFAULT_ALPHA, compute
from .tiers import Tier


# Colour palette, kept consistent with seri.plotting.TIER_COLOURS.
_TIER_COLOURS = {
    Tier.INERT:     "#a83232",
    Tier.MICROBIAL: "#d97a4f",
    Tier.ANNUAL:    "#e8b94f",
    Tier.PERENNIAL: "#7fb04f",
    Tier.WADI:      "#3f8f3f",
    Tier.REGIONAL:  "#1f5e1f",
}

_MONTHS = [
    ("1 - January",   1),
    ("2 - February",  2),
    ("3 - March",     3),
    ("4 - April",     4),
    ("5 - May",       5),
    ("6 - June",      6),
    ("7 - July",      7),
    ("8 - August",    8),
    ("9 - September", 9),
    ("10 - October",  10),
    ("11 - November", 11),
    ("12 - December", 12),
]

_SUBSTRATES = [
    ("hamada (crusted plateau, g = 0.55)",          "hamada"),
    ("reg (desert pavement, g = 0.85)",             "reg"),
    ("erg (sandy dunes, g = 1.25)",                 "erg"),
    ("wadi-bottom (alluvial fines, g = 1.60)",      "wadi_bottom"),
    ("sebkha (saline depression, g = 0.30)",        "sebkha"),
    ("mixed (reg + wadi-bottom, g = 1.10)",         "mixed"),
]


def main() -> int:
    """Launch the GUI. Returns 0 on normal exit, 1 on Tkinter import failure."""
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox
    except ImportError as exc:  # pragma: no cover - very rare on Windows
        print(
            f"error: tkinter is not available ({exc}). "
            "On Linux you may need to install python3-tk; on Windows "
            "tkinter ships with the standard Python installer.",
            file=sys.stderr,
        )
        return 1

    root = tk.Tk()
    root.title(f"SERI - Spatial Effective Rainfall Index (v{__version__})")
    root.minsize(560, 460)

    # ttk theming for a less-1995 look.
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:  # pragma: no cover
        pass
    style.configure("Title.TLabel", font=("TkDefaultFont", 14, "bold"))
    style.configure("Tier.TLabel", font=("TkDefaultFont", 13, "bold"))
    style.configure("Value.TLabel", font=("TkDefaultFont", 22, "bold"))

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------
    header = ttk.Frame(root, padding=(12, 10))
    header.pack(fill="x")
    ttk.Label(
        header,
        text="Spatial Effective Rainfall Index",
        style="Title.TLabel",
    ).pack(anchor="w")
    ttk.Label(
        header,
        text="Selkh (2026) - Earth-Science Reviews, in review",
        foreground="#555",
    ).pack(anchor="w")

    # ------------------------------------------------------------------
    # Inputs
    # ------------------------------------------------------------------
    inputs = ttk.LabelFrame(root, text="Event parameters", padding=12)
    inputs.pack(fill="x", padx=12, pady=(0, 8))

    # P
    ttk.Label(inputs, text="P  (mean intensity, mm):").grid(
        row=0, column=0, sticky="w", padx=4, pady=4)
    var_P = tk.StringVar(value="10.79")
    ttk.Entry(inputs, textvariable=var_P, width=12).grid(
        row=0, column=1, sticky="w", padx=4)

    # A
    ttk.Label(inputs, text="A  (contiguous area, km^2):").grid(
        row=1, column=0, sticky="w", padx=4, pady=4)
    var_A = tk.StringVar(value="1624")
    ttk.Entry(inputs, textvariable=var_A, width=12).grid(
        row=1, column=1, sticky="w", padx=4)

    # Month
    ttk.Label(inputs, text="Month:").grid(
        row=2, column=0, sticky="w", padx=4, pady=4)
    var_month = tk.StringVar(value=_MONTHS[1][0])  # February default (Abadla)
    month_cb = ttk.Combobox(
        inputs, textvariable=var_month, width=20,
        values=[m[0] for m in _MONTHS], state="readonly",
    )
    month_cb.grid(row=2, column=1, sticky="w", padx=4)

    # Substrate
    ttk.Label(inputs, text="Substrate:").grid(
        row=3, column=0, sticky="w", padx=4, pady=4)
    var_sub = tk.StringVar(value=_SUBSTRATES[5][0])  # 'mixed' default
    sub_cb = ttk.Combobox(
        inputs, textvariable=var_sub, width=40,
        values=[s[0] for s in _SUBSTRATES], state="readonly",
    )
    sub_cb.grid(row=3, column=1, columnspan=2, sticky="w", padx=4)

    # Alpha (advanced)
    ttk.Label(inputs, text="alpha  (advanced; default 0.68):").grid(
        row=4, column=0, sticky="w", padx=4, pady=4)
    var_alpha = tk.StringVar(value=str(DEFAULT_ALPHA))
    ttk.Entry(inputs, textvariable=var_alpha, width=12).grid(
        row=4, column=1, sticky="w", padx=4)
    ttk.Label(
        inputs, text="(working value pending formal calibration; Selkh, in prep.)",
        foreground="#777",
    ).grid(row=5, column=0, columnspan=3, sticky="w", padx=4)

    # ------------------------------------------------------------------
    # Result panel
    # ------------------------------------------------------------------
    result_frame = ttk.LabelFrame(root, text="Result", padding=12)
    result_frame.pack(fill="both", expand=True, padx=12, pady=(0, 8))

    var_value = tk.StringVar(value="-")
    var_tier = tk.StringVar(value="(enter values and click Compute)")
    var_desc = tk.StringVar(value="")
    var_coeffs = tk.StringVar(value="")

    ttk.Label(result_frame, text="SERI:").grid(row=0, column=0, sticky="w")
    lbl_value = ttk.Label(result_frame, textvariable=var_value, style="Value.TLabel")
    lbl_value.grid(row=0, column=1, sticky="w", padx=8)

    lbl_tier = ttk.Label(result_frame, textvariable=var_tier, style="Tier.TLabel")
    lbl_tier.grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))

    ttk.Label(
        result_frame, textvariable=var_desc,
        wraplength=500, foreground="#333",
    ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(4, 0))

    ttk.Label(
        result_frame, textvariable=var_coeffs,
        foreground="#666",
    ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(8, 0))

    # ------------------------------------------------------------------
    # Compute action
    # ------------------------------------------------------------------
    def _selected_month() -> int:
        label = var_month.get()
        for lbl, m in _MONTHS:
            if lbl == label:
                return m
        return 2  # fallback

    def _selected_substrate() -> str:
        label = var_sub.get()
        for lbl, s in _SUBSTRATES:
            if lbl == label:
                return s
        return "mixed"

    def _do_compute() -> None:
        try:
            P = float(var_P.get().replace(",", "."))
            A = float(var_A.get().replace(",", "."))
            alpha = float(var_alpha.get().replace(",", "."))
        except ValueError:
            messagebox.showerror(
                "Invalid input",
                "P, A and alpha must be numbers (use a dot or comma as decimal "
                "separator).",
            )
            return

        try:
            r = compute(
                P=P, A=A,
                season=_selected_month(),
                substrate=_selected_substrate(),
                alpha=alpha,
            )
        except (ValueError, TypeError) as exc:
            messagebox.showerror("Invalid input", str(exc))
            return

        var_value.set(f"{r.value:,.1f}".replace(",", " "))
        var_tier.set(f"{r.tier_name}  ({r.tier.name})")
        var_desc.set(r.tier_description)
        var_coeffs.set(
            f"f(season) = {r.f}    g(substrate) = {r.g}    alpha = {r.alpha}"
        )
        lbl_tier.configure(foreground=_TIER_COLOURS.get(r.tier, "#000"))
        lbl_value.configure(foreground=_TIER_COLOURS.get(r.tier, "#000"))

    def _do_reset() -> None:
        var_P.set("10.79")
        var_A.set("1624")
        var_month.set(_MONTHS[1][0])
        var_sub.set(_SUBSTRATES[5][0])
        var_alpha.set(str(DEFAULT_ALPHA))
        var_value.set("-")
        var_tier.set("(enter values and click Compute)")
        var_desc.set("")
        var_coeffs.set("")
        lbl_tier.configure(foreground="#000")
        lbl_value.configure(foreground="#000")

    # ------------------------------------------------------------------
    # Buttons
    # ------------------------------------------------------------------
    btns = ttk.Frame(root, padding=(12, 0, 12, 12))
    btns.pack(fill="x")
    ttk.Button(btns, text="Compute SERI", command=_do_compute).pack(
        side="left", padx=(0, 8))
    ttk.Button(btns, text="Reset to Abadla 2015 defaults",
               command=_do_reset).pack(side="left", padx=(0, 8))
    ttk.Button(btns, text="Quit", command=root.destroy).pack(side="right")

    # Status bar (citation reminder).
    status = ttk.Label(
        root,
        text=("Cite: Selkh, C. (2026). SERI - Spatial Effective Rainfall Index. "
              "Zenodo. doi:10.5281/zenodo.20478949"),
        foreground="#666", padding=(12, 4),
    )
    status.pack(fill="x", side="bottom")

    # Compute Abadla 2015 immediately so the window opens with a populated result.
    _do_compute()
    # Allow Enter key to recompute.
    root.bind("<Return>", lambda _e: _do_compute())

    root.mainloop()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
