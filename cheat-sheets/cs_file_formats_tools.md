# Cheat sheet — File formats & CLI tools

**USD 26.08** · Obj 4.3, 7.3 · Ch 7, 31 · This venv has **no** CLI binaries.

## Four encodings

| Kind | Extension | Magic | `formatId` | Use |
|------|-----------|-------|------------|-----|
| USDA | `.usda` | `#usda 1.0` | `usda` | Git, interfaces, diffs |
| USDC / crate | `.usdc` | `PXR-USDC` | `usdc` | Farm, heavy geo, publish |
| USD | `.usd` | crate **or** text | **`usd`** (follows **extension**) | Default `CreateNew` → crate |
| USDZ | `.usdz` | `PK` (zip) | `usdz` | Package: USD + images + audio |

`.usd` is a **box**: id is `usd`; **bytes** decide crate vs text.  
USDA copied to `text.usd` still **opens**; formatId stays `usd`.

| Job | Encoding |
|-----|----------|
| Department merge in Git | USDA |
| Farm opens 10k times | USDC |
| External vendor drop | Localized / flattened + optional USDZ |
| `usdcat --flatten` when you meant crate | **Wrong** — that **bakes composition** |

## USDZ rules

- Uncompressed zip: `compress_type` **0** (`ZIP_STORED`). DEFLATE is **not** spec-legal.  
- `UsdUtils.CreateNewUsdzPackage("root.usda", "out.usdz")`.  
- No nested `.usdz`, no arbitrary GUI zip, no Alembic as a USDZ member.  
- Inside: asset paths stay `./tex.png` (resolved in-package).

## CLI (full OpenUSD builds) vs this book

```{.bash .norun}
usdcat in.usda -o out.usdc
usdcat in.usdc                 # USDA to stdout
usdcat --flatten shot.usda -o flat.usda
usdzip --asset root.usda out.usdz
usdchecker asset.usda
```

| CLI | usd-core stand-in |
|-----|-------------------|
| `usdcat -o` | `Sdf.Layer.FindOrOpen(...).Export("out.usdc")` |
| `usdcat` print | `print(layer.ExportToString())` |
| `usdcat --flatten` | `stage.Flatten()` (bakes **refs**) |
| Keep refs, drop sublayers | `UsdUtils.FlattenLayerStack(stage)` |
| `usdzip` | `CreateNewUsdzPackage` (STORE) |
| `usdchecker` | `UsdValidation` (`ValidationRegistry`, `Validator`) |
| `usdview` | Not in wheel; LayerStack / purpose are still exam concepts |

`UsdUtils.ComplianceChecker` is **gone**.  
Two metadata checkers: `usdValidation:StageMetadataChecker` (`defaultPrim`) and `usdGeomValidators:StageMetadataChecker` (units / upAxis).

## Detect encoding

Read first bytes: `#usda` → text; `PXR-USDC` → crate; `PK` → zip.  
Then `layer.GetFileFormat().formatId` for the **plugin** (often `usd` on `.usd`).

## Flatten vs convert

| Call | Refs | Sublayers |
|------|------|-----------|
| `Export` to `.usdc` | kept | kept |
| `Flatten()` | **baked** | baked |
| `FlattenLayerStack()` | **kept** | collapsed |

External delivery: localize or Flatten so `hero://` work URIs do not leak (Obj 1.9).
