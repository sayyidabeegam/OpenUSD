# Mock Exam 3 — Answer Key

**Original practice exam. Not actual NVIDIA exam content.**

Paper: `mock-exams/mock03_paper.md`. Verified against **USD 26.08** (`usd-core` 26.8).

Scoring: 1 point per question (multiple-select must match **all** correct letters). Total **65**. This book’s Mock 3 readiness bar is **≥ 80% (52/65)** and **≥ 70% in every domain**. NVIDIA does not publish a passing score.

---

## Score sheet

| Domain | Q IDs | /n | Your score | % |
|--------|-------|----|------------|---|
| Composition (COMP) | 001, 004, 009, 012, 016, 020, 024, 028, 032, 036, 040, 044, 049, 053, 057 | /15 | | |
| Data Exchange (DE) | 003, 011, 021, 030, 039, 046, 054, 058, 061, 064 | /10 | | |
| Pipeline Development (PD) | 006, 013, 022, 027, 035, 043, 051, 059, 065 | /9 | | |
| Data Modeling (DM) | 002, 010, 017, 025, 033, 041, 050, 060 | /8 | | |
| Debugging (DBG) | 008, 019, 029, 038, 045, 055, 063 | /7 | | |
| Content Aggregation (CA) | 005, 015, 023, 031, 042, 052, 062 | /7 | | |
| Visualization (VIS) | 007, 018, 026, 037, 047 | /5 | | |
| Customizing USD (CUST) | 014, 034, 048, 056 | /4 | | |
| **Total** | M3-001–M3-065 | **/65** | | |

Copy weakest domains into `00_MASTER_PLAN.md` §9. If any domain is under 70%, re-read that part before booking the exam.

---

## Answers

**M3-001 — Answer: B.** Obj 1.5. Verified: three sublayers, first in the list wins (`mass = 1`). Last is weakest. Review: Ch 15.

**M3-002 — Answer: B.** Obj 5.5. Verified: `Get(99)` is `(10, 0, 0)` for **both** held and linear — past the last sample, linear does not extrapolate. Review: Ch 10.

**M3-003 — Answer: B.** Obj 4.5. Verified: `GetIntensityAttr().GetName()` is **`inputs:intensity`**. Review: Ch 41.

**M3-004 — Answer: B.** Obj 1.1. Verified: inherit `8` beats selected variant `2`. Inherits > VariantSets. Review: Ch 19, Ch 21.

**M3-005 — Answer: B.** Obj 2.4. Verified: `SetInstanceable(False)` de-instances; `/Vise/Body` is defined and not a proxy. Review: Ch 24.

**M3-006 — Answer: A, B.** Obj 7.5. Verified: mute strongest sublayer → composed `2`; `GetLayerStack()` **omits** the muted layer; `GetMutedLayers()` lists it. Review: Ch 15, Ch 42.

**M3-007 — Answer: B.** Obj 8.4. Verified: `ComputeSurfaceSource` length **3**; index 0 is the connected shader (`/M/PBR`). Review: Ch 40.

**M3-008 — Answer: A.** Obj 6.5. Verified: `DefinePrim` resyncs `/N`; attribute `Set` is **changed-info-only** `/N.f`. Review: Ch 34, Lab 30.

**M3-009 — Answer: B.** Obj 1.1. Verified: weaker-sublayer **local** `2` beats stronger-sublayer **inherit** `8`. Local is the strongest *arc*, not “the strongest sublayer’s arc.” Review: Ch 21.

**M3-010 — Answer: B.** Obj 5.6. Verified: extent `[(0, 0, 0), (2, 3, 0)]`. Review: Ch 13.

**M3-011 — Answer: B.** Obj 4.5. Custom namespaced attributes persist without a downstream schema plugin. Review: Ch 29, Ch 37.

**M3-012 — Answer: B.** Obj 1.8. Verified: relocates keys must be **composed paths** (`</Mill/Rig/Arm>`). `</World/Mill/...>` is ignored. `/Mill/Rig/Arm` remains `size` 1; `over "Arm"` is a sibling at `/Mill/Arm` with 7. Review: Ch 20.

**M3-013 — Answer: B.** Obj 7.2. Verified: `GetPrimStack` strongest first: root, then `s1`, then `s2`. Review: Ch 22, Ch 42.

**M3-014 — Answer: A.** Obj 3.6. Verified: `UsdPhysics.CollisionAPI.Apply` exists on usd-core 26.8. There is no `UsdPhysicsBase` / `Kind.Register` shortcut. Review: Ch 35, Ch 37.

**M3-015 — Answer: A, C.** Obj 2.3. `invisibleIds` masks drawing; count stays 4. Review: Ch 25.

**M3-016 — Answer: B.** Obj 1.3. Verified: with a **local over** of `Ball`, `/Heavy/Ball` exists and `radius = 5` even under `LoadNone`. (Without that over, the payload child is missing.) Review: Ch 17, Ch 20.

**M3-017 — Answer: B.** Obj 5.1 / 8.1. `FindPrimvarWithInheritance`. Review: Ch 11.

**M3-018 — Answer: A, B.** Obj 8.2. Namespaced intensity; LightAPI built-in; ShadowAPI needs Apply. Review: Ch 41.

**M3-019 — Answer: B.** Obj 6.3. Verified: explicit `@file@</Beta>` composes `k = 2` even with no defaultPrim. (A nameless `@file@` would be UnresolvedPrimPath / defaultPrim.) Review: Ch 16.

**M3-020 — Answer: B.** Obj 1.4. `composed = offset + scale * layerTime` → `4 + 1*10 = 14`. Review: Ch 10, Ch 16.

**M3-021 — Answer: A, B.** Obj 4.6. Verified pattern: resolved textures in **assets**; missing files in **unresolved**. Review: Ch 32.

**M3-022 — Answer: B.** Obj 7.4. Verified: `GetEditTargetForLocalLayer` maps stage t=20 through offset 10 → stored at **10**. Review: Ch 15, Lab 19.

**M3-023 — Answer: B.** Obj 2.2. Instance-root primvars. Proxy OverridePrim raises. Prototype edits tint everyone. Review: Ch 24.

**M3-024 — Answer: B.** Obj 1.7. Verified: shot `variants = { size = "lg" }` yields `span = 8`, beating the asset’s `sm`. Review: Ch 18.

**M3-025 — Answer: A, B.** Obj 5.4. Verified: `GetTargets()` stays `/B.r`; `GetForwardedTargets()` walks to `/C`. Review: Ch 5.

**M3-026 — Answer: B.** Obj 8.3. Bind on the Subset; parent often `weakerThanDescendants`. Review: Ch 40.

**M3-027 — Answer: B.** Obj 7.3. Flatten **bakes** references (external delivery). FlattenLayerStack **keeps** them. Review: Ch 22, Ch 34.

**M3-028 — Answer: B.** Obj 1.9. Localize/flatten, pin, defaultPrim. Do not ship live `hero://` work URIs. Review: Ch 22, Ch 32.

**M3-029 — Answer: B.** Obj 6.2. The stack lists contributing specs **strongest first** for debugging; composition already chose local `2`. Review: Ch 42.

**M3-030 — Answer: B.** Obj 4.2. `UsdMtlx` ImportError on usd-core; the mapping table is still required. Review: Ch 27.

**M3-031 — Answer: A, C.** Obj 2.4. Verified: assembly `IsGroup()` **True**, `IsComponent()` **False**. Review: Ch 6, Ch 23.

**M3-032 — Answer: A, B.** Obj 1.6. I > V; L > I (even weak-stack local). Specializes lose to references. E is relocates. Review: Ch 21.

**M3-033 — Answer: A, B.** Obj 5.2. Verified: after Set*, upAxis **Z**, metersPerUnit **1.0**. Review: Ch 2, Ch 13.

**M3-034 — Answer: B.** Obj 3.1. Plug registry + `schema.usda` resources; parse ≠ register. Review: Ch 36, Ch 37.

**M3-035 — Answer: B.** Obj 7.6. `customData`. Review: Ch 12.

**M3-036 — Answer: B.** Obj 1.2. Native instances vs PointInstancer scale. Review: Ch 24, Ch 26.

**M3-037 — Answer: B.** Obj 8.3. `weakerThanDescendants` → child/subset bind wins. (Mock 2 asked the inverse strength.) Review: Ch 40.

**M3-038 — Answer: B.** Obj 6.4. Stale extent after points change. Review: Ch 13, Ch 42.

**M3-039 — Answer: A, C.** Obj 4.4. Hyphens become underscores; keep original in customData; author defaultPrim and units. Review: Ch 29.

**M3-040 — Answer: B.** Obj 1.1. Verified: inherit broadcasts `0.9` to both `/A` and `/B`. Review: Ch 19.

**M3-041 — Answer: B.** Obj 5.3. customData vs comment/documentation fields. Review: Ch 12.

**M3-042 — Answer: B.** Obj 2.1. `BackOfAppendList` keeps index 0. Default `AddTarget` is **not** FrontOfPrependList on 26.08. Review: Ch 25.

**M3-043 — Answer: A, C.** Obj 7.7. Layer-relative check; cwd `Resolve("./…")` is the classic false negative. `AnchorRelativePath` is gone. Review: Ch 33.

**M3-044 — Answer: B.** Obj 1.7. Empty `GetVariantEditContext` authors **local**. Review: Ch 18.

**M3-045 — Answer: B.** Obj 6.1. New-child `DefinePrim` inside ChangeBlock can raise. Review: Ch 34, Ch 44.

**M3-046 — Answer: B.** Obj 4.8. Crate magic `PXR-USDC`, formatId **`usd`** for `.usd`. Review: Ch 7, Ch 31.

**M3-047 — Answer: B.** Obj 8.4. `UsdPrimvarReader_float3` + `displayColor`. Review: Ch 40.

**M3-048 — Answer: B.** Obj 3.7. No UsdImaging/Hd in usd-core. Review: Ch 38.

**M3-049 — Answer: A, B.** Obj 1.5. Verified: session `9` wins; root still has `1`. Review: Ch 2, Ch 15.

**M3-050 — Answer: B.** Obj 5.5. Get → `inherited`; Compute → `invisible`. Review: Ch 13.

**M3-051 — Answer: B.** Obj 7.1. No CLI `usdzip`; `CreateNewUsdzPackage` (STORE). Hand-zip with DEFLATE is **not** USDZ-legal. Review: Ch 31.

**M3-052 — Answer: B.** Obj 2.5. Broken model chain → `IsComponent()` False. Review: Ch 6, Ch 23.

**M3-053 — Answer: A, B.** Obj 1.11. Payload + department sublayers + pin. Review: Ch 22.

**M3-054 — Answer: B.** Obj 4.3. Git USDA / farm USDC. Review: Ch 31.

**M3-055 — Answer: B.** Obj 6.2. Same fact as M3-004, debug framing: inherit hides the variant until you author **local**. Review: Ch 21, Ch 42.

**M3-056 — Answer: A, B.** Obj 3.5. Ar plugin + facade. No Registry.Register; no AnchorRelativePath. Review: Ch 33, Ch 38.

**M3-057 — Answer: B.** Obj 1.10. Instance root (or de-instance that root). Review: Ch 24.

**M3-058 — Answer: B.** Obj 4.1. Bake the working set for glTF. Review: Ch 27.

**M3-059 — Answer: A, B.** Obj 7.8. Typed mapping + payloads. No UsdMtlx/GetMaster. Review: Ch 35.

**M3-060 — Answer: A.** Obj 5.2. One triangle: counts length **1**, indices length **3**. Review: Ch 11, Ch 13.

**M3-061 — Answer: B.** Obj 4.3. ZIP_STORED (0). Review: Ch 31.

**M3-062 — Answer: B, C.** Obj 2.4. Verified: not a Gprim; is Boundable. Review: Ch 25.

**M3-063 — Answer: B.** Obj 6.5. Delegate **before** Open. Review: Ch 43.

**M3-064 — Answer: A, B.** Obj 4.7. defaultPrim + units/upAxis. Review: Ch 28.

**M3-065 — Answer: B.** Obj 7.2. Extract = one file; Compute = closure. Review: Ch 32.

---

## Domain repair

| If weak in | Re-read | Re-lab |
|------------|---------|--------|
| COMP | Ch 14–22 (especially §21 LIVERPS puzzles) | Labs 13–21 |
| DE | Ch 27–31 | Labs 25–28 |
| PD | Ch 32–35 | Labs 29–30 |
| DM | Ch 8–13 | Labs 08–12 |
| DBG | Ch 42–44 | Labs 09, 30, 36 |
| CA | Ch 23–26 | Labs 22–24 |
| VIS | Ch 39–41 | Labs 33–35 |
| CUST | Ch 36–38 | Lab 31 |

If Mock 3 is under 80% overall or any domain is under 70%, add review days before booking. NVIDIA does not publish a passing score.
