# The NCP-OUSD Exam

## Exam facts

Verified on 7 October 2026 against the official NVIDIA certification page. Check again before booking.

| Fact | Value |
|------|-------|
| Full name | NVIDIA-Certified Professional: OpenUSD Development (NCP-OUSD) |
| Level | Professional (NVIDIA describes it as intermediate-level) |
| Number of questions | 60–70 |
| Time limit | 120 minutes |
| Delivery | Online, remotely proctored. You need a Certiverse account to access the exam |
| Price | US $200 |
| Language | English |
| Validity | 2 years from issue. Recertify by retaking the exam |
| Credential | Digital badge and optional certificate |
| Passing score | Not published on the certification page |

**Who it is for.** NVIDIA describes the candidate as a developer who builds, maintains, and optimizes 3D content pipelines with OpenUSD. The stated prerequisite is two to three years of OpenUSD plus Python or C++ experience, **or** completion of the study-guide materials. This book is designed to cover that study-guide material from zero.

## The blueprint

The exam has eight scored domains. The weight is the share of questions from that domain.

| Domain | Weight | ≈ Questions (of 65) | Chapters |
|--------|--------|---------------------|----------|
| Composition | 23% | 15 | 14–22 |
| Data Exchange | 15% | 10 | 27–31 |
| Pipeline Development | 14% | 9 | 32–35 |
| Data Modeling | 13% | 8 | 8–13 |
| Debugging and Troubleshooting | 11% | 7 | 42–44 |
| Content Aggregation | 10% | 7 | 23–26 |
| Visualization | 8% | 5 | 39–41 |
| Customizing USD | 6% | 4 | 36–38 |

> [!KEY] Composition (23%) is almost a quarter of the exam. Data Exchange and Pipeline Development together add another 29%.

```text
Share of exam (each # = 1%)

Composition            #######################  23%
Data Exchange          ###############          15%
Pipeline Development   ##############           14%
Data Modeling          #############            13%
Debugging              ###########              11%
Content Aggregation    ##########               10%
Visualization          ########                  8%
Customizing USD        ######                    6%
```

## Official objectives

NVIDIA's study guide lists specific tasks under each domain. They are summarized below, with the chapters that teach them. Numbers follow NVIDIA's numbering (domains in the guide's alphabetical order). Some objectives appear under two domains; the book teaches them once and cross-references them.

### 1. Composition (23%)

| Obj | You should be able to… | Ch |
|-----|------------------------|----|
| 1.1 | Change the strength of an opinion | 14, 19, 21 |
| 1.2 | Choose an instancing style for data at different scales | 22, 26 |
| 1.3 | Compare references, payloads, and sublayers, and know when to use each | 3, 15–17 |
| 1.4 | Reuse the same animation on several elements at different time offsets | 10, 16 |
| 1.5 | Design layering strategies for multi-user workflows | 15, 22 |
| 1.6 | Explain LIVERPS in simple terms | 14, 21 |
| 1.7 | Know when variants are, and are not, the right way to structure assets | 18 |
| 1.8 | Find why an opinion from one layer does not take effect | 20–22 |
| 1.9 | Prepare an internal asset for delivery to external parties | 22, 34 |
| 1.10 | Remove properties from instanced component prims in an assembly | 22, 24 |
| 1.11 | Split a monolithic asset into collaborative workstreams | 22 |

### 2. Content Aggregation (10%)

| Obj | You should be able to… | Ch |
|-----|------------------------|----|
| 2.1 | Add a new prototype to a PointInstancer | 25 |
| 2.2 | Change the color of an instance-proxy mesh without breaking instancing | 24 |
| 2.3 | Hide PointInstancer instances efficiently | 25 |
| 2.4 | Use instances for efficient reuse in large scenes | 23, 24, 26 |
| 2.5 | Remove properties from instanced component prims in an assembly | 24 |

### 3. Customizing USD (6%)

| Obj | You should be able to… | Ch |
|-----|------------------------|----|
| 3.1 | Build a USD plugin against a given USD version | 35, 36 |
| 3.2 | Build USD from source with custom dependencies | 35 |
| 3.3 | Create custom model kinds when appropriate | 6, 38 |
| 3.4 | Create custom schemas for proprietary data | 6, 37 |
| 3.5 | Integrate a custom asset resolver | 33, 38 |
| 3.6 | Use schemas for nonstandard data during import/export | 37 |
| 3.7 | Write a Hydra scene index plugin that generates renderable geometry | 38 |
| 3.8 | Write an asset resolver that generates in-memory renderable prims | 38 |

### 4. Data Exchange (15%)

| Obj | You should be able to… | Ch |
|-----|------------------------|----|
| 4.1 | Convert USD assets to common 3D formats (such as glTF) with fidelity | 27 |
| 4.2 | Document conceptual mappings between USD and another data model (such as MaterialX) | 27 |
| 4.3 | Explain USDC vs. USDA trade-offs | 7, 31 |
| 4.4 | Implement a round-trip pipeline between a DCC and USD | 27, 35 |
| 4.5 | Use schemas for nonstandard data during import/export | 29, 37 |
| 4.6 | Write a validator for assets exported from a DCC | 30 |
| 4.7 | Write an exporter or converter to USD | 28, 29 |
| 4.8 | Write or extend a USD importer in a DCC | 29, 35 |

### 5. Data Modeling (13%)

| Obj | You should be able to… | Ch |
|-----|------------------------|----|
| 5.1 | Add a primvar to a mesh | 11 |
| 5.2 | Choose the right value types for attribute data | 9, 10 |
| 5.3 | Represent custom metadata | 5, 12 |
| 5.4 | Retrieve the properties of a prim | 2, 4, 5, 8 |
| 5.5 | Understand what causes unexpected visual results | 13 |
| 5.6 | Update a mesh's extent after changing its points | 13 |

### 6. Debugging and Troubleshooting (11%)

| Obj | You should be able to… | Ch |
|-----|------------------------|----|
| 6.1 | Know when `SdfChangeBlock` relieves performance bottlenecks | 8, 34, 44 |
| 6.2 | Find why an opinion from one layer does not take effect | 20, 42 |
| 6.3 | Resolve asset-management issues | 33, 42 |
| 6.4 | Understand what causes unexpected visual results | 13, 42, 44 |
| 6.5 | Use diagnostics and profiling tools (TfDebug, diagnostic delegates, Trace, TfMallocTag) | 43 |

### 7. Pipeline Development (14%)

| Obj | You should be able to… | Ch |
|-----|------------------------|----|
| 7.1 | Convert USD assets to common 3D formats with fidelity | 27 |
| 7.2 | Document asset structure guidelines | 23, 32 |
| 7.3 | Explain USDC vs. USDA trade-offs | 7, 31 |
| 7.4 | Implement round-trip pipelines between a DCC and USD | 35 |
| 7.5 | Integrate custom resolvers to manage asset paths | 33 |
| 7.6 | Represent custom metadata | 12 |
| 7.7 | Validate that asset paths are formatted correctly | 33 |
| 7.8 | Write or extend a USD importer in a DCC | 35 |

### 8. Visualization (8%)

| Obj | You should be able to… | Ch |
|-----|------------------------|----|
| 8.1 | Add a primvar to a mesh | 11, 39 |
| 8.2 | Assign UsdPreviewSurface materials | 40 |
| 8.3 | Bind materials to a mesh | 40 |
| 8.4 | Build a UsdPreviewSurface network that reads diffuse color from a primvar | 40 |

## What the questions look like

NVIDIA's study guide includes sample questions. They show these styles, which this book's practice material copies in **format only**:

- **Single answer**: choose one of four options (A–D).
- **Multiple select**: "Select two options" or "Select three options". The question always tells you how many to pick.
- **USDA reading**: one or more short `.usda` files are shown, and you must work out the composed result, such as "What is the final value of this attribute?" or "Why doesn't this variant selection take effect?"
- **Scenario**: a pipeline or debugging situation where you choose the best design or explanation.

> [!TRAP] In USDA-reading questions, check **every** file shown, including which file is the root layer and the order of arcs inside `prepend references = [...]`. One overlooked local opinion usually decides the answer.

## Exam-day strategy

- **Pace:** 120 minutes for 60–70 questions is about **1 min 45 s per question**. Aim to finish a first pass by minute 90.
- **First pass:** answer what you know. Flag anything that needs long USDA tracing and come back to it.
- **USDA questions:** write the layer stack and arcs on your scratch area (if the proctoring rules allow it) and apply LIVERPS step by step (Chapter 21).
- **Multiple select:** pick exactly the number asked. Each option should be true *on its own*.
- **Eliminate:** distractors often name real APIs used in the wrong place, or swap "stronger" and "weaker". Rule those out first.
- **Logistics:** read NVIDIA's and the proctoring provider's rules before exam day: ID, system check, a quiet room with a clear desk, and a stable internet connection. Requirements can change, so follow the current official instructions.

> [!EXAM TIP] Several objectives appear in two domains (for example "why doesn't an opinion take effect" is 1.8 and 6.2). Mastering one skill earns marks in both.
