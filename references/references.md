# References and further reading

Sources used to write this book. **Tier order:** NVIDIA exam materials, then OpenUSD docs/API, then the installed `usd-core` 26.8 runtime, then NVIDIA Learn OpenUSD / Omniverse, then ASWF / AOUSD, then community guides. Third-party “practice exam” banks were not used as sources. URLs accessed 2026-10-07 unless noted. Recheck the certification page before you book.

Short quotes (≤ two sentences) from these sources are attributed in chapters. Practice questions, mocks, and flashcards are **original**.

## Exam and blueprint

1. NVIDIA. *OpenUSD Development Professional Certification (NCP-OUSD).* https://www.nvidia.com/en-us/learn/certification/openusd-development-professional/ — 60–70 questions, 120 minutes, US$200, English, Certiverse, two-year validity. Weights re-checked 2026-10-08.

2. NVIDIA. *NVIDIA-Certified Professional: OpenUSD Development Exam Study Guide,* version 1.1.0 (doc 4379350, Oct 2025). PDF. Objectives 1.1–8.4 and reading lists. Sample questions were used **only** to learn format (single, select-N, USDA stems); none are reproduced.

## OpenUSD documentation and API

3. Pixar Animation Studios / AOUSD. *OpenUSD documentation* (release 26.08). https://openusd.org/release/index.html

4. *OpenUSD Glossary* (LIVERPS, layer offset, edit target, flatten, primvar, over). https://openusd.org/release/glossary.html

5. *USD Tutorials.* https://openusd.org/release/tut_usd_tutorials.html

6. *OpenUSD C++ / Python API reference.* https://openusd.org/release/api/index.html — UsdStage, UsdPrim, composition, SdfChangeBlock, PointInstancer, MaterialBindingAPI, UsdLux, Ar, Kind, Plug.

7. *USD Toolset* (usdcat, usdchecker, usdzip, usdview, usdresolve, usdtree). https://openusd.org/release/toolset.html — this book’s pip `usd-core` ships **none** of these binaries; chapters give Python stand-ins.

8. *USD FAQ* (sublayers vs references, over vs typeless def, `.usd` detection). https://openusd.org/release/usdfaq.html

9. *USDZ File Format Specification* (v1.3). https://openusd.org/release/spec_usdz.html — store-only zip.

10. *UsdPreviewSurface Specification.* https://openusd.org/release/spec_usdpreviewsurface.html

11. *Maximizing USD Performance.* https://openusd.org/release/maxperf.html

12. *OpenUSD source and CHANGELOG.* https://github.com/PixarAnimationStudios/OpenUSD — latest release 26.08 (2026-07-20).

13. *usd-core on PyPI.* https://pypi.org/project/usd-core/ — this book verified **26.8**.

## NVIDIA Learn OpenUSD and Omniverse

14. NVIDIA. *Learn OpenUSD.* https://docs.nvidia.com/learn-openusd/latest/index.html — curriculum that prepares for the certification (composition, kinds, aggregation, data exchange).

15. NVIDIA Omniverse. *USD documentation.* https://docs.omniverse.nvidia.com/usd/latest/index.html

16. NVIDIA. *Principles of Scalable Asset Structure in OpenUSD.* https://docs.omniverse.nvidia.com/usd/latest/learn-openusd/independent/asset-structure-principles.html

## Industry guidelines

17. ASWF USD Working Group. *Asset Structure Guidelines.* https://github.com/usd-wg/assets/blob/main/docs/asset-structure-guidelines.md

18. Alliance for OpenUSD (AOUSD). https://aousd.org

## Community (tier 6 — never the sole source)

19. Cheller’s *USD Survival Guide.* https://lucascheller.github.io/VFX-UsdSurvivalGuide/

## How this book cites them

In chapters: `[S04] OpenUSD Glossary — LIVERPS`. Never “see the link instead of an explanation.” Runtime disagreements are resolved by running `usd-core` 26.8 (tier 3) and marking `> [!VERSION]`.
