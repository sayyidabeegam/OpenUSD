# Final certification checklist

**Original study aid.** Not NVIDIA exam content. Tick every objective before you book. Chapters follow this book’s TOC. Exam facts: 60–70 questions, **120 minutes**, $200, English, Certiverse remote proctor, valid 2 years. NVIDIA does **not** publish a passing score. This book: Mock 3 **≥ 80%** and **≥ 70% in every domain**.

Verified against study guide v1.1.0 and the NVIDIA certification page (2026-10-07 / 2026-10-08). Recheck logistics the week you sit.

## Exam-day logistics

- [ ] Government photo ID matching the Certiverse registration name
- [ ] System check / proctoring app installed and tested
- [ ] Quiet private room; clear desk; no second monitors or notes unless the current policy allows them
- [ ] Stable internet; charger; 120 uninterrupted minutes
- [ ] Read current NVIDIA + proctor FAQs (policies change)
- [ ] Pace plan: first pass by minute 90; ~1.8 min/question; composition (23%) not left for last
- [ ] Scratch: LIVERPS letters + layer order on USDA stems

## 1. Composition — 23% (Ch 14–22)

- [ ] **1.1** Change the strength of an opinion — Ch 14, 19, 21
- [ ] **1.2** Choose instancing style by scale — Ch 22, 26
- [ ] **1.3** References vs payloads vs sublayers — Ch 3, 15–17
- [ ] **1.4** Same animation, different layer offsets — Ch 10, 16
- [ ] **1.5** Multi-user layering / edit targets — Ch 15, 22
- [ ] **1.6** Explain LIVERPS (and LIVRPS) — Ch 14, 21
- [ ] **1.7** When variants are / are not appropriate — Ch 18
- [ ] **1.8** Why an opinion does not take effect — Ch 20–22, 42
- [ ] **1.9** Prepare an asset for external delivery — Ch 22, 34
- [ ] **1.10** Remove properties on instanced components — Ch 22, 24
- [ ] **1.11** Split a monolithic asset into workstreams — Ch 22

## 2. Content Aggregation — 10% (Ch 23–26)

- [ ] **2.1** Add a PointInstancer prototype — Ch 25
- [ ] **2.2** Tint an instance without breaking instancing — Ch 24
- [ ] **2.3** Hide PI instances efficiently (`invisibleIds`) — Ch 25
- [ ] **2.4** Native instances for large-scene reuse — Ch 23, 24, 26
- [ ] **2.5** Remove properties on instanced components — Ch 24

## 3. Customizing USD — 6% (Ch 36–38)

- [ ] **3.1** Build a plugin against a given USD ABI — Ch 35, 36
- [ ] **3.2** Build USD from source with custom deps — Ch 35
- [ ] **3.3** Custom model kinds (plugin, not `Kind.Registry.Register`) — Ch 6, 38
- [ ] **3.4** Custom schemas (`schema.usda`; parse ≠ register) — Ch 6, 37
- [ ] **3.5** Custom Ar resolver — Ch 33, 38
- [ ] **3.6** Schemas for nonstandard import/export data — Ch 37
- [ ] **3.7** Hydra SceneIndex (needs imaging build) — Ch 38
- [ ] **3.8** Resolver that generates in-memory prims — Ch 38

## 4. Data Exchange — 15% (Ch 27–31)

- [ ] **4.1** Convert to glTF / common formats; fidelity notes — Ch 27
- [ ] **4.2** Document USD ↔ other data model (e.g. MaterialX) — Ch 27
- [ ] **4.3** USDA vs USDC vs `.usd` vs USDZ — Ch 7, 31
- [ ] **4.4** DCC round-trip pipeline — Ch 27, 35
- [ ] **4.5** Nonstandard attributes/schemas on export — Ch 29, 37
- [ ] **4.6** Validator (`UsdValidation`; no `ComplianceChecker`) — Ch 30
- [ ] **4.7** Write an exporter / converter to USD — Ch 28, 29
- [ ] **4.8** Write or extend a DCC importer — Ch 29, 35

## 5. Data Modeling — 13% (Ch 8–13)

- [ ] **5.1** Add a primvar to a mesh — Ch 11
- [ ] **5.2** Choose value types / time samples — Ch 9, 10
- [ ] **5.3** Custom metadata / `customData` — Ch 5, 12
- [ ] **5.4** Retrieve prim properties — Ch 2, 4, 5, 8
- [ ] **5.5** Unexpected visual results — Ch 13, 42
- [ ] **5.6** Update `extent` after `points` — Ch 13

## 6. Debugging — 11% (Ch 42–44)

- [ ] **6.1** When `Sdf.ChangeBlock` helps (and the DefinePrim trap) — Ch 8, 34, 44
- [ ] **6.2** Why an opinion does not take effect — Ch 20, 42
- [ ] **6.3** Asset-path / resolver failures — Ch 33, 42
- [ ] **6.4** Unexpected visuals (purpose, extent, units) — Ch 13, 42, 44
- [ ] **6.5** TfDebug, delegates, Trace, MallocTag — Ch 43

## 7. Pipeline Development — 14% (Ch 32–35)

- [ ] **7.1** Convert to common 3D formats with fidelity — Ch 27
- [ ] **7.2** Document asset structure (work / publish / pin) — Ch 23, 32
- [ ] **7.3** USDA vs USDC trade-offs — Ch 7, 31
- [ ] **7.4** DCC round-trip — Ch 35
- [ ] **7.5** Custom resolvers in the pipeline — Ch 33
- [ ] **7.6** Custom metadata — Ch 12
- [ ] **7.7** Validate asset-path formatting — Ch 33
- [ ] **7.8** Extend a DCC importer — Ch 35

## 8. Visualization — 8% (Ch 39–41)

- [ ] **8.1** Add a primvar to a mesh — Ch 11, 39
- [ ] **8.2** Assign UsdPreviewSurface materials — Ch 40
- [ ] **8.3** Bind materials (`Apply` then `Bind`) — Ch 40
- [ ] **8.4** PreviewSurface that reads diffuse from a primvar — Ch 40

## Labs & papers

- [ ] Python labs 01–37 executed in `.venv`
- [ ] USDA workbook U-001–U-030
- [ ] Domain banks (430) — weakest domain reworked
- [ ] Flashcards FC-001–FC-180
- [ ] Mock 1 (≥ 70% overall) · Mock 2 (≥ 75%) · Mock 3 (≥ 80%, no domain < 70%)
- [ ] Cheat sheets on paper for the last evening (no new topics)

## 26.08 API recap (tick if you can explain each)

- [ ] `GetPrototype` / no `GetMaster`
- [ ] `OpenMasked` + `StagePopulationMask`
- [ ] `LoadNone` loads references
- [ ] `Kind.Registry` has no `Register`
- [ ] `Ar.GetResolver()` is a facade; no `AnchorRelativePath`
- [ ] `Flatten` bakes refs; `FlattenLayerStack` keeps them
- [ ] USDZ `ZIP_STORED` (0)
- [ ] `UsdValidation` imports; `ComplianceChecker` does not
- [ ] Distant intensity 50000; `inputs:intensity`
- [ ] `UsdGeom.Tokens.z` (not `.Z`)
