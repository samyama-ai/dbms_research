---
id: <NN-topic-slug>/<problem-slug>        # stable identity — never change once assigned
title: "<Problem Title>"
topic: <NN-topic-slug>
status: open | partially-solved | empirically-open | solved-but-impractical | stale
first_added: <YYYY-MM>                     # iteration it first appeared
last_reviewed: <YYYY-MM>                   # iteration last verified
last_substantive_update: <YYYY-MM>
stale_since: ""                            # set to <YYYY-MM> when no longer actively worked
provenance: synthesized                    # synthesized | verified (of the PROSE)
refs_checked: <YYYY-MM>                    # iteration every section-9 reference was
                                           # resolved against DBLP/Crossref/DataCite/arXiv
refs_unverified: <N>                       # omit when 0; count of references no source could confirm
---

# <Problem Title>

> **Topic:** <topic name> · **ID:** `<NN-topic-slug>/<problem-slug>` · **Status:** <open | partially-solved | solved-but-impractical | empirically-open>

## 1. Problem Statement

A precise, self-contained statement of the problem. Include the input, the output,
the objective/decision predicate, and what "solving" means. Distinguish the
**decision**, **optimization**, and **counting/enumeration** variants where relevant.

## 2. Mathematical Foundations

The formal model. Define the data model (relations, multisets, graphs, streams, …),
the notation, and the relevant structures. State the key definitions and theorems the
problem rests on (e.g., relational algebra equivalences, the chase, submodularity,
information-theoretic bounds, AGM bound, VC dimension, etc.). Use LaTeX-style inline
math where useful: `$...$` / `$$...$$`.

## 3. State of the Art (SOTA)

The best-known algorithms, systems, and results. Name the algorithm/system, the
result it achieves, and the venue/year. Separate **theory SOTA** from **systems SOTA**
when they differ.

## 4. Upper Bound

Best-known algorithmic upper bound — time/space complexity, approximation ratio, or
competitive ratio — with the result that establishes it.

## 5. Lower Bound

Best-known lower bound / hardness — NP-hardness, fine-grained (SETH/3SUM/APSP)
conditional bounds, information-theoretic limits, cell-probe bounds, communication
complexity, impossibility results (CAP/FLP). State the model the bound holds in.

## 6. The Gap

What separates the upper and lower bounds. Is the problem closed (matching bounds),
or is there a genuine open gap? What would close it?

## 7. Current Research (as of June 2026)

Active directions and the groups/people pursuing them. Flag frontier claims with
*(frontier — verify)* where confidence is limited beyond early 2026.

## 8. Future Work

Open directions researchers in the area have articulated.

## 9. Key References

- **[Foundational]** Author(s). *Title.* Venue, Year. (link if stable)
- **[SOTA]** Author(s). *Title.* Venue, Year.
- **[Survey]** Author(s). *Title.* Venue, Year.
- **[Docs]** Vendor or project documentation, or a format specification.
- **[Artifact]** A code repository, benchmark or dataset.

`[Docs]` and `[Artifact]` mark a source that is real and citable but is **not a
paper**, so no bibliographic database indexes it. The reference checker skips
them for that reason: counting vendor documentation as "no DBLP record" reads as
a missing paper and buries the ones that are.

---
*Part of the [DBMS Research catalog](../../README.md). Schema: [TEMPLATE.md](../../TEMPLATE.md).*
