# Question Bank — Pipeline Development (PD)

**Original practice questions.** Not actual NVIDIA exam content. Mapped to NCP-OUSD study-guide objectives 7.1–7.8 (Pipeline Development, 14%).

Verified against **USD 26.08** (`usd-core` 26.8). Domain target: 56 questions. This file currently holds **PD-001–PD-056** (domain complete).

Work the stems first. Answers and explanations are grouped at the end.

---

**PD-001** · Obj 7.2 · Difficulty: Easy · Type: Single choice

In a USD pipeline, what is the difference between a **work** file and a **publish**?

A. Work files are USDC; publishes are USDA
B. A work file is still being edited; a publish is an immutable snapshot other assets may **pin**
C. Publishes live only in the session layer
D. Work files cannot contain references

---

**PD-002** · Obj 7.2 · Difficulty: Medium · Type: Single choice

A shot references `assets/chair/work/chair.usda`. What guideline does that violate?

A. Relative paths are illegal
B. Shots should pin a **published version** (for example `assets/chair/v017/chair.usda`), not a work tree that still changes
C. Chairs may only be payloads
D. Version numbers must appear in the prim name `/Chair_v017`

---

**PD-003** · Obj 7.2 · Difficulty: Medium · Type: Single choice

`defaultPrim = "Hero_v003"` on a published component. What is wrong?

A. `defaultPrim` is illegal on components
B. Version belongs in the **folder** (and maybe `assetInfo['version']`); the identifier/`defaultPrim` should stay stable (`Hero`)
C. `v003` must be uppercase
D. `defaultPrim` must match the filename only, never the prim

---

**PD-004** · Obj 7.2 · Difficulty: Easy · Type: Single choice

`assetInfo['identifier'] = "chair"` should change when?

A. Every publish (`chair_v002`, then `chair_v003`)
B. Almost never — it is the catalog key for the asset
C. Whenever the USDA comment changes
D. Only when flattening

---

**PD-005** · Obj 7.2 · Difficulty: Medium · Type: Multiple select
Select two.

Obj 7.2 asks you to **document** asset structure. Which artifacts belong in that guideline pack?

A. Folder tree, layer-stack diagram (strongest first), prim/kind tree, ownership table
B. A private mental model the lead TD keeps
C. Pin rules (work vs publish) and naming (`Tf.MakeValidIdentifier`)
D. NVIDIA’s live exam PDF reprinted as the studio bible

---

**PD-006** · Obj 7.2 · Difficulty: Medium · Type: Single choice

ASWF-style structure for a chair component typically includes what?

A. One monolithic USDA with every shot’s animation inside
B. A thin interface layer (`defaultPrim`, payload/reference to contents), plus geometry/material layers
C. A PointInstancer of every vertex
D. No `kind` — kinds are only for assemblies

---

**PD-007** · Obj 7.2 · Difficulty: Medium · Type: Single choice

`UsdUtils.ComputeAllDependencies("entry.usda")` returns what?

A. A dict `{layers, assets, unresolved}`
B. A **3-tuple** `(layers, assets, unresolved)` walked **recursively**
C. Only unresolved paths
D. Prim paths in traverse order

---

**PD-008** · Obj 7.2 · Difficulty: Medium · Type: Single choice

`ExtractExternalReferences("shot.usda")` returns `(['./anim.usda', './layout.usda'], [], [])`. Does that prove the shot has no textures?

A. Yes — empty second list means no assets exist anywhere
B. No — extract is **one file**; textures on `layout.usda` never appear. Run `ComputeAllDependencies`
C. Yes if the shot is USDA
D. Extract always recurses into sublayers

---

**PD-009** · Obj 7.2 · Difficulty: Medium · Type: Multiple select
Select two.

Which statements about the two inventory APIs are true?

A. Extract: `(sublayers, refs+assets, payloads)` for **one** layer’s authored strings
B. Compute: recursive `(layers, assets, unresolved)`; payloads **are** followed
C. Missing files abort Compute with `Tf.ErrorException` and no tuple
D. Extract’s second list is USD references only — never `.png`

---

**PD-010** · Obj 7.2 · Difficulty: Easy · Type: Single choice

On a layer-stack diagram labeled “strongest at top,” lighting is drawn **below** layout, but the caption says lighting overrides layout translates. The caption is:

A. True, because lighting works later in the schedule
B. False — below means weaker; first-listed / top of the strength diagram wins
C. True if lighting uses `def`
D. True because payloads beat sublayers

---

**PD-011** · Obj 7.2 · Difficulty: Medium · Type: Single choice

Two layout artists overwrite the same `shot.usdc` all day. What pipeline split fixes it?

A. Git rebase on USDC
B. Department **sublayers** (`layout.usda`, `anim.usda`, …) with one owner per file; stronger departments listed first
C. Native instancing of the shot
D. Flatten every hour

---

**PD-012** · Obj 7.3 · Difficulty: Easy · Type: Single choice

A pipeline stores **WIP department layers** in Git and **farm caches** on a render share. Encoding policy?

A. Git: USDC; farm: USDA
B. Git: USDA (diff/merge); farm: USDC (I/O)
C. Always USDZ
D. Encoding does not matter in a pipeline

---

**PD-013** · Obj 7.3 · Difficulty: Medium · Type: Single choice

A publish job writes `chair.usd` via `CreateNew`. Reviewers assume it is text because the extension is not `.usdc`. What should the pipeline check?

A. Extension only
B. Magic bytes (`PXR-USDC` vs `#usda`); `formatId` for `.usd` is `usd`, not the encoding name
C. `FindByExtension("usd")` equals `usdc`
D. Git says “binary” so it must be USDA

---

**PD-014** · Obj 7.5 · Difficulty: Easy · Type: Single choice

`Ar.GetResolver()` vs `Ar.GetUnderlyingResolver()` on usd-core 26.8?

A. Both return `DefaultResolver`
B. Facade **`Resolver`**; underlying **`DefaultResolver`**
C. Facade `DefaultResolver`; underlying `Resolver`
D. Both return `None` until a stage is open

---

**PD-015** · Obj 7.5 · Difficulty: Medium · Type: Single choice

`hasattr(Ar.GetResolver(), "AnchorRelativePath")` on USD 26.08?

A. `True` — that is the supported anchor API
B. `False` — use `CreateIdentifier(path, ResolvedPath(layer.realPath))` or `layer.ComputeAbsolutePath`
C. `True` only inside `ResolverContextBinder`
D. The method moved to `Sdf.Path`

---

**PD-016** · Obj 7.7 · Difficulty: Medium · Type: Single choice

From a temp cwd, `r.Resolve("./tex/wood.png")` is `False` even though `assets/tex/wood.png` exists. Why?

A. PNG is not a USD asset
B. Raw `Resolve` of `./` uses **cwd**, not the layer; composition anchors to the **layer**
C. Search paths always apply to `./` paths
D. You must call `AnchorRelativePath`

---

**PD-017** · Obj 7.7 · Difficulty: Medium · Type: Single choice

`r.CreateIdentifier("./tex/wood.png")` with **no** anchor returns what, and is that path search-path eligible?

A. `./tex/wood.png` still; `./` paths **are** search-path lookups
B. `tex/wood.png`; **unanchored** identifiers become search-path (context-dependent); `./` paths are **not**
C. An absolute `/mnt/...` path
D. `None`

---

**PD-018** · Obj 7.7 · Difficulty: Medium · Type: Multiple select
Select two.

With a `DefaultResolverContext` bound to `searchA/` (which contains `tex/wood.png`):

A. `Resolve("tex/wood.png")` succeeds
B. `Resolve("./tex/wood.png")` still fails — `./` is not a search-path lookup
C. Both succeed equally
D. Unbinding keeps the search path for the rest of the process

---

**PD-019** · Obj 7.5 · Difficulty: Medium · Type: Single choice

`shot.usda` references `@chair.usda@` (no `./`). `Usd.Stage.Open("shot.usda")` without a context reports `ErrorInvalidAssetPath`. Opening with `pathResolverContext=` pointing at `assets/` succeeds. Lesson?

A. `Open` cannot take a resolver context
B. Context-dependent identifiers need `Stage.Open(..., pathResolverContext=)`; do not rely on cwd
C. Missing `defaultPrim` always produces `InvalidAssetPath`
D. You must convert the reference to a sublayer

---

**PD-020** · Obj 7.5 · Difficulty: Medium · Type: Multiple select
Select two.

A studio custom resolver is missing in the DCC. Which integration steps match Obj 7.5?

A. Ship `ArResolver` plugin + `plugInfo.json` on `PXR_PLUGINPATH_NAME` (before USD initializes)
B. Rebuild the plugin against the **same** USD the DCC loads
C. `pip install` any resolver wheel compiled against USD 24 into a USD 26 DCC
D. Call `AnchorRelativePath` to register the plugin

---

**PD-021** · Obj 7.6 · Difficulty: Easy · Type: Single choice

Where should a pipeline store a **typed, queryable** department tag `dept = "layout"` on a prim?

A. In the prim **name** (`layout_Chair`)
B. `customData` (dictionary metadata) via `SetCustomDataByKey` / USDA `customData = { ... }`
C. In `faceVertexIndices`
D. Only as a filename prefix

---

**PD-022** · Obj 7.6 · Difficulty: Medium · Type: Single choice

`prim.GetCustomData()` after setting only `dept` may contain extra keys such as `userDocBrief`. How should a validator read the studio key?

A. Assume `GetCustomData()` is exactly `{dept: ...}`
B. `GetCustomDataByKey("dept")` (or equivalent key lookup)
C. `GetAssetInfo()` — customData aliases assetInfo
D. Parse USDA with regex only

---

**PD-023** · Obj 7.6 · Difficulty: Medium · Type: Single choice

`assetInfo` vs `customData` in a publish pipeline?

A. They are the same field
B. `assetInfo` holds catalog fields (`identifier`, `version`, `name`); `customData` is the open bag for studio keys; neither replaces typed attributes/schemas
C. `customData` is stripped on every Save
D. `assetInfo` is only legal on materials

---

**PD-024** · Obj 7.6 · Difficulty: Medium · Type: Multiple select
Select two.

Flattening a shot for a vendor **keeps** `customData` owner names and often **absolutizes** `@/mnt/show/tex.png@`. What must the pipeline still do (Obj 7.6 / 1.9)?

A. Clear confidential `customData` / `assetInfo` keys
B. `UsdUtils.ModifyAssetPaths` (or localize) so paths are package-relative
C. Rely on Flatten to strip metadata automatically
D. Leave `/mnt` paths so the vendor’s DefaultResolver “finds them”

---

**PD-025** · Obj 7.7 · Difficulty: Easy · Type: Single choice

A publish gate should fail when `ComputeAllDependencies` returns a non-empty **unresolved** list. Why?

A. Unresolved is only a warning for usdview
B. The package is missing a layer or asset the stage needs; ship is incomplete
C. Unresolved always includes the session layer
D. Unresolved means the file is USDA

---

**PD-026** · Obj 7.7 · Difficulty: Medium · Type: Single choice

Authored path is `@./gone.jpg@`. Compute’s unresolved entry is often an **absolute** tmp path. How should the gate compare?

A. String-equal against `./gone.jpg` only
B. Normalize / `os.path.basename` (or resolve both) before matching
C. Ignore unresolved if stderr also warned
D. Unresolved is never absolutized

---

**PD-027** · Obj 7.4 · Difficulty: Medium · Type: Single choice

A DCC round-trip CI should treat which event as a **failure** if the pipeline requires live payloads?

A. USDA rewritten as USDC (lossless encoding hop)
B. Flatten on export that **bakes away** the payload layer
C. `upAxis` still `Y`
D. `ComputeAllDependencies` still lists the payload

---

**PD-028** · Obj 7.4 · Difficulty: Medium · Type: Multiple select
Select two.

A DCC **importer** in a pipeline (Obj 7.4 / 7.8) should:

A. Honor `LoadNone` vs `LoadAll` / masks according to studio policy
B. Preserve namespaced custom attributes and `customData` keys the mapping lists
C. `Xform.Define` on every referenced root before adding the reference
D. Call `GetMaster()` to discover assets

---

**PD-029** · Obj 7.8 · Difficulty: Medium · Type: Single choice

Extending a DCC importer: chairs are payloads. The plugin uses `Open(..., LoadNone)` for speed and never Loads. Result?

A. Illegal API
B. Empty payload contents until `Load`; references would still be populated
C. Payloads and references both stay empty
D. Hydra loads them anyway

---

**PD-030** · Obj 7.8 · Difficulty: Medium · Type: Single choice

The DCC’s USD is 26.08; a studio file-format plugin was built against 24.11 and dropped on `PXR_PLUGINPATH_NAME`. Typical outcome?

A. Perfect load; ABI is stable across years
B. Plugin fail / missing types — **match plugin builds to the DCC’s USD** (Obj 3.1 / 7.8)
C. USD silently recompiles the plugin
D. Only USDA files fail

---

**PD-031** · Obj 7.1 · Difficulty: Medium · Type: Single choice

A pipeline converts published USD components to glTF for a web viewer. Fidelity policy should require which documented steps?

A. Copy USDA into `.gltf` extras and skip meshes
B. Triangulate, meters/+Y, UV V-flip, bake or report dropped variants/layers, then **validate** the glTF
C. Trust `metersPerUnit` inside glTF (glTF reads USD metadata)
D. Keep quads; core glTF 2.0 stores n-gons

---

**PD-032** · Obj 7.1 · Difficulty: Easy · Type: Single choice

Which hop is **lossless** and therefore not a fidelity incident?

A. USD Mesh → OBJ
B. USDA ↔ USDC
C. USD variants → core glTF
D. CAD NURBS → USD Mesh

---

**PD-033** · Obj 7.1 · Difficulty: Medium · Type: Multiple select
Select two.

A mapping document for the USD→glTF farm job should list:

A. Known loss (composition arcs, unbaked variants)
B. Required transforms (triangulate, V-flip, unit scale)
C. That glTF `formatId` is `usd`
D. That Flatten is illegal in every pipeline

---

**PD-034** · Obj 7.4 · Difficulty: Medium · Type: Single choice

Exporter **hooks** shared by four DCCs should run when?

A. After the farm already rendered
B. Immediately before Save/publish: `defaultPrim`, units, upAxis, kind, identifier
C. Only inside usdview
D. Only when exporting USDA

---

**PD-035** · Obj 7.2 · Difficulty: Medium · Type: Single choice

`GetLayerStack()` of an opened shot lists what **first**?

A. Weakest sublayer
B. The anonymous **session** layer (strongest local sheet)
C. `layout.usda`
D. Referenced chair assets

---

**PD-036** · Obj 7.5 · Difficulty: Easy · Type: Single choice

Artists should author which style of asset path when a studio resolver is in play?

A. Absolute `/mnt/show/seq/shot/tex.png` in every layer
B. Resolver **identifiers** (search-path or URI), never machine mounts
C. Windows drive letters only
D. `file://` with user home directories

---

**PD-037** · Obj 7.7 · Difficulty: Medium · Type: Single choice

`IsContextDependentPath("tex/wood.png")` vs `("./tex/wood.png")`?

A. Both True
B. `True` for `tex/wood.png`, `False` for `./tex/wood.png`
C. Both False
D. `./` is always context-dependent

---

**PD-038** · Obj 7.6 · Difficulty: Medium · Type: USDA-reading

```usda
#usda 1.0
def Xform "Chair" (
    assetInfo = {
        string identifier = "chair"
        string version = "3"
    }
    customData = {
        string dept = "model"
    }
)
{
}
```

Which Python reads the catalog key vs the studio tag?

A. Both from `GetAttribute("identifier")`
B. `GetAssetInfoByKey("identifier")` and `GetCustomDataByKey("dept")`
C. `GetAssetInfoByKey("dept")` for both
D. Layer metadata only — prims cannot hold these dictionaries

---

**PD-039** · Obj 7.2 · Difficulty: Hard · Type: Single choice

`ExtractExternalReferences("shot.usda")` does not list `chair.usda`, but the composed shot shows a chair. Why?

A. References on sublayers are illegal
B. Extract does not recurse; the reference is authored on `layout.usda`
C. USDC chairs are invisible to extract
D. The chair exists only as a PointInstancer prototype

---

**PD-040** · Obj 7.3 · Difficulty: Medium · Type: Single choice

usd-core has no `usdcat`. A pipeline convert job should:

A. Fail — Obj 7.3 requires the CLI
B. `Sdf.Layer.Export` to the destination extension (`.usda` / `.usdc`)
C. Rename bytes without transcoding
D. Always Flatten first

---

**PD-041** · Obj 7.2 · Difficulty: Easy · Type: Single choice

Pipelines should author which field so `UsdUtils.GetModelNameFromRootLayer` is a **stable** asset name?

A. The filename stem only (`chair.usda` → always `"chair"`)
B. `defaultPrim` (the API reads that; without it it may fall back to an arbitrary root prim name)
C. `assetInfo['name']` only — `defaultPrim` is ignored
D. A session-layer comment

---

**PD-042** · Obj 7.2 · Difficulty: Medium · Type: Multiple select
Select two.

Which pair is the right split for history vs pins?

A. Git (or similar) versions **work** files
B. Publish **folders** (`v017/`) are what shots pin
C. Daily `monday.usda` sublayers on the shot are the supported history mechanism
D. Layer stacks replace git

---

**PD-043** · Obj 7.5 · Difficulty: Medium · Type: Single choice

Setting `PXR_PLUGINPATH_NAME` **after** the DCC has already imported `pxr` / opened a stage. Expected result?

A. Custom `StudioResolver` appears immediately
B. Too late in many hosts — resolver plugins must be visible **before** USD initializes
C. USD restarts automatically
D. Only Hydra plugins need early path setup

---

**PD-044** · Obj 7.7 · Difficulty: Medium · Type: Single choice

A validator flags asset paths that contain spaces, backslashes, or unanchored `C:\` drives in published layers. That check is primarily Obj:

A. 8.2 (PreviewSurface)
B. 7.7 (asset paths formatted correctly) plus resolver policy (7.5)
C. 1.6 (LIVERPS)
D. 3.3 (custom kinds)

---

**PD-045** · Obj 7.4 · Difficulty: Medium · Type: Single choice

Round-trip of `UsdPhysics.CollisionAPI` through a DCC that only maps Mesh + PreviewSurface. Pipeline choice?

A. Physics always survives because it is core USD imaging
B. Keep USD as source of truth / sidecar, or extend the importer; document the loss in the mapping
C. Flatten restores physics APIs
D. Set `kind = component` to encode colliders

---

**PD-046** · Obj 7.8 · Difficulty: Medium · Type: Multiple select
Select two.

When extending a DCC importer you should **not**:

A. Flatten the stage on import “to simplify the node graph” if the studio needs live references
B. Typeless `DefinePrim` then `AddReference` so asset types survive
C. Drop `factory:partId` because it is not UsdGeom
D. Honor layer offsets on referenced animation

---

**PD-047** · Obj 7.2 · Difficulty: Medium · Type: Single choice

A kitchen assembly should use which **kinds** in the documented model hierarchy?

A. Assembly at the kitchen, **component** on each published chair; groups as needed
B. Component on every vertex
C. No kinds — they slow the farm
D. `model` on cameras only

---

**PD-048** · Obj 7.3 · Difficulty: Easy · Type: Single choice

Why might a pipeline **forbid USDC in Git** for department WIP?

A. USDC cannot store references
B. Crate is binary — merges and reviews are painful compared with USDA
C. Git cannot store files larger than 1 KB
D. USDC is deprecated in 26.08

---

**PD-049** · Obj 7.5 · Difficulty: Medium · Type: Single choice

`Ar.ResolverContextBinder` is used in lab 29 to:

A. Register a new C++ resolver class
B. Temporarily bind a `DefaultResolverContext` (search paths) for `Resolve` calls
C. Mute layers
D. Flatten the stage

---

**PD-050** · Obj 7.7 · Difficulty: Hard · Type: Python-reading

Lab 29 prints `with ctx errors/type: 0 Xform` and `no ctx errors: 1 ErrorInvalidAssetPath`. The referenced identifier was `@chair.usda@`. What did the context provide?

A. A population mask
B. A search path so the identifier resolved under `assets/`
C. `LoadAll`
D. A session layer

---

**PD-051** · Obj 7.6 · Difficulty: Easy · Type: Single choice

Pipeline documentation (`assetInfo.identifier`) vs secrets (`customData.owner = "jdoe"`) in a **vendor** delivery:

A. Ship both; Flatten removes owner
B. Keep identifier if it is public catalog; **strip** owner and other PII/secrets
C. Strip identifier always; keep owner
D. `customData` cannot be stripped from Python

---

**PD-052** · Obj 7.2 · Difficulty: Medium · Type: Single choice

`UsdUtils.LocalizeAsset` / USDZ packaging uses the same inventory as Compute. After localize, unresolved `gone.jpg` should:

A. Be ignored
B. Fail the job or be listed as a known omission — do not ship a silent hole
C. Turn into a Sphere
D. Always be downloaded from NVIDIA

---

**PD-053** · Obj 7.1 · Difficulty: Medium · Type: Single choice

Farm converts USD → glTF **after** Flatten. Variants are gone. Is that a fidelity bug?

A. Always — Flatten is forbidden before glTF
B. Only if the mapping promised live variants; if the job is “delivery bake,” document Flatten as the transform and still validate meshes/UVs/units
C. Never — glTF stores variant sets in core
D. Only if USDA was used

---

**PD-054** · Obj 7.4 · Difficulty: Medium · Type: Multiple select
Select two.

CI after DCC export should compare:

A. `ComputeAllDependencies` 3-tuple (basenames)
B. Selected attribute `Get()` values including custom namespaces
C. `GetMaster()` equality
D. That `ComplianceChecker` still exists

---

**PD-055** · Obj 7.8 · Difficulty: Easy · Type: Single choice

usd-core lacks `usdview` and Hydra. A pipeline importer running in a headless convert farm should:

A. Require usdview to import
B. Use `Usd`/`Sdf` APIs only; do not assume imaging plugins
C. Call `UsdMtlx` on this wheel
D. Shell out to `usdcat` on usd-core

---

**PD-056** · Obj 7.2 · Difficulty: Medium · Type: Single choice

Best pin for a **locked** lighting shot that must not drift when modelers keep working?

A. `assets/chair/work/chair.usda`
B. `assets/chair/v017/chair.usda` (immutable publish)
C. Sublayer every historical `v001`…`v017` on the shot
D. Rename the prim `/Chair_v017` in the work file

---

## Answers

**PD-001 — Answer: B.** Work vs immutable publish vs pin is the pipeline loop. Encoding is independent. Review: §32.1–32.3.

**PD-002 — Answer: B.** Pin published versions, not work trees. Version in the prim name is the other common mistake. Review: §32.3.

**PD-003 — Answer: B.** Stable `defaultPrim` / identifier; version in folders. Review: §32.3, §23.2.

**PD-004 — Answer: B.** Identifier is the catalog key. Review: §32.3.

**PD-005 — Answer: A, C.** Obj 7.2 is written guidelines plus diagrams. Review: §32.5, §23.5.

**PD-006 — Answer: B.** Interface + payload/contents layers; kinds on models. Review: §23.2–23.5.

**PD-007 — Answer: B.** Verified 3-tuple, recursive. Not a dict. Review: §32.4, lab 28.

**PD-008 — Answer: B.** Extract is one file. Review: §32.4.

**PD-009 — Answer: A, B.** Missing files warn and list; they do not abort. Extract’s second list includes textures. Review: §32.4.

**PD-010 — Answer: B.** First listed / top of the strength diagram is stronger. Review: §15.1, §32.6.

**PD-011 — Answer: B.** One owner per department layer. Review: §32.6, §15.5.

**PD-012 — Answer: B.** Same trade-off as DE, applied as pipeline policy. Review: §31.1, §7.3.

**PD-013 — Answer: B.** Verified magic vs `formatId usd`. Review: §31.3.

**PD-014 — Answer: B.** Verified lab 29. Review: §33.2.

**PD-015 — Answer: B.** `AnchorRelativePath` is gone on 26.08. Review: §33.2.

**PD-016 — Answer: B.** Naive `./` is cwd; layers anchor. Review: §33.2, lab 29.

**PD-017 — Answer: B.** Verified: no-anchor ident `tex/wood.png`; `./` is not search-path. Review: §33.3, lab 29.

**PD-018 — Answer: A, B.** Verified bound tex True, bound `./` False; unbind restores False. Review: lab 29.

**PD-019 — Answer: B.** Verified: with context 0 errors / Xform; without `ErrorInvalidAssetPath`. Review: §33.3, lab 29.

**PD-020 — Answer: A, B.** Plugin path + ABI match. Do not mix USD 24 plugins into 26. Review: §33.5, §35.2.

**PD-021 — Answer: B.** `customData` is the metadata bag (Obj 7.6). Review: §12.2, lab 08.

**PD-022 — Answer: B.** Schema may inject `userDocBrief`. Review: lab 08, §12.2.

**PD-023 — Answer: B.** Catalog vs studio bag vs typed properties. Review: §12.2.

**PD-024 — Answer: A, B.** Flatten does not sanitize. Review: §34.3.

**PD-025 — Answer: B.** Non-empty unresolved fails publish. Review: §32.4.

**PD-026 — Answer: B.** Unresolved is often absolutized. Review: §32.4.

**PD-027 — Answer: B.** Flatten bakes payloads; encoding USDA↔USDC is lossless. Review: §34.2, §27.5.

**PD-028 — Answer: A, B.** Load policy + preserve mapped metadata. `Xform.Define` before reference can clobber type; `GetMaster` is gone. Review: §35.3, §29.5.

**PD-029 — Answer: B.** Same LoadNone fact, importer framing. Review: §17.2, §35.3.

**PD-030 — Answer: B.** Match plugin ABI to host USD. Review: §35.2.

**PD-031 — Answer: B.** Fidelity = transform + validate + report loss. Review: §27.4.

**PD-032 — Answer: B.** USDA↔USDC lossless. Review: §31.1, §27.1.

**PD-033 — Answer: A, B.** Mapping document contents. Flatten can be a delivery step; it is not universally illegal. Review: §27.3–27.4.

**PD-034 — Answer: B.** Shared hooks before Save. Review: §34.1, §29.6.

**PD-035 — Answer: B.** Session is strongest local. Review: §15.3, §32.6.

**PD-036 — Answer: B.** Identifiers, not mounts. Review: §33.5.

**PD-037 — Answer: B.** Verified lab 29. Review: §33.3.

**PD-038 — Answer: B.** `assetInfo` vs `customData` APIs. USDA metadata is on the spec in parentheses. Review: §12.2.

**PD-039 — Answer: B.** Extract does not walk layout. Review: §32.4.

**PD-040 — Answer: B.** Python Export stand-in for usdcat. Flatten is composition. Review: §31.4, §35.1.

**PD-041 — Answer: B.** The API reads `defaultPrim`. Verified: with `defaultPrim = "B"` it returns `B`; with no default it returned the first root prim (`A`); an empty layer returns `''`. Author `defaultPrim` for a stable name. Review: §32.3.

**PD-042 — Answer: A, B.** Git for work history; publish folders for pins. Daily sublayers are not version control. Review: §32.3, §32.6.

**PD-043 — Answer: B.** Plugin path must be set before USD init in many hosts. Review: §33.5, §35.2, §36.2.

**PD-044 — Answer: B.** Path format + resolver policy. Review: §33.4.

**PD-045 — Answer: B.** Domain APIs need mapping or a USD sidecar. Review: §35.4, §27.5.

**PD-046 — Answer: A, C.** Flatten-on-import and dropping custom attrs are the anti-patterns; B and D are correct importer behavior (not selected). Review: §29.5, §35.3.

**PD-047 — Answer: A.** Assembly/group/component model hierarchy. Review: §23.3, lab 22.

**PD-048 — Answer: B.** Crate is not deprecated; it is the wrong Git WIP default. Review: §31.1.

**PD-049 — Answer: B.** Lab 29 binds search-path context. Review: §33.3.

**PD-050 — Answer: B.** Search path `assets/` resolves `@chair.usda@`. Review: lab 29.

**PD-051 — Answer: B.** Identifier can stay; strip secrets. Flatten keeps customData. Review: §34.3.

**PD-052 — Answer: B.** Unresolved is a failed or explicit omission, never silent. Review: §32.4, §31.2.

**PD-053 — Answer: B.** Bake vs live is a documented transform. Core glTF has no variant sets. Review: §27.4, §34.2.

**PD-054 — Answer: A, B.** `GetMaster` gone; `ComplianceChecker` gone. Review: §32.4, §35.3, lab 27–28.

**PD-055 — Answer: B.** Headless `Usd`/`Sdf`; no usdcat/UsdMtlx on usd-core. Review: §35.1, F5.

**PD-056 — Answer: B.** Pin the published version folder. Review: §32.3.

---

*Pipeline Development domain complete: PD-001–PD-056 (target 56).*

