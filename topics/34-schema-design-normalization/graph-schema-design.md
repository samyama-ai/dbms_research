---
id: 34-schema-design-normalization/graph-schema-design
title: "Schema Design for Graph and Property-Graph Stores"
topic: 34-schema-design-normalization
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Schema Design for Graph and Property-Graph Stores

> **Topic:** Schema Design & Normalization · **ID:** `34-schema-design-normalization/graph-schema-design` · **Status:** empirically-open
> **Verification note:** Per Fan–Wu–Xu (SIGMOD 2016), GFD *satisfiability* is coNP-complete while GFD *implication* is NP-complete; the text below sometimes states both as coNP-complete, which conflates the two.

## 1. Problem Statement
Property-graph stores (Neo4j, TigerGraph, Amazon Neptune) and RDF triple stores expose a different design surface than the relational model: the same domain fact can be modeled as a **node property**, as a separate **node connected by an edge**, or as an **edge property** (or, in RDF, as a literal, a resource, or a reified statement). These factoring choices — *which attributes become properties vs. promoted to nodes vs. attached to edges* — determine traversal performance, storage, index applicability, and update anomalies, yet there is no normalization theory (BCNF/4NF analog) to guide them.

The problem: **decide node/edge/property factoring and the normalization/denormalization tradeoffs for property-graph and RDF schemas.** Variants:
- **Decision:** Is a given graph schema "normalized" (free of a defined redundancy/anomaly) w.r.t. graph dependencies?
- **Optimization:** Given a workload (traversal/pattern-match queries) and constraints, choose a factoring minimizing cost subject to a storage/anomaly budget.
- **Empirical question (the dominant one today):** Which factorings actually perform best, and can we predict it?

It is **empirically-open**: practice is governed by best-practice patterns and benchmarks, not by a theory with guarantees.

## 2. Mathematical Foundations
A property graph is $G=(V,E,\lambda,\sigma)$: vertices $V$, directed labeled edges $E\subseteq V\times \mathcal{L}\times V$, label map $\lambda$, and property map $\sigma$ assigning key→value maps to vertices and edges. RDF is the special triple case $G\subseteq \mathcal{R}\times\mathcal{R}\times(\mathcal{R}\cup \mathcal{L})$. Dependency theory generalizes via **graph functional dependencies (GFDs)** and **graph entity dependencies (GEDs)** (Fan, Lu; Fan, Wu, Xu), which pair a graph *pattern* $Q$ with an FD-like literal constraint enforced on each match $h(Q)$:
$$G \models (Q,\ X\to Y) \iff \forall \text{ matches } h(Q):\ h \models X \Rightarrow h \models Y.$$
Validation/implication/satisfiability of GFDs/GEDs are the formal handles for "redundancy" and "anomaly" in graphs; **subgraph isomorphism** (NP-hard) underlies pattern matching, and **graph keys** define identity. A normal-form theory would define when promoting/merging a property removes a GED-certified redundancy while preserving information (lossless w.r.t. the graph), but no agreed redundancy measure yet exists for graphs.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** **GFDs** (Fan, Wu, Xu, PODS/SIGMOD 2016) and **GEDs** (Fan, Lu, *Dependencies for Graphs*, TODS 2019) give the dependency language and settle implication/validation complexity; **graph keys** (Fan, Fan, Tian, Zhao, VLDB 2015) handle entity identity. **GQL/SQL-PGQ** (ISO 2024) standardize property-graph querying, and emerging **PG-Schema / PG-Keys** proposals (Angles, Bonifati, Hartig, et al., 2021–2023) define schema and key languages — but neither prescribes *normalization*.
- **Systems-SOTA / empirical:** Design is driven by vendor modeling guides and benchmarks (**LDBC SNB / Graphalytics**). Studies compare property-on-node vs. node-promotion factorings on traversal cost; RDF storage layout (triple table vs. property tables vs. emergent-schema) has a large empirical literature (e.g., Pham, Boncz on *emergent schemas* for RDF). No tool auto-normalizes a property-graph schema with guarantees.

## 4. Upper Bound
There is no algorithm with proven optimality for workload-aware graph factoring; current methods are **heuristic / cost-model-driven search** over factorings, validated empirically. For the dependency layer: GFD **satisfiability and validation** are decidable but expensive — validation involves subgraph pattern matching, and **GFD/GED implication is coNP-complete to (for some fragments) higher** in the relevant catalog of Fan–Lu (model: classical complexity). Emergent-schema discovery for RDF runs in near-linear passes over triples with clustering heuristics (Pham–Boncz), giving practical but unguaranteed property-table layouts (model: RAM, heuristic).

## 5. Lower Bound
- Core operations are **NP-hard**: subgraph isomorphism / graph pattern matching underlying GFD validation is NP-complete (model: classical NP).
- **GFD/GED satisfiability and implication** are **coNP-complete** for central fragments (Fan, Wu, Xu 2016; Fan, Lu 2019; model: classical complexity), so reasoning that any normalization theory needs is already intractable.
- Choosing an optimal factoring/partitioning of a graph for a workload generalizes **balanced graph partitioning**, which is NP-hard and hard to approximate (model: NP / hardness-of-approximation). No information-theoretic redundancy lower bound for graph schemas is yet established — itself a gap.

## 6. The Gap
The gap is foundational, not just quantitative: **there is no normalization theory for property graphs** — no agreed redundancy/anomaly measure, no "graph BCNF," and no lossless-decomposition analog certifying that a node/edge/property refactoring removes redundancy without losing information. Empirically, factoring choices demonstrably swing performance, but predictions rest on benchmarks rather than guarantees. The dependency layer (GFD/GED) supplies the language to *state* redundancy, yet its coNP-hardness, plus NP-hard pattern matching, means even checking a proposed normal form is expensive. Closing requires (1) an information-theoretic redundancy definition for graphs and (2) workload-aware factoring with cost-model and anomaly guarantees.

## 7. Current Research (as of June 2026)
Active: **Edinburgh (Fan)** on graph dependencies, keys, and cleaning; the **GQL/SQL-PGQ standardization** effort and the **PG-Schema/PG-Keys** group (Angles, Bonifati, Hartig, Vrgoč, Voigt) defining schema languages that could host normalization; **CWI (Boncz)** lineage on RDF emergent schemas and graph storage. Emerging 2025–2026 threads: workload-aware and **learned** graph-schema/storage design, GED-driven graph cleaning, and translating relational normal-form intuition into PG-Schema constraints *(frontier — verify)*. A principled graph normalization theory has not yet consolidated.

## 8. Future Work
- An information-theoretic redundancy measure and "normal forms" for property graphs and RDF.
- Workload-aware, anomaly-bounded factoring (node/edge/property) with cost-model guarantees and benchmarks.
- Tractable design-oriented fragments of GFD/GED reasoning, or approximation algorithms.
- Tooling that ingests PG-Schema + workload and recommends/verifies a normalized factoring.

## 9. Key References
- **[Foundational]** W. Fan, Y. Wu, J. Xu. *Functional Dependencies for Graphs.* SIGMOD, 2016. — [ACM](https://dl.acm.org/doi/10.1145/2882903.2915232)
- **[Foundational]** W. Fan, P. Lu. *Dependencies for Graphs.* ACM TODS, 2019. — [ACM](https://dl.acm.org/doi/10.1145/3287285)
- **[Foundational]** W. Fan, Z. Fan, C. Tian, X. L. Zhao. *Keys for Graphs.* PVLDB, 2015. — [PVLDB](http://www.vldb.org/pvldb/vol8/p1590-fan.pdf) · [DBLP](https://dblp.org/rec/journals/pvldb/FanFTD15.html)
- **[SOTA]** R. Angles, A. Bonifati, S. Dumbrava, G. Fletcher, et al. *PG-Schema: Schemas for Property Graphs.* SIGMOD, 2023. — [DOI](https://doi.org/10.1145/3589778) · [arXiv](https://arxiv.org/abs/2211.10962)
- **[SOTA]** M.-D. Pham, P. Boncz, et al. *Deriving an Emergent Relational Schema from RDF Data.* WWW / VLDB Journal, 2015–2018. — [DOI](https://doi.org/10.1145/2736277.2741121) · [DBLP](https://dblp.org/rec/conf/www/PhamPEB15.html)
- **[Survey]** R. Angles, M. Arenas, P. Barceló, A. Hogan, J. Reutter, D. Vrgoč. *Foundations of Modern Query Languages for Graph Databases.* ACM Computing Surveys, 2017. — [DOI](https://doi.org/10.1145/3104031) · [arXiv](https://arxiv.org/abs/1610.06264)
- **[Foundational]** A. Deutsch, N. Francis, A. Green, et al. *Graph Pattern Matching in GQL and SQL/PGQ.* SIGMOD, 2022. — [DOI](https://doi.org/10.1145/3514221.3526057) · [arXiv](https://arxiv.org/abs/2112.06217)

## 10. Worked Example
Consider modeling "a Person lives in a City, which is in a Country." Two factorings:

**Factoring A (property-on-node):** each Person node carries properties $city$ and $country$ as strings. For 1,000 people living across 50 cities in 5 countries, the string `"France"` is stored redundantly on every person in a French city. A query "all people in France" must scan all 1,000 Person nodes filtering on $country$.

**Factoring B (promote to nodes):** City and Country become nodes, linked by edges $\text{(Person)}\!-\![\text{LIVES\_IN}]\!\rightarrow\!\text{(City)}\!-\![\text{IN}]\!\rightarrow\!\text{(Country)}$. Now $country$ is stored once per country (5 nodes), and "all people in France" is a 2-hop traversal from the France node, touching only matching edges.

The redundancy in A is exactly what a GFD can *state*: with pattern $Q$ matching a Person–City pair and the constraint $city \to country$, $G \models (Q, city \to country)$ asserts that city functionally determines country — so storing $country$ per-person is redundant whenever $city$ is present. Factoring B removes that redundancy losslessly (the country is recoverable by traversal). But validating the GFD requires matching $Q$ across the graph — subgraph isomorphism, NP-hard in general — so even *checking* that B is "more normalized" than A is expensive, illustrating the foundational gap: the language to state graph redundancy exists, yet no tractable normal-form test or lossless-decomposition guarantee does.

---
*Part of the [DBMS Research catalog](../../README.md).*
