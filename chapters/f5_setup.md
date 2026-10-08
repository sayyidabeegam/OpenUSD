# Setting Up Your Lab

You will run every example in this book yourself. This section takes you from an empty computer to a working OpenUSD Python setup in about 15 minutes.

## What you need

| Item | Why |
|------|-----|
| Python 3 (64-bit) | OpenUSD's Python API runs in it |
| `usd-core` package | Pixar's official OpenUSD build for Python, published on PyPI |
| A text editor | To read and edit `.usda` and `.py` files (any editor works) |
| A terminal | To run scripts |

`usd-core` supports specific Python versions. Check the "Requires" information on its PyPI page before installing. This book was verified with Python 3.12 and `usd-core` 26.8.

## Step 1: Create a project folder and a virtual environment

A **virtual environment** is a private Python installation for one project, so packages you install don't affect anything else.

**Linux and macOS:**

```{.bash .norun}
mkdir usd-study
cd usd-study
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**

```{.bash .norun}
mkdir usd-study
cd usd-study
py -m venv .venv
.venv\Scripts\Activate.ps1
```

After activation your prompt shows `(.venv)`. From now on, `python` means the Python inside this environment.

## Step 2: Install OpenUSD

```{.bash .norun}
python -m pip install usd-core
```

To install exactly the version this book was verified with:

```{.bash .norun}
python -m pip install "usd-core==26.8"
```

> [!VERSION] `usd-core` version numbers drop the leading zero of the month: package 26.8 is OpenUSD release 26.08. Inside Python, `Usd.GetVersion()` returns `(0, 26, 8)`.

## Step 3: Check the installation

Save as `check_usd.py` and run `python check_usd.py`:

```python
from pxr import Usd
print("USD version:", Usd.GetVersion())
```

**Expected output**

```text
USD version: (0, 26, 8)
```

All of OpenUSD's Python modules live in the `pxr` package. You will mostly use `Usd`, `Sdf`, `UsdGeom`, `UsdShade`, `UsdLux`, `Gf`, `Vt`, `Tf`, and `Ar`. Chapter 1 explains what each one does.

## Step 4: Your first USD file

Save as `hello.py` and run it:

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateNew("hello.usda")
world = UsdGeom.Xform.Define(stage, "/World")
ball = UsdGeom.Sphere.Define(stage, "/World/Ball")
ball.GetRadiusAttr().Set(2.0)
stage.SetDefaultPrim(world.GetPrim())
stage.GetRootLayer().Save()

print(stage.GetRootLayer().ExportToString())
```

**Expected output**

```text
#usda 1.0
(
    defaultPrim = "World"
)

def Xform "World"
{
    def Sphere "Ball"
    {
        double radius = 2
    }
}
```

The script created a file called `hello.usda` next to it. Open it in your text editor: it contains exactly the text printed above. You have just written a **scene description**: a transform called `World` holding a sphere called `Ball` with a radius of 2. Every term here (stage, prim, attribute, default prim) is explained in Chapters 2–5.

## Command-line tools and their Python stand-ins

A full OpenUSD build includes command-line tools. You will meet them in the exam and in real pipelines:

| Tool | What it does | Chapter |
|------|--------------|---------|
| `usdcat` | Prints a USD file as text, converts between formats, can flatten | 7, 31 |
| `usdtree` | Prints the prim hierarchy | 2 |
| `usdchecker` | Validates a file against OpenUSD rules | 30 |
| `usdzip` | Creates or lists `.usdz` packages | 31 |
| `usdresolve` | Shows how an asset path resolves | 33 |
| `usddiff` | Compares two USD files | 31 |
| `usdedit` | Opens any USD file as text in an editor | 7 |
| `usdview` | Interactive 3D viewer and inspector | 41, 42 |

> [!KEY] The pip package `usd-core` contains the Python modules but **none of these command-line tools**, and no `usdview`. Everything they do can also be done from Python, which is what this book does.

Typical command-line usage, for reference (**not run automatically**: needs a full OpenUSD build):

```{.bash .norun}
usdcat hello.usda                  # print as text
usdcat hello.usda -o hello.usdc    # convert to binary crate format
usdcat --flatten shot.usda -o shot_flat.usda
usdtree hello.usda
usdchecker hello.usda
usdzip hello.usdz hello.usda
```

The three small scripts below do the same jobs with `usd-core`. They are **not run automatically** because they need command-line arguments; they were run by hand against USD 26.08 with the outputs shown.

**`usdcat_lite.py`:** print or convert a layer:

```{.python .norun}
import sys
from pxr import Sdf

# Usage: python usdcat_lite.py input.usd [output.usda]
src = Sdf.Layer.FindOrOpen(sys.argv[1])
if len(sys.argv) > 2:
    src.Export(sys.argv[2])          # format chosen by the output extension
    print("wrote", sys.argv[2])
else:
    print(src.ExportToString())
```

`python usdcat_lite.py hello.usda hello.usdc` prints `wrote hello.usdc`. The new file is binary. `python usdcat_lite.py hello.usdc` prints it back as readable text, because `ExportToString()` always produces USDA text.

**`usdtree_lite.py`:** print the prim hierarchy:

```{.python .norun}
import sys
from pxr import Usd

# Usage: python usdtree_lite.py input.usd
stage = Usd.Stage.Open(sys.argv[1])
for prim in stage.Traverse():
    depth = len(prim.GetPath().GetPrefixes()) - 1
    print("  " * depth + f"{prim.GetName()} ({prim.GetTypeName()})")
```

`python usdtree_lite.py hello.usda` prints:

```text
World (Xform)
  Ball (Sphere)
```

**`usdzip_lite.py`:** package a file and its dependencies as `.usdz`:

```{.python .norun}
import sys
from pxr import UsdUtils

# Usage: python usdzip_lite.py input.usd output.usdz
ok = UsdUtils.CreateNewUsdzPackage(sys.argv[1], sys.argv[2])
print("packaged:", ok)
```

`python usdzip_lite.py hello.usda hello.usdz` prints `packaged: True`.

Validation (the `usdchecker` replacement) needs more background. It is covered with the `UsdValidation` framework in Chapter 30.

## Getting usdview (optional)

`usdview` is not required for anything in this book, and every lab works without it. It is still worth knowing because exam questions may mention it, especially its **Layer Stack** and **Composition** inspection panels (Chapter 42).

Ways to get it:

1. **NVIDIA prebuilt binaries (Windows and Linux).** NVIDIA's OpenUSD developer page (developer.nvidia.com/openusd, checked 2026-10-08) offers **USD 25.08, Python 3.12** packages for **Windows** and **Linux**. Those archives include `usdview` and the rest of the USD toolset. After extracting:

   - **Windows:** run `.\scripts\usdview_gui.bat` from the extracted folder (File → Open to load a stage). `.\scripts\usdview.bat your.usda` requires a file argument.
   - **Linux:** run `./scripts/usdview_gui.sh`. On Ubuntu, install the X11 packages listed in NVIDIA's Learn OpenUSD usdview install guide first (`libxkbcommon-x11-0` and related `libxcb-*` packages).

   The same page archives **USD 25.05, Python 3.11** for Windows and Linux. The prebuilt USD version **lags** this book's verified **26.08**; `pip install usd-core` never includes `usdview`.

2. **macOS:** NVIDIA does not currently ship a macOS prebuilt. Build OpenUSD from source with `build_usd.py` from the OpenUSD GitHub repository (Chapter 35). NVIDIA's Learn OpenUSD install notes say the same: usdview runs on macOS after you build it yourself.

3. **Build from source** on any platform if you need a viewer that matches this book's Python API (USD 26.08).

> [!VERSION] Verified 2026-10-08: NVIDIA prebuilts are USD 25.08 / Python 3.12 for Windows and Linux and include `usdview`. There is no NVIDIA macOS prebuilt. This book's labs use `usd-core` 26.8 and do not need `usdview`.

## Working folder for the labs

Keep one folder per lab so generated files don't collide:

```text
usd-study/
├── .venv/
├── check_usd.py
├── hello.py
└── labs/
    ├── lab01/
    ├── lab02/
    └── ...
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ModuleNotFoundError: No module named 'pxr'` | The virtual environment isn't active, or `usd-core` was installed into a different Python | Activate `.venv` and run `python -m pip install usd-core` again |
| `pip` reports no matching distribution | Your Python version is not supported by `usd-core`, or there is no network | Check the supported versions on PyPI and install a supported Python |
| `Usd.Stage.CreateNew` raises "A layer already exists with identifier…" | That file is **already open as a layer in the same Python session** (common in interactive shells and notebooks) | Restart Python, or use `Usd.Stage.Open` to work with the open layer |
| Your earlier content in a file disappeared | In a new Python session, `CreateNew` on an existing file starts an **empty** layer, and `Save()` replaces the file | Use `Usd.Stage.Open` to edit existing files; use `CreateNew` only for new ones |
| Script runs but no file appears | Paths are relative to the folder you ran the script **from** | `cd` into the script's folder first |

> [!MISTAKE] Running `pip install usd-core` with one Python and the script with another. Using `python -m pip ...` always installs into the same Python that `python` runs.
