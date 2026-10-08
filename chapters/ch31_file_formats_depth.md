# Chapter 31 — File Formats in Depth

> **Exam domain:** Data Exchange (15%) · **Objectives:** 4.3, 7.3 · **Study day:** 9 · **Est. time:** 75 min
> **Prerequisites:** Ch 7 (USDA / USDC / `.usd` / USDZ first look)

Chapter 7 named the four encodings. This chapter is the **decision** chapter the exam wants: when USDA vs USDC (Obj 4.3 / 7.3), the USDZ packaging rules, how to tell what a `.usd` file really is, and the `usdcat` / `usdzip` commands with `usd-core` stand-ins.

## Learning goals

- Choose USDA or USDC from performance, readability, diff/merge, and archival needs.
- Explain why a tiny interface file can be *larger* as crate than as text.
- Package a USDZ: uncompressed zip, first file is the root layer, allowed media.
- Detect USDA vs crate vs zip from magic bytes, even when the extension is `.usd`.
- Convert encodings with `Sdf.Layer.Export` and `UsdUtils.CreateNewUsdzPackage`.

## Key terms

| Term | One-line definition |
|------|---------------------|
| **USDA** | Text layer (`#usda 1.0`); format id `usda` |
| **USDC / crate** | Binary layer (`PXR-USDC`); format id `usdc` |
| **`.usd`** | Extension that may hold either encoding; `CreateNew` writes crate; format id `usd` |
| **USDZ** | Uncompressed zip **package** of USD layer(s) plus allowed media |
| **Magic bytes** | The first bytes of a file that identify the encoding |
| **`usdcat`** | CLI to convert/print layers (not in `usd-core`); Python: `Sdf.Layer.Export` |
| **`usdzip`** | CLI to build `.usdz` (not in `usd-core`); Python: `CreateNewUsdzPackage` |
| **ARKit USDZ** | Package aimed at Apple viewers; often stores the root as `.usdc` |

---

## 31.1 USDA vs. USDC trade-offs

### 1. What is it?

**USDA** is the text encoding of one layer. **USDC** (crate) is the binary encoding of one layer. Same scene data; different on-disk form. Obj 4.3 and 7.3 ask you to pick one and say why.

### 2. Why do we need it?

A million-point mesh in USDA is slow to parse and painful in git. A two-line payload interface in USDC is *bigger* than the text and cannot be reviewed in a pull request. The wrong choice is a pipeline tax you pay every day.

### 3. Beginner explanation

USDA is **source code**. USDC is a **compiled object file**. You edit and merge source. You ship objects to the renderer. You keep both: a tiny USDA entry layer that payloads a USDC geometry layer (Chapter 23).

*Where the analogy breaks:* crate is not compiled from USDA by a separate compiler you run. `Export("file.usdc")` rewrites the same `Sdf.Layer`. Nothing is lost except comments/layout (crate does not store USDA comments).

### 4. Technical explanation

Verified on USD 26.08:

| Need | Prefer | Why |
|------|--------|-----|
| Read, diff, merge, code review | USDA | Line-oriented text; git works |
| Heavy geometry, time samples, publish | USDC | Faster load; smaller for large layers |
| Tiny interface (`defaultPrim` + payload) | USDA | Crate has a **fixed header**; a 30-byte USDA was **582 bytes** as USDC |
| Archival of a published mesh | USDC | Compact; not meant to be hand-edited |
| Archival of a human-authored layout | USDA | You can still read it in 20 years in a text editor |
| Mixed asset | USDA entry + USDC payload | Interface stays reviewable; geo stays fast |

Numbers from the example below (same prims, two encodings):

- Empty Xform: `tiny.usda` **30** bytes, `tiny.usdc` **582** bytes (crate overhead wins).
- 200 spheres: `many.usda` **12119** bytes, `many.usdc` **3171** bytes (crate ~4× smaller).

Other rules:

- `ExportToString()` always emits USDA text, even from a crate layer.
- `CreateNew("x.usdc")` / `Export("x.usdc")` → format id `usdc`, magic `PXR-USDC`.
- Comments and original USDA whitespace do not survive a round trip through crate.
- Neither encoding is encryption. Crate is not a zip (USDZ is).

### 5. Mental model

```text
  tiny layer:   USDA 30 B   <   USDC 582 B     (header overhead)
  fat layer:    USDA 12 KB  >   USDC  3 KB     (binary packing)

  typical asset:
    chair.usda     (interface, variants, payload)     keep text
        payload --> chair_geo.usdc                    keep crate
```

### 6. Simple example

A published chair: `chair.usda` is 40 lines of metadata. `chair_geo.usdc` holds the mesh. Reviewers diff the USDA. usdview loads the crate quickly.

### 7. USDA example

The *text* encoding of the tiny layer used in step 8:

```usda
#usda 1.0

def Xform "W"
{
}
```

That is the entire 30-byte file (plus newline). The crate of the same spec is hundreds of bytes of header.

### 8. Python example

```python
from pxr import Usd, UsdGeom
import os

tiny = Usd.Stage.CreateNew("tiny.usda")
UsdGeom.Xform.Define(tiny, "/W")
tiny.GetRootLayer().Save()
tiny.GetRootLayer().Export("tiny.usdc")

many = Usd.Stage.CreateNew("many.usda")
UsdGeom.Xform.Define(many, "/R")
for i in range(200):
    UsdGeom.Sphere.Define(many, f"/R/S{i}").GetRadiusAttr().Set(1.0)
many.GetRootLayer().Save()
many.GetRootLayer().Export("many.usdc")

print("tiny.usda", os.path.getsize("tiny.usda"),
      "tiny.usdc", os.path.getsize("tiny.usdc"))
print("many.usda", os.path.getsize("many.usda"),
      "many.usdc", os.path.getsize("many.usdc"))
```

**Expected output**

```text
tiny.usda 30 tiny.usdc 582
many.usda 12119 many.usdc 3171
```

For a 30-byte interface, crate is the wrong default. For 200 gprims, crate is the right publish encoding.

### 9. Real-world use case

A VFX show: layout and lighting department layers stay USDA so leads can review in GitLab. Animation caches and hero meshes publish as USDC. The shot root is USDA that sublayers both.

### 10. Common mistakes

> [!MISTAKE] Publishing every layer as USDC "for speed," including 8-line payload interfaces. You lose diffs and *increase* size. Keep interfaces USDA.

> [!MISTAKE] Editing USDC in a text editor. You will corrupt the crate. Convert to USDA, edit, convert back if you must.

### 11. Exam traps

> [!TRAP] "USDC is always smaller." False for tiny layers. The table in step 4 is the answer.

> [!TRAP] "USDA cannot hold time samples." It can; it is just verbose.

### 12. Practice questions

**DE-031a** · Obj 4.3 · Difficulty: Medium · Type: Single choice
A 30-byte USDA Xform exported to `.usdc` became 582 bytes. Why prefer USDA for that file?

A. Crate cannot store Xforms
B. Crate header overhead dominates; the file is for humans to diff
C. USDA is always faster to load
D. USDC is a zip

**DE-031b** · Obj 7.3 · Difficulty: Easy · Type: Select two.
Choose USDC when:

A. The layer is a large mesh cache
B. You need git merge of a lighting edit
C. Load time of heavy geometry matters
D. You want to leave comments in the file

**Answers**

**DE-031a — B.** Verified 30 vs 582. Review: §31.1.

**DE-031b — A and C.** B and D are USDA. Review: §31.1.

### 13. Exam takeaways

> [!KEY]
> - USDA = readable/mergeable; USDC = fast/compact for *large* layers.
> - Tiny files: USDA can be smaller than crate.
> - Typical asset: USDA interface, USDC payload.
> - Comments do not survive crate.

---

## 31.2 USDZ packaging rules and `usdzip`

### 1. What is it?

**USDZ** is an **uncompressed, unencrypted zip** of one or more USD layers plus allowed media (images, audio). The **first file in the archive** is the default layer you get when you `Usd.Stage.Open("file.usdz")`.

### 2. Why do we need it?

Web, AR, and vendor delivery want **one file**. A folder of USDA + PNGs gets lost in email. USDZ is that package, with extra rules so USD can memory-map contents (no DEFLATE).

### 3. Beginner explanation

USDZ is a **folder in a box**. The box is zip, but the files inside are stored, not squeezed. The first item in the box is the front door (the root layer). Textures sit beside it.

*Where the analogy breaks:* you cannot zip an arbitrary folder with the OS GUI and call it USDZ. Compression, absolute paths, nested `.usdz`, and disallowed types (for example Alembic) violate the spec. Use `usdzip` / `CreateNewUsdzPackage`.

### 4. Technical explanation

Verified on USD 26.08:

- `UsdUtils.CreateNewUsdzPackage("root.usda", "out.usdz")` → `True` on success.
- `zipfile` lists `['root.usda', 'tex.png']` when the layer has an `asset` attribute pointing at `./tex.png`.
- `compress_type` is **0** (`ZIP_STORED`). Not DEFLATE.
- `CreateNewARKitUsdzPackage` builds a sibling package for Apple viewers; the **first** entry was `root.usdc` (crate), not `root.usda`.
- `ExtractUsdzPackage(usdz, dir, verbose=False, force=False)` unpacks. Pass `force=True` if the directory already exists; otherwise it can return `False`.
- Opening `out.usdz` gives `GetFileFormat().formatId == "usdz"`. Asset paths inside still look like `./tex.png` (resolved inside the package).

Spec rules the exam expects (OpenUSD USDZ spec; packaging tool enforces most of them):

- No zip compression; 64-byte alignment of file data (mmap).
- Relative paths only; no `..`.
- Allowed: `.usd` / `.usda` / `.usdc`, images (png, jpeg, exr, avif, …), some audio. Not a free-for-all.
- One default layer: the first USD file in the zip.

`usdzip` (full toolset, `.norun` here):

```text
usdzip --asset root.usda out.usdz
```

### 5. Mental model

```text
  out.usdz  (zip, STORE only)
    [0] root.usda     <-- Stage.Open uses this
    [1] tex.png
```

### 6. Simple example

A component with one PNG. `CreateNewUsdzPackage` puts the USDA first and the PNG second, both uncompressed. `ExtractUsdzPackage` restores both files.

### 7. USDA example

*File: root.usda* (the layer that gets packed)

```usda
#usda 1.0
(
    defaultPrim = "Asset"
)

def Xform "Asset"
{
    asset tex = @./tex.png@
}
```

### 8. Python example

```python
from pxr import Sdf, Usd, UsdGeom, UsdUtils
import os, zipfile

stage = Usd.Stage.CreateNew("root.usda")
UsdGeom.Xform.Define(stage, "/Asset")
stage.SetDefaultPrim(stage.GetPrimAtPath("/Asset"))
open("tex.png", "wb").write(
    bytes([137, 80, 78, 71, 13, 10, 26, 10]) + b"\x00" * 8)
stage.GetPrimAtPath("/Asset").CreateAttribute(
    "tex", Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath("./tex.png"))
stage.GetRootLayer().Save()

print("usdzip-equivalent:",
      UsdUtils.CreateNewUsdzPackage("root.usda", "out.usdz"))
print("contents:", zipfile.ZipFile("out.usdz").namelist())
print("compress:",
      [i.compress_type for i in zipfile.ZipFile("out.usdz").infolist()])
print("arkit:",
      UsdUtils.CreateNewARKitUsdzPackage("root.usda", "arkit.usdz"))
print("arkit first:", zipfile.ZipFile("arkit.usdz").namelist()[0])
os.makedirs("unpacked", exist_ok=True)
print("extract:",
      UsdUtils.ExtractUsdzPackage("out.usdz", "unpacked", False, True))
print("unpacked:", sorted(os.listdir("unpacked")))
```

**Expected output**

```text
usdzip-equivalent: True
contents: ['root.usda', 'tex.png']
compress: [0, 0]
arkit: True
arkit first: root.usdc
extract: True
unpacked: ['root.usda', 'tex.png']
```

`compress: [0, 0]` is the exam fact: stored, not deflated. ARKit's first file is crate.

### 9. Real-world use case

A manufacturer emails `pump.usdz` to a client. The client opens it on an iPad (ARKit package) and in usdview (generic package). Same textures; ARKit edition uses a crate root.

### 10. Common mistakes

> [!MISTAKE] `zip -r scene.usdz folder/` with default compression. USD may fail to mmap. Use `CreateNewUsdzPackage`.

> [!MISTAKE] Forgetting `defaultPrim` on the packed root. Referencing the USDZ then fails the same way a bare USDA would (Chapter 16).

> [!MISTAKE] `ExtractUsdzPackage` returning `False` because the output dir exists and `force` is False.

### 11. Exam traps

> [!TRAP] "USDZ is compressed USDC." USDC is one layer. USDZ is a zip of files, uncompressed.

> [!TRAP] "The `.usda` inside a USDZ is always the default layer." The **first archive member** that is a USD layer is. ARKit packages may put `.usdc` first.

### 12. Practice questions

**DE-031c** · Obj 4.3 · Difficulty: Medium · Type: Select two.
Legal USDZ properties:

A. Zip compression type 0 (stored)
B. First USD file is the default layer
C. Nested `.usdz` of Alembic is required
D. DEFLATE is required for textures

**DE-031d** · Obj 4.3 · Difficulty: Easy · Type: Single choice
`CreateNewARKitUsdzPackage` in the example put first:

A. `root.usda`
B. `root.usdc`
C. `tex.png`
D. `PXR-USDC` as a loose file outside the zip

**Answers**

**DE-031c — A and B.** Review: §31.2.

**DE-031d — B.** Review: §31.2.

### 13. Exam takeaways

> [!KEY]
> - USDZ = uncompressed zip package, not a crate.
> - First USD member is the root layer.
> - Python: `CreateNewUsdzPackage` / `ExtractUsdzPackage` (`force=True` if needed).
> - ARKit helper often crates the root.

---

## 31.3 Format detection for `.usd`

### 1. What is it?

The **`.usd` extension does not tell you the encoding.** The file may be crate or text. You detect by **magic bytes** (and then `GetFileFormat().formatId`).

### 2. Why do we need it?

The exam and the USD FAQ ask "what file format is my `.usd` file?" Pipelines that assume `.usd` means crate will `file` a hand-written text `.usd` and panic. Detection is a two-byte (well, nine-byte) look.

### 3. Beginner explanation

`.usd` is a **box labeled "USD"** that might hold a letter (USDA) or a brick (USDC). Open the box: if you see `#usda 1.0`, it is a letter; if you see `PXR-USDC`, it is a brick; if you see `PK`, it is actually a zip (usually `.usdz`).

*Where the analogy breaks:* `GetFileFormat().formatId` for a `.usd` file is often **`usd`**, not `usda` or `usdc`, even when the bytes are crate or text. The **id follows the extension**; the **magic follows the bytes**. Report both.

### 4. Technical explanation

Verified on USD 26.08:

| File | Magic (first bytes) | `formatId` |
|------|---------------------|------------|
| `tiny.usda` | `#usda 1.0` | `usda` |
| `tiny.usdc` | `PXR-USDC\x00` | `usdc` |
| `CreateNew("scene.usd")` | `PXR-USDC\x00` | `usd` |
| USDA bytes saved as `text.usd` | `#usda 1.0` | `usd` |
| `.usdz` | `PK` (zip local header) | `usdz` |

- `Usd.Stage.CreateNew("scene.usd")` writes **crate** contents. That is the default.
- Copying USDA text into a `.usd` name still **opens**; prims are there; `formatId` stays `usd`.
- Detection function: read 12 bytes; test `startswith(b"#usda")`, `b"PXR-USDC"`, `b"PK"`.

> [!VERSION] Verified on USD 26.08. Default `.usd` = crate has been the rule for current OpenUSD; always detect, never trust the extension alone.

### 5. Mental model

```text
  extension  = nickname
  magic      = actual encoding
  formatId   = plugin that claimed the extension
```

### 6. Simple example

`scene.usd` from `CreateNew` is crate (`PXR-USDC`, id `usd`). `text.usd` copied from a `.usda` is text (`#usda 1.0`, id still `usd`).

### 7. USDA example

A `.usd` file *can* contain exactly this text — the extension does not forbid it:

```usda
#usda 1.0

def Xform "W"
{
}
```

If you only `ls *.usd`, you cannot know. Read the first line.

### 8. Python example

```python
from pxr import Sdf, Usd, UsdGeom


def detect(path):
    with open(path, "rb") as f:
        b = f.read(12)
    if b.startswith(b"#usda"):
        kind = "usda-text"
    elif b.startswith(b"PXR-USDC"):
        kind = "usdc-crate"
    elif b.startswith(b"PK"):
        kind = "zip-usdz"
    else:
        kind = "unknown"
    return kind, b[:9]


tiny = Usd.Stage.CreateNew("tiny.usda")
UsdGeom.Xform.Define(tiny, "/W")
tiny.GetRootLayer().Save()
tiny.GetRootLayer().Export("tiny.usdc")
st = Usd.Stage.CreateNew("scene.usd")
UsdGeom.Xform.Define(st, "/W")
st.GetRootLayer().Save()
open("text.usd", "wb").write(open("tiny.usda", "rb").read())

for p in ("tiny.usda", "tiny.usdc", "scene.usd", "text.usd"):
    kind, magic = detect(p)
    layer = Sdf.Layer.FindOrOpen(p)
    print(p, kind, "formatId=", layer.GetFileFormat().formatId,
          "magic=", magic)
```

**Expected output**

```text
tiny.usda usda-text formatId= usda magic= b'#usda 1.0'
tiny.usdc usdc-crate formatId= usdc magic= b'PXR-USDC\x00'
scene.usd usdc-crate formatId= usd magic= b'PXR-USDC\x00'
text.usd usda-text formatId= usd magic= b'#usda 1.0'
```

`text.usd` is the exam trap: extension `.usd`, id `usd`, **contents USDA**.

### 9. Real-world use case

A ingest tool rejects "binary" uploads into git. It must detect magic, not extension: a `.usd` that starts with `#usda` is allowed in the source repo; a `.usd` that starts with `PXR-USDC` goes to the publish store.

### 10. Common mistakes

> [!MISTAKE] `if path.endswith(".usd"): treat_as_crate()`. Fail on hand-written `.usd`.

> [!MISTAKE] Using `formatId == "usdc"` to mean crate. A crate `.usd` reports `usd`.

### 11. Exam traps

> [!TRAP] "`.usd` means USDA because the letters are USD ASCII." Default new `.usd` is crate.

> [!TRAP] "`formatId` is always the encoding name." For `.usd` it is the **generic** id `usd`.

### 12. Practice questions

**DE-031e** · Obj 4.3 · Difficulty: Medium · Type: Single choice
`CreateNew("shot.usd")` on USD 26.08 writes:

A. `#usda 1.0` text
B. Crate (`PXR-USDC`), format id `usd`
C. A USDZ zip
D. An empty folder

**DE-031f** · Obj 4.3 · Difficulty: Medium · Type: Single choice
A file named `layout.usd` starts with `#usda 1.0`. It is:

A. Invalid
B. Text USDA contents in a `.usd` name
C. Always crate
D. A payload

**Answers**

**DE-031e — B.** Review: §31.3.

**DE-031f — B.** Review: §31.3.

### 13. Exam takeaways

> [!KEY]
> - Detect `.usd` by magic: `#usda` vs `PXR-USDC` vs `PK`.
> - `CreateNew("*.usd")` → crate; format id `usd`.
> - `formatId` follows the extension plugin; magic follows the bytes.
> - FAQ item: "What file format is my .usd file?"

---

## 31.4 Conversion tools (`usdcat`, `usdzip`)

### 1. What is it?

**`usdcat`** prints or converts a layer (USDA ↔ USDC, optional flatten). **`usdzip`** builds a `.usdz`. Neither ships with `usd-core`. Python equivalents are `Sdf.Layer.Export` / `ExportToString` and `UsdUtils.CreateNewUsdzPackage`.

### 2. Why do we need it?

Obj 4.3 includes converting encodings. Exam questions show CLI flags. This book must also give you a command that runs in the lab venv.

### 3. Beginner explanation

`usdcat` is **cat for USD**: dump as text, or save as another encoding. `usdzip` is **zip for USD**, with the USDZ rules already applied.

*Where the analogy breaks:* `usdcat --flatten` is not `cat`. Flatten **bakes composition** into one layer (Chapter 34). Converting USDA→USDC does **not** flatten.

### 4. Technical explanation

Full toolset (`.norun` on `usd-core`):

```text
usdcat in.usda -o out.usdc
usdcat in.usdc                 # print USDA to stdout
usdcat --flatten shot.usda -o flat.usda
usdzip --asset root.usda out.usdz
```

Python stand-ins (verified 26.08):

| CLI | Python |
|-----|--------|
| `usdcat in.usda -o out.usdc` | `Sdf.Layer.FindOrOpen("in.usda").Export("out.usdc")` |
| `usdcat in.usdc` (print) | `print(layer.ExportToString())` |
| `usdzip --asset a out.usdz` | `UsdUtils.CreateNewUsdzPackage("a", "out.usdz")` |
| unpack | `UsdUtils.ExtractUsdzPackage(usdz, dir, verbose, force)` |

`Export` picks the encoding from the **destination extension**. `Export("x.usdc")` writes crate (magic `PXR-USDC`). Flatten is a different API (`Usd.Stage.Flatten`, Chapter 34).

### 5. Mental model

```text
  usdcat   =  Layer.Export / ExportToString     (encoding)
  usdzip   =  CreateNewUsdzPackage              (package)
  flatten  =  Stage.Flatten                     (composition; Ch 34)
```

### 6. Simple example

`tiny.usda` exported to `fromcat.usdc` starts with `PXR-USDC`. Packaging is Section 31.2.

### 7. USDA example

No new syntax. Input is any layer from 31.1. Output crate is binary; you check magic, not USDA.

### 8. Python example

```python
from pxr import Sdf, Usd, UsdGeom

tiny = Usd.Stage.CreateNew("tiny.usda")
UsdGeom.Xform.Define(tiny, "/W")
tiny.GetRootLayer().Save()
print("usdcat-equivalent export:",
      Sdf.Layer.FindOrOpen("tiny.usda").Export("fromcat.usdc"))
print("fromcat magic:", open("fromcat.usdc", "rb").read(9))
```

**Expected output**

```text
usdcat-equivalent export: True
fromcat magic: b'PXR-USDC\x00'
```

CLI (not run; `usd-core` has no `usdcat`):

```{.bash .norun}
usdcat tiny.usda -o fromcat.usdc
usdzip --asset root.usda out.usdz
```

### 9. Real-world use case

A publish job: `usdcat --flatten` is **not** used (that would smash the asset). Instead `Export` of `chair_geo.usda` → `chair_geo.usdc`, then `CreateNewUsdzPackage` for the client drop.

### 10. Common mistakes

> [!MISTAKE] Using `usdcat --flatten` when you only wanted crate. You baked away references.

> [!MISTAKE] `layer.Export("out.usd")` and assuming USDA. Destination `.usd` is crate by default, like `CreateNew`.

### 11. Exam traps

> [!TRAP] "`usdcat` is the only way to convert." `Sdf.Layer.Export` does it in-process.

> [!TRAP] "`usdzip` compresses with gzip." It stores, matching 31.2.

### 12. Practice questions

**DE-031g** · Obj 4.3 · Difficulty: Easy · Type: Single choice
`usd-core` provides `usdcat` as:

A. A PATH binary
B. Nothing; use `Sdf.Layer.Export`
C. `usdview --cat`
D. `ComplianceChecker`

**DE-031h** · Obj 4.3 · Difficulty: Medium · Type: Select two.
Which convert encoding **without** flattening composition?

A. `layer.Export("out.usdc")`
B. `usdcat in.usda -o out.usdc`
C. `Usd.Stage.Flatten()`
D. `usdcat --flatten`

**Answers**

**DE-031g — B.** Review: §31.4, F5.

**DE-031h — A and B.** C and D bake composition. Review: §31.4.

### 13. Exam takeaways

> [!KEY]
> - `usdcat -o` ↔ `Sdf.Layer.Export`; stdout ↔ `ExportToString`.
> - `usdzip` ↔ `CreateNewUsdzPackage`.
> - Flatten is a different operation (Ch 34).
> - Destination `.usd` / `.usdc` → crate magic.

---

## Chapter lab(s)

Lab 28 (dependencies, flatten, USDZ) uses these APIs with `LocalizeAsset`. This chapter is the encoding/package theory that lab needs.

## USDA reading exercises

**Exercise 31-A.** `tiny.usda` is 30 bytes and `tiny.usdc` is 582. A shot's lighting layer is 80 lines of overs. Which encoding, and why?

**Exercise 31-B.** `layout.usd` starts with `#usda 1.0` and `cache.usd` starts with `PXR-USDC`. What is each, and what is `CreateNew("x.usd")`?

**Answers**

**31-A.** USDA: it is an interface/department layer for review and merge; crate overhead would dominate and kill diffs. Review: §31.1.

**31-B.** `layout.usd` is text contents; `cache.usd` is crate; `CreateNew("x.usd")` writes crate with format id `usd`. Review: §31.3.

---

## Chapter review

### Summary

- USDA for humans and tiny interfaces; USDC for large published geometry. Crate is not always smaller.
- Typical asset: USDA entry + USDC payload.
- USDZ is an uncompressed zip; first USD file is the root; `compress_type` 0.
- ARKit packager often crates the root (`root.usdc` first).
- `.usd` encoding = magic bytes, not the extension. Default new `.usd` is crate; `formatId` is `usd`.
- `usdcat` / `usdzip` missing from `usd-core`; use `Export` and `CreateNewUsdzPackage`. Flatten ≠ convert.

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| Obj 4.3 / 7.3 | USDA vs USDC table, including tiny-file overhead |
| `PXR-USDC` | Crate / USDC |
| `#usda 1.0` | Text, even if the name is `.usd` |
| `PK` | Zip → probably USDZ |
| `formatId usd` | Generic `.usd` plugin; still inspect magic |
| `usdzip` | `CreateNewUsdzPackage`; STORE not DEFLATE |
| `usdcat -o` | `Layer.Export`; not flatten |
| `usdcat --flatten` | Composition bake (Ch 34), not encoding |

### Review questions

**R31-01** · Obj 4.3 · Single choice
Best encoding for a 20-line payload interface?
A. USDC always
B. USDA
C. USDZ of Alembic
D. Encrypted crate

**R31-02** · Obj 7.3 · Single choice
Best encoding for a 2 million point cache?
A. USDA in git
B. USDC
C. Comments in crate
D. Nested USDZ of USDA copies

**R31-03** · Obj 4.3 · Select two.
True about crate:
A. Magic `PXR-USDC`
B. Drops USDA comments
C. Always smaller than USDA
D. Is a zip of USDA

**R31-04** · Obj 4.3 · Single choice
USDZ compression in the worked example:
A. DEFLATE
B. Type 0 (stored)
C. gzip
D. Brotli

**R31-05** · Obj 4.3 · Single choice
Default layer of a USDZ is:
A. Any file named `default.usda`
B. The first USD archive member
C. Always `tex.png`
D. The session layer

**R31-06** · Obj 4.3 · Single choice
`CreateNew("a.usd")` magic:
A. `#usda 1.0`
B. `PXR-USDC`
C. `PK`
D. empty

**R31-07** · Obj 4.3 · Single choice
`formatId` of that `a.usd`:
A. `usda`
B. `usdc`
C. `usd`
D. `usdz`

**R31-08** · Obj 4.3 · Select two.
Detect encoding of `.usd` by:
A. Extension only
B. Magic bytes
C. `GetFileFormat().formatId` plus magic
D. File mtime

**R31-09** · Obj 4.3 · Single choice
`usdcat in.usda -o out.usdc` Python stand-in:
A. `Stage.Flatten`
B. `Sdf.Layer.FindOrOpen("in.usda").Export("out.usdc")`
C. `CreateNewUsdzPackage`
D. `ComplianceChecker`

**R31-10** · Obj 4.3 · Single choice
`usdzip` on `usd-core`:
A. On PATH
B. Use `UsdUtils.CreateNewUsdzPackage`
C. `zip -9`
D. `usdview --zip`

**R31-11** · Obj 4.3 · Single choice
`ExtractUsdzPackage` returned False because the dir existed. Fix:
A. Flatten first
B. Pass `force=True`
C. Rename to `.usdc`
D. Mute the root

**R31-12** · Obj 7.3 · Single choice
`usdcat --flatten` vs `Export` to `.usdc`:
A. The same
B. Flatten bakes composition; Export only changes encoding
C. Both delete payloads
D. Both require usdview

### Review answers

**R31-01 — B.** Review: §31.1.

**R31-02 — B.** Review: §31.1.

**R31-03 — A and B.** Tiny files can be larger as crate (not C); zip is USDZ (not D). Review: §31.1.

**R31-04 — B.** Review: §31.2.

**R31-05 — B.** Review: §31.2.

**R31-06 — B.** Review: §31.3.

**R31-07 — C.** Review: §31.3.

**R31-08 — B and C.** Review: §31.3.

**R31-09 — B.** Review: §31.4.

**R31-10 — B.** Review: §31.4.

**R31-11 — B.** Review: §31.2.

**R31-12 — B.** Review: §31.4, Ch 34.

## Further reading

- [S04] OpenUSD USDZ specification: https://openusd.org/release/spec_usdz.html
- [S08] USD FAQ — "What file format is my .usd file?": https://openusd.org/release/usdfaq.html
- [S06] Toolset (`usdcat`, `usdzip`): https://openusd.org/release/toolset.html
- [S11] Maximizing USD Performance — crate vs text: https://openusd.org/release/maxperf.html
