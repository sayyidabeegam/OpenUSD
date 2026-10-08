# Cheat sheet — NCP-OUSD domains (one-pager)

**Original study aid.** Not NVIDIA exam content. Blueprint verified 2026-10-07 (re-checked 2026-10-08): **60–70 Q, 120 min, $200**, English, Certiverse, valid 2 years. Passing score **not published**. This book’s Mock 3 bar: **≥ 80%** and **≥ 70% per domain**.

## Weights (of 65)

| # | Domain | Wt | Q | Chapters | First recall |
|---|--------|----|---|----------|--------------|
| 1 | Composition | 23% | 15 | 14–22 | LIVERPS two-step; list-ops; offsets |
| 2 | Data Exchange | 15% | 10 | 27–31 | USDA/USDC/USDZ; mapping; validate |
| 3 | Pipeline | 14% | 9 | 32–35 | Work/publish/pin; Ar; Flatten vs FLS |
| 4 | Data Modeling | 13% | 8 | 8–13 | Types, samples, primvars, extent |
| 5 | Debugging | 11% | 7 | 42–44 | Stacks, Pcp errors, ChangeBlock, Trace |
| 6 | Content Aggregation | 10% | 7 | 23–26 | Native vs PI; kinds; payloads |
| 7 | Visualization | 8% | 5 | 39–41 | PreviewSurface, Bind, lights |
| 8 | Customizing USD | 6% | 4 | 36–38 | Plugin ABI, schemas, Ar, SceneIndex |

Cross-listed in the study guide (taught once): 1.10 = 2.5, 4.3 = 7.3, 5.1 = 8.1, 1.8 = 6.2, 5.3 = 7.6, 4.8 = 7.8, 3.5 = 7.5.

## 120-minute pace (~1.8 min / Q)

| Min | Do |
|-----|-----|
| 0–5 | Skim all stems; mark USDA-reading |
| 5–90 | Answer in order; flag ≤ 3 hard |
| 90–110 | Flagged + USDA/Python-reading |
| 110–120 | Domain gaps; never leave blank |

Composition first if you run short — it is 23%.

## Version landmines (26.08)

`GetPrototype` not `GetMaster` · `OpenMasked` not `Open(mask=)` · Apply then Bind · `inputs:intensity` · Distant **50000** / Sphere **1** · `Tokens.z` · no `Kind.Registry.Register` · no `AnchorRelativePath` · no `ComplianceChecker` / `UsdMtlx` / CLI in usd-core · USDZ **STORE** · `LoadNone` still loads **refs** · default `AddTarget` ≠ guaranteed front-prepend.

## “If you see X, think Y”

| Stem | Y |
|------|---|
| Two numbers, two arcs | Which **letter** is earlier? |
| Git vs farm | USDA vs USDC |
| Why isn’t my over showing? | Stack + LIVERPS + mute + edit target |
| Missing file vs missing prim | `InvalidAssetPath` vs `UnresolvedPrimPath` |
| Hide PI instances | `invisibleIds` (count unchanged) |
| Tint one instance | Instance **root**, not proxy |
| New PI proto | Explicit `ListPosition`; watch index 0 |
| Diffuse from mesh color | `PrimvarReader_float3` + `displayColor` |
| Custom physics on Mesh | `UsdAPISchemaBase` / CollisionAPI |
| Plugin in a DCC | **Same ABI** as loaded USD |

## Day plan (this book)

Days 1–4 foundations + DM · 5–7 composition · 8 CA · 9 DE · 10 PD · 11 CUST+VIS · 12 Mock 1 · 13 Mock 2 · 14 Mock 3 + cheat sheets only.
