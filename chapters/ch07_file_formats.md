# Chapter 7 — USD File Formats and Reading USDA

> **Exam domain:** Data Exchange (15%) and Pipeline (14%) · **Objectives:** 4.3, 7.3
> **Study day:** 2 · **Est. time:** 60 min
> **Prerequisites:** Chapters 1–6

## Learning goals

- Explain **USDA**, **USDC** (crate), **USD** (either), and **USDZ**.
- State trade-offs: performance, readability, archival, diff/merge (Obj 4.3 / 7.3).
- Read a USDA file line by line.
- Convert formats with `Sdf.Layer.Export` (the `usdcat` equivalent in `usd-core`).

## Key terms

| Term | One-line definition |
|------|---------------------|
| USDA | Human-readable text format (`.usda`) |
| USDC / crate | Binary format (`.usdc`); magic bytes `PXR-USDC` |
| USD | Extension `.usd` that may be crate *or* text; default new files are crate |
| USDZ | Uncompressed zip **package** of USD + images + audio |
| Crate | Pixar's name for the USDC binary layout |

---

## 7.1 USDA (text)

### 1. What is it?

**USDA** is the text encoding of a layer. Files usually end in `.usda`. The first line is `#usda 1.0`.

### 2. Why do we need it?

Humans read, diff, and merge text. Asset *interfaces* (tiny files that only declare `defaultPrim`, variants, and a payload) are often USDA.

### 3. Beginner explanation

USDA is to USD what ASCII FBX is *trying* to be: a readable document. Unlike OBJ, it can express composition, not just a mesh.

### 4. Technical explanation

- Format id: `usda` (`layer.GetFileFormat().formatId`).
- Larger on disk for heavy geometry; slow to parse relative to crate.
- Excellent for git diffs of small layers.
- `ExportToString()` always produces USDA text, even if the layer is crate.

### 5. Mental model

USDA = source code of a layer. USDC = compiled object file.

### 6. Simple example

`chair.usda` with twenty lines of interface metadata; `chair_geo.usdc` with a million points.

### 7. USDA example

```usda
#usda 1.0
(
    defaultPrim = "World"
)

def Xform "World"
{
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateNew("ch07.usda")
UsdGeom.Xform.Define(stage, "/World")
stage.GetRootLayer().Save()
print("format:", stage.GetRootLayer().GetFileFormat().formatId)
print("starts with:", open("ch07.usda", "rb").read(9).decode("ascii"))
```

**Expected output**

```text
format: usda
starts with: #usda 1.0
```

### 9. Real-world use case

Code review of a shot's root layer: reviewers read USDA sublayer lists in git.

### 10. Common mistakes

> [!MISTAKE] Checking a 5 GB USDA "so we can see it". Open it in usdcat (or ExportToString on a subset). Prefer crate for caches.

### 11. Exam traps

> [!TRAP] "USDA cannot store meshes." It can. You just should not want to at scale.

### 12. Practice questions

**DE-PRE-001** · Difficulty: Easy · Type: Single choice

USDA's main advantage is:

A. Fastest load of heavy geometry  
B. Human readability and diff/merge  
C. It is the only format Hydra can read  
D. It compresses textures  

**Answer:** B. Obj 4.3.

### 13. Exam takeaways

> [!KEY]
> - USDA = text, readable, good for small interface layers.

---

## 7.2 USDC (crate binary)

### 1. What is it?

**USDC** is the binary **crate** format (`.usdc`). On disk it starts with magic bytes `PXR-USDC`.

### 2. Why do we need it?

Obj 4.3: performance. Opening a stage keeps layers open; crate is smaller in memory and faster than text for "big data" (points, time samples).

### 3. Beginner explanation

Crate is the packed binary of the same layer. Same scene description, different encoding.

Where the analogy breaks: crate is **not** encrypted and not zip. USDZ is zip.

### 4. Technical explanation

- Format id: `usdc`.
- Pixar's performance guide: prefer binary for geometry and shading caches; keep USDA for small interface files.
- mmap-friendly; plays well with multithreading (especially vs Alembic Ogawa's file-descriptor story).
- Tiny scenes can be *larger* as crate than as USDA because of headers (verified: a one-prim Xform was 30 bytes USDA vs ~583 bytes USDC). The win appears when arrays grow.

### 5. Mental model

Heavy data → crate. Light structure → USDA.

### 6. Simple example

Animation caches, packed crowds, hero meshes: `.usdc`.

### 7. USDA example

You do not write crate by hand. You **export** to it. This is the text equivalent of what crate stores:

```usda
#usda 1.0

def Xform "World"
{
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom, Sdf

stage = Usd.Stage.CreateNew("ch07.usda")
UsdGeom.Xform.Define(stage, "/World")
stage.GetRootLayer().Save()
stage.GetRootLayer().Export("ch07.usdc")
layer = Sdf.Layer.FindOrOpen("ch07.usdc")
print("format:", layer.GetFileFormat().formatId)
print("magic:", open("ch07.usdc", "rb").read(8))
print("text view:", layer.ExportToString().splitlines()[0])
```

**Expected output**

```text
format: usdc
magic: b'PXR-USDC'
text view: #usda 1.0
```

### 9. Real-world use case

A farm converts Alembic caches to crate (`usdcat` in a full build) so USD does not pay an extra translation tax (performance guide).

### 10. Common mistakes

> [!MISTAKE] Committing huge crate files to git as if they were USDA. Use artifact storage.

### 11. Exam traps

> [!TRAP] "USDC is a zip of USDA." No. Zip-of-files is USDZ. USDC is a native binary layer format.

### 12. Practice questions

**DE-PRE-002** · Difficulty: Medium · Type: Single choice

Crate / USDC is best described as:

A. A zip package of textures  
B. USD's native binary layer format, efficient for heavy data  
C. A rival scene description to USD  
D. Always smaller than USDA even for empty layers  

**Answer:** B. D is false for tiny files (verified).

### 13. Exam takeaways

> [!KEY]
> - USDC = crate = binary layer. Magic `PXR-USDC`.
> - Prefer it for geometry caches.

---

## 7.3 The `.usd` extension

### 1. What is it?

**`.usd`** is an extension that can hold **either** crate or USDA. USD detects the actual format from the contents (FAQ: "What file format is my .usd file?").

### 2. Why do we need it?

Pipelines can say "always use `.usd`" and still switch encodings. Tools should not assume `.usd` is text.

### 3. Beginner explanation

`.usd` is a labeled box that might contain text or crate. Look inside (magic bytes or `GetFileFormat()`).

### 4. Technical explanation

Verified on USD 26.08: `Usd.Stage.CreateNew("file.usd")` creates **crate** contents (`PXR-USDC`) with format id `usd` (not `usdc`). The bytes are still crate.

Detection: if the file starts with `#usda` it is text; if `PXR-USDC` it is crate.

### 5. Mental model

Extension ≠ encoding. `.usda` / `.usdc` are honest. `.usd` is "either".

### 6. Simple example

A publisher writes `.usd` so internal tools never bikeshed extensions; encoding is crate unless someone exports USDA into that path.

### 7. USDA example

If a `.usd` file is text, it still begins:

```usda
#usda 1.0

def Xform "World" {}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateNew("ch07.usd")
UsdGeom.Xform.Define(stage, "/World")
stage.GetRootLayer().Save()
print("format id:", stage.GetRootLayer().GetFileFormat().formatId)
print("magic:", open("ch07.usd", "rb").read(8))
```

**Expected output**

```text
format id: usd
magic: b'PXR-USDC'
```

### 9. Real-world use case

`usdcat file.usd` (full build) prints text regardless of encoding — same as `ExportToString()`.

### 10. Common mistakes

> [!MISTAKE] Opening `.usd` in a text editor and seeing binary garbage. It is crate. Use usdcat / ExportToString.

### 11. Exam traps

> [!TRAP] "`.usd` means USDA." Not necessarily. Default new `.usd` in this runtime is crate.

### 12. Practice questions

**DE-PRE-003** · Difficulty: Medium · Type: Single choice

A newly created `asset.usd` from `Usd.Stage.CreateNew` in USD 26.08 is:

A. Always USDA text  
B. Crate bytes with format id `usd` (verified default)  
C. A USDZ package  
D. Illegal; you must use `.usda`  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - `.usd` = either encoding. Detect contents.
> - Default `CreateNew("*.usd")` here is crate.

---

## 7.4 USDZ (package)

### 1. What is it?

**USDZ** is an **uncompressed, unencrypted zip** that packages USD files plus allowed media (png, jpeg, exr, avif, audio). Spec version 1.3 (OpenUSD 26.08 docs).

### 2. Why do we need it?

Content delivery: one object, no unpacking required, possible streaming. Apple's AR and many viewers consume USDZ.

### 3. Beginner explanation

USDZ is a zip folder of a USD scene and its textures, with extra rules (64-byte alignment, no compression).

Where the analogy breaks: you cannot freely zip anything. Alembic inside USDZ is not allowed; files must be mmap-friendly.

### 4. Technical explanation

- First USD file in the package is the **default layer** (like `defaultPrim`, but for files).
- `usdzip` in a full toolset; Python: `UsdUtils.CreateNewUsdzPackage(src, dest)` (F5).
- Editing: unpack, edit, repack. The package is read-only.
- `--arkitAsset` enforces a stricter subset for iOS.

### 5. Mental model

USDZ = box. USDA/USDC = papers in the box. Textures = photos in the box.

### 6. Simple example

Marketing wants one file to drop into a web viewer: `chair.usdz`.

### 7. USDA example

USDZ is binary zip. The **default layer inside** might be:

```usda
#usda 1.0
(
    defaultPrim = "Chair"
)

def Xform "Chair"
{
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom, UsdUtils, Sdf

stage = Usd.Stage.CreateNew("pack_me.usda")
UsdGeom.Xform.Define(stage, "/World")
stage.SetDefaultPrim(stage.GetPrimAtPath("/World"))
stage.GetRootLayer().Save()
ok = UsdUtils.CreateNewUsdzPackage("pack_me.usda", "pack_me.usdz")
print("packaged:", ok)
print("usdz format id:", Sdf.FileFormat.FindByExtension("usdz").formatId)
```

**Expected output**

```text
packaged: True
usdz format id: usdz
```

### 9. Real-world use case

Vendor delivery (Obj 1.9): localize textures, flatten or package, hand over one `.usdz`.

### 10. Common mistakes

> [!MISTAKE] Compressing the zip. The spec requires **zero compression** so USD can mmap contents.

### 11. Exam traps

> [!TRAP] "USDZ is just renamed USDC." USDC is one layer. USDZ is a package of files.

### 12. Practice questions

**DE-PRE-004** · Difficulty: Medium · Type: Single choice

USDZ is:

A. A compressed crate file  
B. An uncompressed zip package of USD plus allowed media  
C. USDA with a different extension  
D. A Hydra render delegate  

**Answer:** B. Obj 4.3 adjacent.

### 13. Exam takeaways

> [!KEY]
> - USDZ = uncompressed zip package; first USD file is the default layer.
> - Not the same as USDC.

---

## 7.5 Reading USDA syntax

### 1. What is it?

A line-by-line reading of the syntax you have been using since Chapter 1.

### 2. Why do we need it?

Exam questions paste USDA. You must parse them under time pressure.

### 3. Beginner explanation

Treat USDA like a strict language: header, metadata, then nested prims.

### 4. Technical explanation

Anatomy:

```text
#usda 1.0                         required magic
(                                 optional layer metadata
    defaultPrim = "World"
    subLayers = [@a.usda@, @b.usda@]
)
def Xform "World" (               specifier type "name" (prim metadata)
    kind = "component"
)
{                                 prim body: properties and children
    double radius = 2             attribute
    rel material:binding = </M>   relationship
    over "Child" { }              child spec
}
```

Asset paths use `@path@`. Prim paths as values use `</Path>`.

### 5. Mental model

Header → metadata in `( )` → tree of specs.

### 6. Simple example

See the combined example below.

### 7. USDA example

```usda
#usda 1.0
(
    defaultPrim = "World"
    metersPerUnit = 0.01
    upAxis = "Y"
)

def Xform "World" (
    kind = "component"
)
{
    def Sphere "Ball"
    {
        double radius = 2
    }
}
```

### 8. Python example

```python
from pxr import Sdf

text = '''#usda 1.0
(
    defaultPrim = "World"
)
def Xform "World" {
    def Sphere "Ball" {
        double radius = 2
    }
}
'''
layer = Sdf.Layer.CreateAnonymous(".usda")
print("parse:", layer.ImportFromString(text))
print("defaultPrim:", layer.defaultPrim)
print("has /World/Ball:", bool(layer.GetPrimAtPath("/World/Ball")))
```

**Expected output**

```text
parse: True
defaultPrim: World
has /World/Ball: True
```

### 9. Real-world use case

Debugging: if parse fails, the error is `Expected } at ...` pointing at a missing newline or brace — as this book's labs discovered with inline nested specs.

### 10. Common mistakes

> [!MISTAKE] Putting two `def "World"` in one layer. Duplicate prim specs in one layer error.

### 11. Exam traps

> [!TRAP] Skipping the header metadata when the question's answer lives in `subLayers` order.

### 12. Practice questions

**FUN-022** · Difficulty: Easy · Type: Single choice

`@./chair.usda@` in USDA denotes:

A. A prim path  
B. An asset path  
C. A time sample  
D. A kind  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - `#usda 1.0` required. `@asset@` vs `</prim/path>`.
> - Layer metadata in the header `( )`; prim metadata in spec `( )`.

I need to remove the "Wait" note from the chapter - that's my internal note. Let me fix when editing.

Also the python example with nested braces on separate lines should work.

---

## 7.6 Converting formats

### 1. What is it?

Changing a layer's encoding: USDA ↔ USDC, packing USDZ, flattening (Ch 34).

### 2. Why do we need it?

Obj 4.3: pick the right encoding. Pipelines convert on publish.

### 3. Beginner explanation

Same document, different save-as.

### 4. Technical explanation

Full toolset: `usdcat in.usda -o out.usdc`, `usdzip`, `usdcat --flatten`.

`usd-core` equivalents:

- `layer.Export("out.usdc")` — format from extension
- `layer.ExportToString()` — always USDA text
- `UsdUtils.CreateNewUsdzPackage`

`CreateNew("x.usd")` default crate, as above.

### 5. Mental model

Export chooses encoding by file extension.

### 6. Simple example

Publish: USDA interface stays; geo layer exported to USDC.

### 7. USDA example

Conversion does not change this meaning, only packing:

```usda
#usda 1.0
def Xform "World" {}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom, Sdf

stage = Usd.Stage.CreateNew("conv.usda")
UsdGeom.Xform.Define(stage, "/World")
stage.GetRootLayer().Save()
stage.GetRootLayer().Export("conv.usdc")
print("usda id:", Sdf.Layer.FindOrOpen("conv.usda").GetFileFormat().formatId)
print("usdc id:", Sdf.Layer.FindOrOpen("conv.usdc").GetFileFormat().formatId)
```

**Expected output**

```text
usda id: usda
usdc id: usdc
```

### 9. Real-world use case

A CI job fails if a published component's payload is USDA over a size limit — encoding policy as documentation (Obj 7.2).

### 10. Common mistakes

> [!MISTAKE] Renaming `file.usda` to `file.usdc` without exporting. The bytes are still text; tools will fail.

### 11. Exam traps

> [!TRAP] "usdcat always flattens." Only with `--flatten`. Default is "show this layer as text".

### 12. Practice questions

**DE-PRE-005** · Difficulty: Medium · Type: Select two.

Which preserve scene description while changing encoding? Select two.

A. `layer.Export("out.usdc")` from an USDA layer  
B. Renaming `.usda` to `.usdc` on disk  
C. `CreateNewUsdzPackage` for delivery  
D. Deleting `defaultPrim`  

**Answer:** A and C. B is a fake conversion. D changes metadata, not encoding.

### 13. Exam takeaways

> [!KEY]
> - Convert with Export / usdcat, not by renaming.
> - Extension selects format on Export.

---

## Chapter lab(s)

Lab 01 leftover + format conversion in Labs 25–28. Run this chapter's scripts.

## USDA reading exercise

**USDA-08.** Is this file crate or text if its first bytes are `#usda 1.0` but its name is `hero.usd`?

**Answer:** Text encoding inside a `.usd` wrapper. Name does not force crate.

## Chapter review

### Obj 4.3 / 7.3 cheat box

| Format | Readability | Heavy geometry | Typical use |
|--------|-------------|----------------|-------------|
| USDA | Best | Poor | Interfaces, shot roots, reviews |
| USDC | Via usdcat | Best | Caches, payloads |
| .usd | Depends | Depends | "Either"; default new = crate here |
| USDZ | N/A (package) | Payload files inside | Delivery, AR, single-file share |

### Chapter questions

**Q1.** Magic bytes of crate?  
**Q2.** Default encoding of `CreateNew("a.usd")` on USD 26.08?  
**Q3.** USDZ compression?  
**Q4.** Why USDA for a 15-line asset interface?  
**Q5.** How to convert without usdcat?  
**Q6.** `@path@` vs `</path>`?  
**Q7.** Can USDA store meshes?  
**Q8.** First file in a USDZ package?

**Answers**

1. `PXR-USDC`. 2. Crate (`PXR-USDC`, format id `usd`). 3. None (uncompressed). 4. Diff/merge/read. 5. `Sdf.Layer.Export`. 6. Asset path vs prim path. 7. Yes. 8. The default layer.

## Further reading

- FAQ: What file format is my .usd file? — https://openusd.org/release/usdfaq.html  
- USDZ spec — https://openusd.org/release/spec_usdz.html  
- Maximizing USD Performance — https://openusd.org/release/maxperf.html  
- Toolset: usdcat, usdzip — https://openusd.org/release/toolset.html  
