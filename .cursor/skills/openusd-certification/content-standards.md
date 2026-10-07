# Content Standards

## Callouts

Write callouts as Markdown blockquotes with a tag. The build converts them to boxed, labelled, grayscale panels (the label text carries the meaning, not color).

```markdown
> [!EXAM TIP] Composition is 23% of the exam — the largest domain.
> [!TRAP] "Payloads are weaker than references" is about strength order, not loading.
> [!MISTAKE] Forgetting `defaultPrim` → referencing without a prim path fails.
> [!VERSION] Verified on USD 25.xx. Before 21.02, `GetPrototype()` was `GetMaster()`.
> [!KEY] LIVERPS: Local, Inherits, VariantSets, rElocates, References, Payloads, Specializes.
> [!NOTE] Optional depth.
> [!VERIFY] Unconfirmed claim — must be resolved in Phase 15.
```

## Python code rules

- Full script: imports at top (`from pxr import Usd, Sdf, UsdGeom, ...`), no hidden setup.
- Prefer `Usd.Stage.CreateInMemory()` or write into a temp dir so scripts run anywhere.
- Deterministic output (sorted lists, fixed values) so "Expected output" stays true.
- Run with `.venv/bin/python <file>` before marking done; paste the real stdout under:

  ````markdown
  **Expected output**
  ```text
  ...
  ```
  ````

- The "Expected output" label line must sit directly above the ` ```text ` block; `scripts/check_code_blocks.py` compares them.
- Blocks that cannot run on their own (fragments, C++, deliberately broken code) use ` ```{.python .norun} ` or ` ```{.usda .norun} ` and need a one-line reason in the text.
- If behavior differs across USD versions, add a `> [!VERSION]` callout (see "Version facts" below).
- Never use APIs that are not in the installed version; check with `help()` / `dir()` if in doubt.
- Capabilities missing from `usd-core` (usdview, Hydra, usdGenSchema with C++ build): explain conceptually, show the file contents/commands, and mark "not runnable with usd-core".
- Max line length 88 chars (fits A4 code blocks at 8.5–9 pt).

## Python lab format (`python-labs/labNN_slug.md` + `.py`)

```markdown
# Lab NN — Title
**Domain / objectives:** … · **Chapter:** … · **Time:** 20–40 min · **Difficulty:** ★☆☆
## Goal
## Background (3–6 lines, self-contained)
## Steps (numbered; each step = code + what to observe)
## Full script (identical to labNN_slug.py)
## Expected output (real)
## Check your understanding (3 questions + answers)
## Stretch challenge (optional, solution at end)
```

Labs progress from ★☆☆ to ★★★. Later labs may build on files from earlier labs only if the lab recreates them itself.

## Verification scripts

Run from the project root after writing any chapter, lab write-up, or exercise file:

```bash
.venv/bin/python .cursor/skills/openusd-certification/scripts/check_code_blocks.py chapters/ch16_*.md
.venv/bin/python .cursor/skills/openusd-certification/scripts/check_usda_blocks.py chapters/ch16_*.md
.venv/bin/python python-labs/lab13_*.py
```

`check_code_blocks.py` runs each Python block in a temp directory and diffs stdout against its "Expected output". `check_usda_blocks.py` parses each USDA block (and `.usda` files) with `Sdf`. Both skip `.norun` blocks and exit non-zero on failure. A unit is not done until both pass.

## Version facts

Checked against the OpenUSD CHANGELOG on 2026-10-07 (latest release: **26.08**, 2026-07-20). Rows marked † come from an earlier session and have not been re-checked yet; confirm them before relying on them.

| Topic | Fact (release) | Book impact |
|-------|----------------|-------------|
| `UsdUtils.ComplianceChecker` | Warns when used (26.05); removed from `usdchecker` (26.03); **removed entirely (26.08)** | Never use in runnable code; mention it as legacy in a VERSION callout |
| UsdValidation framework | Introduced (24.08); Python bindings (24.11)†; separate `pxr.UsdValidation` library (25.02)† | Primary validation API in Ch 30 |
| `UsdUtils.LocalizeAsset` | Added (24.03) | OK for packaging/delivery labs |
| Relocates | Initial work (24.05); composition completed (24.08)†; in `PrimCompositionQuery` (26.03)† | Relocates lab needs a recent USD |
| UsdLux `inputs:` names | Light attributes became `inputs:intensity` etc. (21.02)† | Always use `inputs:` names |
| `MaterialBindingAPI` | Must be applied before binding; validators require it (22.11)† | Always call `UsdShade.MaterialBindingAPI.Apply(prim)` |
| `GetMaster` → `GetPrototype` | Instancing "master" renamed "prototype" (21.x)† | Use the prototype names |
| UTF-8 identifiers | UTF-8 prim/property names allowed (24.03)† | Version note in the naming chapter |
| Splines (Ts) | Introduced (24.03)†; attribute splines resolve (25.05)†; Get/SetSpline (25.08)† | Mention only; time samples remain the core encoding |

The NVIDIA study guide (Oct 2025) predates USD 26.x. Where the exam may reflect older behavior, teach the current API and describe the older one in a VERSION callout.

## USDA rules

- Begin with `#usda 1.0`; include layer metadata when relevant (`defaultPrim`, `upAxis`, `metersPerUnit`).
- Must parse: `scripts/check_usda_blocks.py` (uses `Sdf.Layer.CreateAnonymous(".usda").ImportFromString(text)`).
- Multi-file examples: label each file with a caption `File: asset.usda`.
- Keep ≤ 40 lines per block; split if longer.

## USDA reading exercises (`questions/usda_exercises.md`)

Each exercise: files shown → question ("What is the composed value of… / Which prim exists… / Why does…") → answer → explanation with the resolution path. Verify the answer by composing the files in Python.

## Question formats

ID scheme: `<DOMAIN>-<NNN>` with domains `FUN, DM, COMP, CA, DE, PD, CUST, VIS, DBG`.

```markdown
**COMP-014** · Obj 1.8 · Difficulty: Medium · Type: Single choice
<stem>
A. …
B. …
C. …
D. …

<details-free answer block placed in the "Answers" section of the file:>
**COMP-014 — Answer: C.** Explanation (why C is right, why each distractor is wrong).
```

Types and mix (the official study guide shows single-answer and "Select two/three options" items, often with USDA snippets):

| Type | Share |
|------|-------|
| Single choice (A–D) | ~60% |
| Multiple select ("Select two." / "Select three."; always state the count) | ~25% |
| USDA- or Python-reading ("What is the composed value…?", "What does this print?") | ~15% |

Rules:
- Distractors are plausible, based on real misconceptions; never "all/none of the above".
- Every question states its objective ID and difficulty: Easy = recall, Medium = apply, Hard = analyze/debug.
- Every answer is re-derived independently; code/USDA answers are confirmed by running them.
- Answers are grouped at the end of each file so the questions can be printed and practiced blind.
- Each answer cites the chapter section to review (e.g. "Review: §21.3").

## Question bank targets (weighted by blueprint, total ≈ 400)

| Domain | Weight | Bank target | Mock (per 65 Q) |
|--------|--------|-------------|-----------------|
| Composition | 23% | 92 | 15 |
| Data Exchange | 15% | 60 | 10 |
| Pipeline Development | 14% | 56 | 9 |
| Data Modeling | 13% | 52 | 8 |
| Debugging & Troubleshooting | 11% | 44 | 7 |
| Content Aggregation | 10% | 40 | 7 |
| Visualization | 8% | 32 | 5 |
| Customizing USD | 6% | 24 | 4 |

Plus a `FUN` (fundamentals) set of ~30 for beginners (not exam-weighted).

## Mock exams

- ≥ 3 papers, 65 questions each, 120-minute timer note, mix of types matching the bank.
- No question repeated verbatim from the bank; ≤ 10% overlap of concepts phrased similarly.
- Answer key file: answer, objective, explanation, "review chapter" pointer.
- Difficulty progression: Mock 1 medium, Mock 2 medium-hard, Mock 3 hard (more debugging and USDA-reading items).
- Score sheet with per-domain breakdown to feed the master plan's "Weak areas". The book's readiness target (≥ 80% on Mock 3) is its own; NVIDIA does not publish a passing score on the certification page.
- Header on every paper: "Original practice exam. Not actual NVIDIA exam content."

## Flashcards (`questions/flashcards.md`, ≥ 150)

Two-column table per domain for print cutting: `| # | Front | Back |`. Fronts are questions or terms; backs ≤ 30 words.

## Cheat sheets

Final certification checklist (`cheat-sheets/final_checklist.md`): one checkbox per official objective from `references/NVIDIA_EXAM_OBJECTIVES.md`, each with its chapter, plus exam-day logistics (ID, proctoring setup, quiet room, 120-minute pacing plan).

One A4 page each (two max): LIVERPS & value resolution, USDA syntax, Python API quick reference (per module: Usd, Sdf, UsdGeom, UsdShade, UsdLux, Gf, Vt, Tf, Ar, Kind, UsdUtils), list-editing ops, primvar interpolation, instancing decision table, debugging toolkit, file formats, command-line tools.
