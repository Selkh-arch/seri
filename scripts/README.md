# Windows launchers

Double-clickable `.bat` files for users on Windows who prefer not to
open a terminal. They all live next to each other in this folder; their
working directory is auto-set to the package root, so you can copy this
whole `scripts/` folder anywhere and the launchers will still work.

| File | What it does | When to use it |
|---|---|---|
| **`install.bat`**     | First-time setup: upgrades pip, installs SERI in editable mode with the `[plot]` and `[dev]` extras, runs the test suite. | Run **once**, the first time you set up the package on a new machine. |
| **`run-gui.bat`**     | Opens the SERI calculator window (Tkinter). Pre-filled with the Abadla 2015 anchor case. | Day-to-day use for quick single-event SERI computations. |
| **`run-demo.bat`**    | Runs the bundled `examples/demo_abadla_2015.py` script in a console window. | When you want to see the full numerical demo (anchor case, sensitivity, batch, substrate mix, tier table) printed in one go. |
| **`run-notebook.bat`**| Launches Jupyter and opens `examples/notebook_demo.ipynb` in your browser. Auto-installs Jupyter the first time if needed. | When you want to walk through SERI interactively, modify cells, or generate the figures. |
| **`run-tests.bat`**   | Runs the pytest suite (73 tests). | After any local edit to the source — to confirm the Abadla 2015 anchor case still reproduces. |

## Pre-requisites

You need **Python 3.9 or later** installed on your system, with
"Add Python to PATH" enabled at install time. If `python --version`
works in `cmd`, you're set. Otherwise download and re-install Python
from [python.org/downloads](https://www.python.org/downloads/) and
**tick the "Add Python to PATH" checkbox** on the first installer
screen.

## Order of operations the very first time

1. Open this `scripts/` folder in File Explorer.
2. Double-click **`install.bat`**. A black console window opens, runs
   `pip install`, runs the tests, and prints a green success banner.
3. Press any key to close the console.
4. Now double-click **`run-gui.bat`** — the SERI calculator should open.

If anything goes wrong, the console will print an `ERROR:` line
explaining what to fix.
