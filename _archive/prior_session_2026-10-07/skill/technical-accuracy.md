# Technical Accuracy Rules and Audit

## Verification environment

Set up once (Phase 2 or earlier) and record the version in the master plan:

```bash
python3 -m venv .venv
.venv/bin/pip install usd-core
.venv/bin/python -c "from pxr import Usd; print(Usd.GetVersion())"
```

`usd-core` (PyPI) provides the `pxr` Python modules and command-line tools such as `usdcat`, `usdtree`, `usdchecker`, `usdzip`, `usddiff`, `usdresolve` (check which are on PATH in `.venv/bin`). It does **not** include `usdview` (needs a full build or NVIDIA's prebuilt binaries); describe usdview, but never make it required for a lab.

## Rules for every code example

1. Imports included (`from pxr import Usd, Sdf, UsdGeom`).
2. Runs standalone with `usd-core`; uses `Usd.Stage.CreateInMemory()` or writes files into the current directory only.
3. Prints something observable, followed by `**Expected output:**` and a ` ```text ` block matching real output.
4. Only real APIs. If unsure whether a function exists or its signature, check the API reference (openusd.org/release/api) or run `help()` in the venv before using it. When verification is impossible, mark the block `.norun` and add a `.version` callout saying it is unverified — then list it in the master plan "Open issues".
5. Version-sensitive behavior gets a `.version` callout with the version where it changed. Verified against the OpenUSD CHANGELOG on 2026-10-07 (latest release 26.08):

   | Topic | Fact (release) | Book impact |
   |-------|----------------|-------------|
   | UsdLux `inputs:` prefix | Light attributes renamed to `inputs:intensity` etc. and made connectable (21.02) | Always use `inputs:` names; mention old names exist in legacy files |
   | `MaterialBindingAPI` | ComplianceChecker began requiring it applied (22.11); binding computation expects it | Always `UsdShade.MaterialBindingAPI.Apply(prim)` before `Bind` |
   | UTF-8 identifiers | Prim, property, variant names may use UTF-8 (24.03); such files are not readable by older USD | Version note in naming chapters |
   | Splines (Ts library) | Introduced 24.03; `UsdAttribute` value resolution supports splines (25.05); `GetSpline`/`SetSpline` APIs (25.08); splines in value clips (26.08) | Mention as current feature; time samples remain the main animation encoding for the exam |
   | `UsdUtils.LocalizeAsset` | Added 24.03 | OK to use in packaging labs |
   | Relocates | Initial work 24.05; composition "completed" 24.08; exposed in `PrimCompositionQuery` 26.03 | Lab 19 requires ≥ 24.08 |
   | `UsdValidation` framework | Introduced 24.08; Python bindings 24.11; moved to `pxr.UsdValidation` library 25.02 | Primary validation API in Ch 39 |
   | `usdchecker` | Uses only `UsdValidation` since 26.03; `--arkit` deprecated | Teach current behavior |
   | `UsdUtils.ComplianceChecker` | Deprecated (warns 26.05), **removed 26.08** | Do not use in runnable code; mention historically only |
   | `SdfAnimationBlock` | Added 25.08 (blocks animation but lets weaker defaults through) | Version note in value resolution |

   The NVIDIA study guide (Oct 2025) predates 26.x. Where the exam may reflect older behavior (e.g. ComplianceChecker), teach the current API and note the older one in a `.version` callout.
6. C++-only features (file format plugins, resolvers, SceneIndex, usdGenSchema with C++ codegen): show C++/plugInfo/schema snippets as `.norun`, explain concepts fully, and give a Python-side verification when possible (e.g. `Plug.Registry`, `Usd.SchemaRegistry`, codeless schemas).

## Verification scripts

Run from the project root:

```bash
.venv/bin/python .cursor/skills/openusd-certification/scripts/check_code_blocks.py chapters/ch17_*.md
.venv/bin/python .cursor/skills/openusd-certification/scripts/check_usda_blocks.py chapters/ch17_*.md
.venv/bin/python python-labs/lab13_*.py
```

- `check_code_blocks.py` runs every ` ```python ` block in a temp directory, and compares stdout with the following "Expected output" block when present.
- `check_usda_blocks.py` parses every ` ```usda ` block with `Sdf.Layer` and reports errors.
- Both skip blocks tagged `.norun`. Exit code is non-zero on any failure.

## Phase 15 audit checklist (per Part)

```
- [ ] All python blocks pass check_code_blocks.py (record count run/skipped)
- [ ] All usda blocks pass check_usda_blocks.py
- [ ] All labs run end to end; outputs match lab write-ups
- [ ] Every .norun block justified (fragment, C++, intentionally broken)
- [ ] Every official objective in the Part is taught and tagged [Obj x.y]
- [ ] LIVERPS order, list-editing semantics, and value resolution stated consistently everywhere
- [ ] Version notes present and verified against the CHANGELOG
- [ ] Every question's answer re-derived independently; explanations match chapter text
- [ ] No claims that practice questions are real exam questions
- [ ] No essential explanation depends on an external link
- [ ] Terminology consistent with the glossary
- [ ] Print check: no meaning conveyed only by color; tables fit A4 width; code lines ≤ 88 chars
```

Record audit results in the master plan (Audit section) with file, issue, fix, status.
