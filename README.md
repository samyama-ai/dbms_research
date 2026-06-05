# DBMS Research — 1000+ Open & Hard Problems

![Problems](https://img.shields.io/badge/problems-1053-blue) ![Topics](https://img.shields.io/badge/topics-35-green) ![References](https://img.shields.io/badge/linked%20references-6700%2B-orange) ![License](https://img.shields.io/badge/license-CC%20BY%204.0-lightgrey)

A structured, research-grade catalog of **1,053 open and hard problems across the database management systems (DBMS) space** — from relational theory and query optimization to vector search, learned components, and self-driving databases. Each problem is a standalone Markdown page with a formal statement, the mathematical foundations it rests on, the current state of the art, the best-known **upper and lower bounds** (and the gap between them), active research directions as of mid-2026, and **linked references**.

It is meant as a **map of where the hard questions are** — for graduate students choosing a thesis, researchers scanning adjacent subfields, engineers who want the theory behind a system limitation, and anyone who wants to know what is *actually still open* in databases.

> ⚠️ **Read the [provenance & honesty note](#-provenance--honesty-note) before citing anything.** This is a synthesized study aid, not a primary source.

---

## At a glance

| | |
|---|---|
| **Problems** | 1,053 across 35 topics (~30 each) |
| **Every problem documents** | statement · math foundations · SOTA · upper bound · lower bound · the gap · current research (June 2026) · future work · references · worked example |
| **Linked references** | 6,700+ links to arXiv / DOI / ACM DL / DBLP, each verified or flagged `*(unverified)*` |
| **Worked examples** | 1,053 — every page has a small concrete instance |
| **Content** | ~1.16M words |

**Status mix across the 1,053 problems:**

| Status | Count | Meaning |
|---|---:|---|
| 🔴 `open` | 450 | No known solution; decidability/complexity genuinely unresolved |
| 🟡 `partially-solved` | 369 | Solved for restricted cases or with caveats; general case open |
| 🟠 `empirically-open` | 227 | Works in practice, but lacks proven guarantees / matching bounds |
| 🟢 `solved-but-impractical` | 7 | Theoretically settled, but no deployable algorithm |

---

## Start here

- 🗺️ **[`TAXONOMY.md`](./TAXONOMY.md)** — the 35-topic map with scope descriptions.
- 📇 **[`INDEX.md`](./INDEX.md)** — flat, clickable list of all 1,053 problems grouped by topic.
- 📐 **[`TEMPLATE.md`](./TEMPLATE.md)** — the 10-section schema every problem page follows.

**Browsing tips**
- New to an area? Open the topic's `README.md` (e.g. [`topics/02-query-optimization/`](./topics/02-query-optimization/)) for a one-paragraph overview and a status-tagged index of its problems.
- Looking for a thesis topic? Filter for 🔴 `open` problems and read the **The Gap** section — it states exactly what would close the problem.
- Want the math fast? Each page's **§2 Mathematical Foundations** and **§10 Worked Example** are self-contained.

## Topics

| # | Topic | Problems |
|---|-------|---------:|
| 01 | [Relational Model & Dependency Theory](./topics/01-relational-theory/) | 30 |
| 02 | [Query Optimization](./topics/02-query-optimization/) | 31 |
| 03 | [Query Processing & Execution](./topics/03-query-processing/) | 30 |
| 04 | [Indexing & Access Methods](./topics/04-indexing-access-methods/) | 30 |
| 05 | [Concurrency Control](./topics/05-concurrency-control/) | 30 |
| 06 | [Recovery, Logging & Durability](./topics/06-recovery-logging/) | 30 |
| 07 | [Storage & Buffer Management](./topics/07-storage-buffer/) | 30 |
| 08 | [Distributed Query Processing](./topics/08-distributed-databases/) | 30 |
| 09 | [Replication & Consistency](./topics/09-replication-consistency/) | 30 |
| 10 | [Consensus & Coordination](./topics/10-consensus-coordination/) | 30 |
| 11 | [NoSQL & Key-Value Stores](./topics/11-nosql-kv/) | 31 |
| 12 | [NewSQL & Distributed SQL](./topics/12-newsql-distributed-sql/) | 30 |
| 13 | [Column Stores & OLAP](./topics/13-column-stores-olap/) | 30 |
| 14 | [Main-Memory Databases](./topics/14-main-memory-db/) | 30 |
| 15 | [Data Integration & Schema Mapping](./topics/15-data-integration/) | 30 |
| 16 | [Data Cleaning & Quality](./topics/16-data-cleaning-quality/) | 30 |
| 17 | [Approximate Query Processing](./topics/17-approximate-query-processing/) | 30 |
| 18 | [Streaming & Continuous Queries](./topics/18-streaming-queries/) | 30 |
| 19 | [Temporal Databases](./topics/19-temporal-databases/) | 31 |
| 20 | [Spatial & Spatiotemporal Databases](./topics/20-spatial-databases/) | 30 |
| 21 | [Graph Databases & Graph Query Processing](./topics/21-graph-databases/) | 30 |
| 22 | [Provenance & Lineage](./topics/22-provenance-lineage/) | 30 |
| 23 | [Database Security & Access Control](./topics/23-database-security/) | 30 |
| 24 | [Privacy & Encrypted Databases](./topics/24-privacy-encrypted-db/) | 30 |
| 25 | [Query Languages & Expressiveness](./topics/25-query-languages-expressiveness/) | 30 |
| 26 | [Cardinality Estimation & Statistics](./topics/26-cardinality-estimation/) | 30 |
| 27 | [Learned Database Components](./topics/27-learned-db-components/) | 30 |
| 28 | [Vector Databases & Similarity Search](./topics/28-vector-similarity-search/) | 30 |
| 29 | [Hardware-Conscious Databases](./topics/29-hardware-conscious-db/) | 30 |
| 30 | [Cloud & Serverless Databases](./topics/30-cloud-serverless-db/) | 30 |
| 31 | [Time-Series Databases](./topics/31-time-series-db/) | 30 |
| 32 | [Multi-Model & Document Databases](./topics/32-multimodel-document-db/) | 30 |
| 33 | [Benchmarking, Testing & Verification](./topics/33-benchmarking-testing/) | 30 |
| 34 | [Schema Design & Normalization](./topics/34-schema-design-normalization/) | 30 |
| 35 | [Self-Driving / Autonomous Databases](./topics/35-autonomous-db/) | 30 |

## How each problem page is structured

Every `.md` follows the same 10-section schema (see [`TEMPLATE.md`](./TEMPLATE.md)):

1. **Problem Statement** — precise, self-contained; distinguishes decision / optimization / counting variants.
2. **Mathematical Foundations** — the formal model, notation, and key theorems (LaTeX math).
3. **State of the Art** — best-known algorithms/systems, separating *theory-SOTA* from *systems-SOTA*.
4. **Upper Bound** — best algorithmic bound, naming the model (RAM, cell-probe, …).
5. **Lower Bound** — hardness / impossibility, naming the model (NP, fine-grained/SETH, info-theoretic, communication complexity, CAP/FLP, …).
6. **The Gap** — what separates the bounds; is it closed or genuinely open; what would close it.
7. **Current Research (June 2026)** — active directions and the groups pursuing them.
8. **Future Work** — open directions researchers articulate.
9. **Key References** — canonical + recent literature, linked.
10. **Worked Example** — a small concrete instance illustrating the problem and its bound.

## Repository layout

```
dbms_research/
├── README.md            ← you are here
├── TAXONOMY.md          ← 35-topic map
├── INDEX.md             ← flat list of all 1,053 problems  (generated by gen_index.sh)
├── TEMPLATE.md          ← per-problem schema
├── CLAUDE.md            ← maintenance conventions
├── gen_index.sh         ← regenerates INDEX.md from topics/
└── topics/
    └── NN-topic-slug/
        ├── README.md        ← topic overview + problem index
        └── problem-slug.md  ← one file per problem
```

Math renders on GitHub via MathJax. (Note: `#` inside math must be written `\\#` — GitHub strips one backslash before MathJax; see [github/markup#1662](https://github.com/github/markup/issues/1662).)

## ⚠️ Provenance & honesty note

This catalog was **synthesized primarily from established domain knowledge** (canonical PODS / SIGMOD / VLDB / ICDE / CIDR results and textbook theory), then passed through automated citation-verification that fetched and confirmed reference links.

- **Foundational results** (Codd, Selinger, Stonebraker, Gray, Abiteboul–Hull–Vianu, Atserias–Grohe–Marx, Ngo–Ré–Rudra, Dwork, Malkov–Yashunin, …) are reliable.
- **References are real and link-checked**, or explicitly flagged `*(unverified)*` (a handful) / `[DBLP search]` where no clean DOI exists. Where verification caught a citation error (wrong year/author/venue), a `> **Verification note:**` line records the correction.
- **2025–2026 frontier claims** are made to the best of current knowledge but may **lag the true frontier** (knowledge horizon ≈ January 2026); they are flagged inline with *(frontier — verify)*.
- **Complexity bounds** reflect results believed correct and name the model they hold in; folklore/contested bounds are marked.

**Do not cite this repository as a primary source.** Use it to orient yourself, then read — and cite — the linked references. Corrections are very welcome (see below).

## Contributing

Issues and PRs are welcome — especially:
- **Corrections** to bounds, attributions, or citation metadata (please link a source).
- **Frontier updates** removing a `*(frontier — verify)*` flag with a confirmed reference.
- **New problems** — copy [`TEMPLATE.md`](./TEMPLATE.md), fill all 10 sections, add it under the right `topics/NN-*/`, update that topic's `README.md`, and regenerate `INDEX.md` with `./gen_index.sh`. See [`CLAUDE.md`](./CLAUDE.md) for conventions (real references only, name the model for every bound, flag the frontier).

## License

Content released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — share and adapt with attribution.
