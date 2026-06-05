# Order Dependencies and Their Implication

> **Topic:** Relational Model & Dependency Theory · **ID:** `01-relational-theory/order-dependencies-implication` · **Status:** partially-solved

## 1. Problem Statement

An **order dependency (OD)** captures monotonicity between ordered lists of attributes: $X \mapsto Y$ (or $X \preceq Y$) means that sorting tuples by $X$ also sorts them by $Y$ — e.g. *salary determines tax bracket* in an order-preserving way. ODs strictly generalize FDs (an FD is an OD where $Y$ is constant within $X$-groups). The problems:

- **Axiomatization:** Find a sound and complete inference system for OD implication.
- **Decision (implication):** Given ODs $\Sigma$ and an OD $\sigma$, decide $\Sigma \models \sigma$.
- **Discovery:** Mine valid (and approximate) ODs from data.
- **Optimization use:** Exploit ODs to eliminate sorts, push down predicates, and remove order-by/group-by operations in query optimization.

Status is **partially solved**: list-based ODs were shown to admit a sound and complete axiomatization and **coNP-complete** implication; set-based formulations and bidirectional/approximate variants are still being mapped, and optimizer integration is ongoing.

## 2. Mathematical Foundations

Let $X = [A_1,\dots,A_k]$ be an attribute **list**. Define a lexicographic order $\preceq_X$ on tuples. A **list-based OD** $X \mapsto Y$ holds in relation $r$ iff
$$\forall s,t \in r:\ s \preceq_X t \ \Rightarrow\ s \preceq_Y t.$$
Equivalently, ordering by $X$ yields an ordering compatible with $Y$.

- **Order compatibility** $X \sim Y$: there is a single order consistent with both — the symmetric core.
- ODs subsume FDs: $X \mapsto XY$ encodes $X \to Y$.
- **Set-based ODs / sequential dependencies** (Golab et al.) relax to "within $X$-ordered runs, $Y$ stays within a bounded gap," connecting to data-quality on streams.

Two main formalizations: **list-based ODs** (Szlichta–Godfrey–Gryz) with a complete axiomatization, and **set-based canonical ODs**. Bidirectional and pointwise ODs add descending order and per-pair monotonicity. The reasoning machinery uses an OD-specific chase / closure over polarity-annotated attribute lists.

## 3. State of the Art (SOTA)

**Theory-SOTA:**
- **List-based OD axiomatization + complexity:** Szlichta, Godfrey, Gryz established a sound and complete set of inference rules and proved **OD implication is coNP-complete** (TODS / VLDBJ, 2012–2017).
- Mapping between **set-based** and **list-based** ODs and a polynomial-mappable canonical form (Szlichta et al., 2017–2018).
- **Sequential dependencies** for ordered/streaming data (Golab, Karloff, Korn, Saha, Srivastava, VLDB 2009).

**Systems-SOTA:**
- **OD discovery:** **ORDER** and **FASTOD** (Szlichta et al., SIGMOD 2017) discover all valid ODs; **DISTOD** parallelizes set-based OD discovery; approximate-OD discovery exists for dirty data.
- **Optimizer use:** ODs generalize the "interesting orders" of System R; modern engines exploit functional/order dependencies to avoid sorts (DB2 with the original OD work, and research integrations).

## 4. Upper Bound

- **List-based OD implication:** in **coNP** (and complete for it) — a counterexample relation has polynomial size, so the complement is in NP.
- **Order-compatibility checking** and FD-subsumed fragments: **polynomial** time.
- **OD discovery (FASTOD):** worst-case exponential in attributes but with strong lattice-pruning; polynomial in the number of tuples.
- Mapping set-based ↔ list-based ODs: polynomial.

Model: finite relations under list/lexicographic order semantics.

## 5. Lower Bound

- **List-based OD implication:** **coNP-complete** (Szlichta–Godfrey–Gryz) — coNP-hardness by reduction encoding monotone constraint satisfaction into order chains.
- This places OD reasoning strictly harder than FD implication (PTIME) but no harder than necessary for the expressiveness gained.
- **Approximate OD** validation (minimum tuples to delete to satisfy an OD) is NP-hard in general, mirroring approximate-FD $g_3$ hardness.
- Discovery faces an **exponential output-size** lower bound (number of minimal ODs can be exponential in attributes).

## 6. The Gap

For the central case — **list-based OD implication** — the gap is essentially **closed**: a complete axiomatization plus matching coNP-completeness. Remaining open pieces are at the edges: (a) tight complexity and clean axiomatizations for **approximate / pointwise / bidirectional** ODs; (b) implication when ODs are **combined with FDs, INDs, or cardinality constraints**; (c) the *optimization* gap — how much real query speedup ODs unlock, which is empirical rather than complexity-theoretic. Closing these needs unified inference across mixed dependency classes and broader optimizer adoption.

## 7. Current Research (as of June 2026)

- **Scalable and approximate OD discovery** on dirty/real data, including bidirectional ODs and incremental discovery (Szlichta and collaborators; the Naumann/HPI discovery community) *(frontier — verify)*.
- **Optimizer integration**: using discovered ODs to remove sorts and group-bys, and to tighten cardinality estimates, with renewed interest in cloud query engines *(frontier — verify)*.
- ODs over **temporal / streaming** data via sequential dependencies for data quality.
- Combining ODs with **denial constraints** for unified data-cleaning frameworks.

## 8. Future Work

- Complete axiomatizations and tight complexity for **approximate** and **bidirectional** ODs.
- Unified reasoning for **OD + FD + IND + cardinality**.
- Robust, benchmarked **optimizer exploitation** of ODs (sort elimination, predicate pushdown) with measured gains.
- OD discovery that scales to wide tables and is robust to noise.

## 9. Key References

- **[Foundational]** Ginsburg, S., Hull, R. *Order Dependency in the Relational Model.* Theoretical Computer Science, 1983.
- **[SOTA]** Szlichta, J., Godfrey, P., Gryz, J. *Fundamentals of Order Dependencies.* PVLDB, 2012.
- **[SOTA]** Szlichta, J., Godfrey, P., Gryz, J. et al. *Effective and Complete Discovery of Order Dependencies via Set-based Axiomatization (FASTOD).* PVLDB, 2017.
- **[Foundational]** Golab, L., Karloff, H., Korn, F., Saha, A., Srivastava, D. *Sequential Dependencies.* PVLDB, 2009.
- **[Survey]** Szlichta, J., Godfrey, P., Gryz, J., Zuzarte, C. *Expressiveness and Complexity of Order Dependencies.* PVLDB, 2013.

---
*Part of the [DBMS Research catalog](../../README.md).*
