# Technical audit — NCP-OUSD study book

**USD verified against:** 26.08 (`usd-core` 26.8, `Usd.GetVersion() == (0, 26, 8)`, Python 3.12.3)  
**Audit dates:** 2026-10-08  
**Scope:** Phase 15 of `00_MASTER_PLAN.md`. This file is the living findings log.

Checklist from `.cursor/skills/openusd-certification/book-build.md`:

- [x] Re-run every `.py` lab and every chapter Python block; diff against printed output
- [x] Parse every USDA block
- [x] Grep for suspicious APIs; confirm each against installed `pxr`
- [x] All `[!VERIFY]` callouts in book content resolved or removed
- [x] `[!VERSION]` callouts state the verified version (spot-checked; V-009 rows confirmed against CHANGELOG)
- [x] Every official objective (1.1–8.4) is covered by ≥ 1 chapter section, ≥ 1 lab **or** exercise, ≥ 3 questions
- [x] Question answer keys: USDA/Python checkers pass; high-risk 26.08 facts re-run (below). Exhaustive re-solve of every stem was not repeated; keys were derived on this wheel when written.
- [x] No claim that questions are real NVIDIA exam questions
- [x] Terminology consistent (LIVERPS spelling, with LIVRPS explained as the older six-arc form)
- [x] Cross-references: 1022 `§N.N` cites and 364 `Lab NN` cites in the current tree all resolve; no Ch 45+ in `chapters/` / `questions/` / `mock-exams/` / `cheat-sheets/`

---

## Checker results (2026-10-08)

| Corpus | USDA (`check_usda_blocks.py`) | Python (`check_code_blocks.py`) |
|--------|-------------------------------|----------------------------------|
| `chapters/*.md` | checked=310 skipped=1 failed=0 | ran=247 skipped=24 failed=0 mismatch=0 |
| `python-labs/*.md` | checked=0 | ran=37 skipped=0 failed=0 mismatch=0 |
| `python-labs/lab*.py` | — | **37/37 executed, exit 0** |
| `questions/*.md` | checked=41 skipped=0 failed=0 | ran=0 skipped=3 (`.norun` stems) |
| `mock-exams/*.md` | checked=40 skipped=0 failed=0 | ran=0 skipped=8 (`.norun` stems) |
| `cheat-sheets/*.md` | checked=1 skipped=0 failed=0 | ran=0 skipped=2 after A-001 |

The one skipped USDA block is the intentional override fragment in `chapters/ch25_point_instancing.md` (Exercise 25-B, tagged `.norun`).

---

## VERIFY items

| ID | Status | Resolution |
|----|--------|------------|
| V-001–V-007 | Already resolved (prior sessions) | See master plan |
| V-008 | **Resolved** | NVIDIA developer.nvidia.com/openusd (checked 2026-10-08): **USD 25.08, Python 3.12** prebuilts for **Windows and Linux** include `usdview` (`usdview_gui.bat` / `usdview_gui.sh`). Archived 25.05 / Python 3.11 also listed. **No macOS prebuilt** — build from source. Packages lag this book’s 26.08. `usd-core` never includes usdview. Labs do not need it. F5 rewritten; Ch 35 / Ch 41 mistakes updated. |
| V-009 | **Resolved** | OpenUSD CHANGELOG (release branch, 26.08 dated 2026-07-20) re-checked 2026-10-08. Dagger rows in `content-standards.md` confirmed and unmarked. See version-facts table there. |

No `[!VERIFY]` callouts remain in `chapters/`, `python-labs/`, `questions/`, `mock-exams/`, or `cheat-sheets/`. The tag still appears in the skill as the *format* definition only.

### V-009 CHANGELOG confirmations

| Topic | CHANGELOG |
|-------|-----------|
| UsdValidation | First phase / registry **24.08**; Python bindings for validator types **24.11**; moved to `pxr/usdValidation`, `UsdValidationContext` Python wrappings **25.02** |
| Relocates | Initial work **24.05**; composition completed **24.08**; relocate arcs in `PrimCompositionQuery` **26.03** |
| UsdLux `inputs:` | Light/filter inputs renamed with `inputs:` prefix **21.02** |
| `MaterialBindingAPI` | `ComplianceChecker` / bound-material computation require the API applied **22.11** |
| `GetMaster` → `GetPrototype` | “master” renamed “prototype”; `GetMaster`/`GetMasters` deprecated **20.11**; deprecated master API **removed 21.08** |
| UTF-8 identifiers | Prim/property/variant names and dictionary keys **24.03** |
| Splines (Ts) | Initial Ts library (not yet used by USD) **24.03**; `UsdAttribute` resolution / `ResolveInfoSourceSpline` **25.05**; `SdfAttributeSpec` Get/Set/ClearSpline and `UsdAttributeQuery` GetSpline/HasSpline **25.08**; clips+splines **26.08** |

---

## Suspicious-API grep

Runnable examples do **not** call removed APIs. Occurrences of `GetMaster`, `ComplianceChecker`, `Kind.Registry.Register`, and `AnchorRelativePath` are teaching (“gone”), exam distractors, or `hasattr(...)` proofs. Confirmed absent on this wheel in prior labs: `GetMaster`, `UsdUtils.ComplianceChecker`, `Kind.Registry.Register`, `Ar.Resolver.AnchorRelativePath`.

---

## Objective coverage (≥ 3 bank questions)

Counted `Obj X.Y` tags in question-bank **stems** (not answer sections). After A-004, every official objective has ≥ 3 unique bank items. CUST grew from 24 → **26** (CUST-025, CUST-026 for Obj 3.8). Bank total **432**.

Obj 3.8 had looked like “2” because CUST-017 repeated “Obj 3.8” in the stem; unique count was **1** before the fill.

Mock papers: primvar items that also satisfy Obj 8.1 were tagged only 5.1 (DM slot). Dual-tagged `Obj 5.1 / 8.1` on M1-010, M2-010, M3-017 so the coverage matrix examples match the papers.

Objectives with **no dedicated `.py` lab** (chapter exercises still exist): 3.2 (source build), 3.7 (Hydra SceneIndex), 3.8 (procedural resolver — C++), 4.2, 4.8, 7.4, 7.8. These cannot be fully exercised on `usd-core`. See A-012.

Blueprint mock mix (15/10/9/8/7/7/5/4) is unchanged.

---

## Terminology and exam-claim rules

- Book spelling is **LIVERPS**. **LIVRPS** appears only as the older six-arc label.
- Front matter, every qbank, and every mock paper state that items are **original** and **not actual NVIDIA exam content**.
- Ch 6 no longer cites an NVIDIA sample question.

---

## Findings

| ID | File | Issue | Severity | Fix | Status |
|----|------|-------|----------|-----|--------|
| A-001 | `cheat-sheets/cs_primvars.md` | Two fragment Python fences ran as full scripts (`NameError`) | Medium | Tagged `{.python .norun}` | **Fixed** |
| A-002 | `chapters/f5_setup.md` | Open `[!VERIFY]` (V-008) for usdview prebuilts; URL `developer.nvidia.com/usd` | High | Rewrote Getting usdview; NVIDIA 25.08 Win/Linux; no macOS prebuilt | **Fixed** |
| A-003 | `content-standards.md` | Version-facts rows marked † (V-009) | High | Re-checked CHANGELOG 2026-10-08; unmarked | **Fixed** |
| A-004 | `questions/qbank_customizing.md` | Obj 3.8 had one unique bank item (stem double-counted) | High | Added CUST-025, CUST-026 | **Fixed** |
| A-005 | `mock-exams/mock0{1,2,3}_paper.md` | Zero stems tagged Obj 8.1; coverage matrix pointed at 5.1 primvar items | Medium | Dual-tag M1-010, M2-010, M3-017 as `5.1 / 8.1` | **Fixed** |
| A-006 | `chapters/ch06_schemas_kinds.md` | “NVIDIA sample:” phrasing | Low | Restate `UsdAPISchemaBase` without citing a sample | **Fixed** |
| A-007 | `chapters/ch24_native_instancing.md` | `GetMaster` “renamed in 21.x” slightly imprecise | Low | 20.11 deprecate / 21.08 remove | **Fixed** |
| A-008 | `chapters/ch21_liverps_value_resolution.md` | Splines called “24.03+” (Ts existed; attributes resolved later) | Low | Aligned with Ch 10 / CHANGELOG | **Fixed** |
| A-009 | `chapters/ch30_validation.md` | UsdValidation Python timeline vague | Low | 24.08 / 24.11 / 25.02 | **Fixed** |
| A-010 | `chapters/ch35_build_dcc.md`, `ch41_usdlux.md` | “Must build imaging” omitted NVIDIA prebuilts; leftover V-008 ticket | Low | Point at F5 prebuilts | **Fixed** |
| A-011 | `chapters/f5_setup.md` | Old NVIDIA path `/usd` | Low | `developer.nvidia.com/openusd` | **Fixed** (with A-002) |
| A-012 | Coverage matrix | Seven objectives have no dedicated lab (`—`) | Info | Conceptual / C++ / build-only on this wheel; chapter exercises exist | **Accepted** |
| A-013 | Book-wide | Full § / Lab cross-reference walk | Medium | Scripted: 240 `## N.N` heads; 1022 cites ok; 364 lab cites ok | **Fixed** |
| A-014 | `questions/`, `mock-exams/` | Exhaustive re-solve of 432+195 stems | Medium | High-risk facts re-run 2026-10-08 (below). Residual: not every MCQ stem re-typed. USDA 392 parse. | **Accepted** |

---

## Part 3 — cross-refs and sampled keys (2026-10-08)

Cross-ref scanner (current tree only, not `_archive/`):

- 240 numbered section headings (`##` / `### N.N`)
- 1022 `§N.N` citations — **0 missing**
- 364 `Lab NN` citations — **0 missing** (labs 01–37)

High-risk answer-key facts re-executed on usd-core 26.8:

| Fact | Result |
|------|--------|
| `Usd.GetVersion()` | `(0, 26, 8)` |
| `GetMaster` | absent |
| `GetPrototype` | `/__Prototype_1` when a second instanceable internal reference exists |
| `UsdUtils.ComplianceChecker` | absent |
| `Kind.Registry.Register` | absent |
| `Ar.Resolver.AnchorRelativePath` | absent |
| DistantLight intensity fallback | `50000`; name `inputs:intensity` |
| Sphere radius fallback | `1` |
| `UsdGeom.Tokens.z` / `.Z` | present / absent |
| Bind without `MaterialBindingAPI.Apply` | `HasAPI` False; `material:binding` rel True |
| `CreateInMemory` upAxis / metersPerUnit | `Y` / `0.01` |
| Linear `Get(6)` with samples 0→0, 10→10 | `6.0` |
| Held `Get(6)` | `0.0` |
| Linear and held `Get(99)` | both last sample `10.0` |
| `Get()` with samples only | `None` |
| `LoadNone` | payload `IsLoaded` False; references still compose |
| `OpenMasked` | present |
| PointInstancer default `AddTarget` | `[Bush, Tree]` — not front-prepend |
| Inherit 8 vs variant 2 | composed **8** |

One-line USDA `{ double x = 8 }` still fails to parse (book already uses multiline). Native instancing requires a **second** instanceable reference before `IsInstance()` / `GetPrototype()` are live — consistent with Ch 24.

**Phase 15 complete.** Next: Phase 16 A4 PDF.
