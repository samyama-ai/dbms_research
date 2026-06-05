# Scalable Serializability Checking

> **Topic:** Benchmarking, Testing & Verification · **ID:** `33-benchmarking-testing/scalable-serializability-checking` · **Status:** partially-solved

## 1. Problem Statement

Given an *observed history* $H$ — a partial record of operations (reads, writes, commits) executed by a set of concurrent transactions $T_1,\dots,T_n$ against a database — decide whether $H$ is **serializable**: whether there exists a total order on committed transactions equivalent to $H$ that respects per-session program order and the observed read/write values.

Variants:
- **Decision (VSR / view-serializability):** is $H$ view-serializable? This is the canonical NP-complete formulation.
- **Conflict-serializability (CSR):** is the conflict graph acyclic? Polynomial *when the conflict relation is fully known*, but black-box testing only sees values, not internal read-from edges, so the witness ordering must be reconstructed.
- **Isolation-level checking:** decide membership in weaker classes — snapshot isolation (SI), read-committed, causal consistency — each with its own axioms.
- **Counting / repair:** how many distinct serial orders explain $H$; or the minimum number of operations to remove to restore serializability.

The practical instance: black-box differential testing of a DBMS or distributed store, where $H$ has $10^5$–$10^8$ operations and the checker must scale near-linearly to be useful in CI.

## 2. Mathematical Foundations

A history is a labeled partial order $H=(O,<_H)$ over operations. Two operations **conflict** if they touch the same item and at least one is a write. The **conflict graph** (serialization graph) $\mathrm{SG}(H)$ has a vertex per transaction and an edge $T_i \to T_j$ when an operation of $T_i$ precedes and conflicts with one of $T_j$.

> **Theorem (Conflict-serializability).** $H$ is conflict-serializable iff $\mathrm{SG}(H)$ is acyclic.

This is decidable in $O(|O| + n^2)$ once conflict edges are known. The hardness migrates into *which* read-from / version-order edges hold:

> **Theorem (Papadimitriou 1979).** Deciding view-serializability is NP-complete; the difficulty is choosing the version order on writes.

For SI, Cerone–Gotsman give an axiomatic characterization: $H \in \mathrm{SI}$ iff there is a commit order and a write-conflict-free read-from relation such that $\mathrm{SG}$ extended with anti-dependency edges has no cycle violating the "prefix" axiom. Adya's framework formalizes isolation as forbidden cycle patterns ($G0,G1,G2,\dots$) in the **dependency graph** (read-, write-, anti-dependencies $\mathrm{rw},\mathrm{ww},\mathrm{wr}$).

## 3. State of the Art (SOTA)

**Systems-SOTA.**
- **Cobra** (Tan et al., OSDI 2020) — SI/serializability checking via constraint encoding accelerated by domain-specific *pruning* (e.g., write-write order from versioned reads) and GPU-based BFS reachability, scaling to $\sim$10K txns/round.
- **Elle** (Kingsbury & Alvaro, VLDB 2020) — the checker inside **Jepsen**; uses *recoverable list/register* datatypes so the version order is observable from values, collapsing much of the NP-hardness in practice; widely deployed against production stores.
- **PolySI / Viper / IsoVista** (2023–2024) — encode SI checking as SMT/SAT with polygraph pruning; IsoVista adds visualization.

**Theory-SOTA.** Biswas & Enea (OOPSLA 2019) show that for a *bounded number of sessions* $k$, checking causal consistency and several isolation levels is polynomial (degree depending on $k$); the general (unbounded-session) problem stays NP-hard for most levels.

## 4. Upper Bound

- CSR with known conflicts: $O(|O|+n^2)$, RAM model.
- VSR / general serializability: NP, witnessed by a guessed version order checkable in P.
- **Fixed parameter:** $O(n^{c \cdot k})$ for $k$ sessions (Biswas–Enea), polynomial for constant $k$.
- **Practical:** near-linear *expected* time when datatypes make read-from observable (Elle), or with the polygraph-pruning + SMT pipeline (Cobra/PolySI) that empirically resolves most edges before search.

## 5. Lower Bound

- **NP-completeness** of VSR (Papadimitriou 1979) and of serializability/SI checking under unbounded sessions (Biswas–Enea 2019); SI checking is NP-complete even for a fixed isolation axiom set.
- Conditional fine-grained lower bounds: under the assumption that the read-from relation is *not* observable, recovering it subsumes set-disjointness-style search; no truly sub-quadratic black-box algorithm is known.
- These are worst-case; the structured instances arising from real workloads are typically far from the hard cores.

## 6. The Gap

The *theory* gap is closed in the classical sense — the problem is NP-complete and FPT in sessions. The *open* engineering gap is the distance between worst-case NP-hardness and the near-linear behavior seen on real histories. We lack a crisp structural parameter (beyond session count) that provably governs tractability and matches why Elle/Cobra succeed. Closing it means a parameterized or smoothed-analysis theorem predicting which observable histories are easy.

## 7. Current Research (as of June 2026)

- Extending Elle-style *recoverability* to richer datatypes and to SQL (range predicates, secondary indexes) so anti-dependencies become observable *(frontier — verify)*.
- Incremental / streaming checkers that validate histories online in CI rather than post-hoc.
- SMT-portfolio and GPU-reachability hybrids (Cobra successors, PolySI line).
- Formal connections between Adya cycle classes and parameterized complexity (Enea, Gotsman, Alvaro/Kingsbury groups).

## 8. Future Work

- A parameterized complexity map: pinpoint a width/treewidth-like measure of $\mathrm{SG}$ that yields provable near-linear checking.
- Sound *sampling*-based checkers with statistical guarantees for histories too large for exact methods.
- Unified oracle covering serializability + SI + causal + session guarantees with shared pruning.
- Certificate generation: machine-checkable proofs of (non-)serializability for trust.

## 9. Key References

- **[Foundational]** C. H. Papadimitriou. *The Serializability of Concurrent Database Updates.* JACM, 1979. — [DOI](https://doi.org/10.1145/322154.322158)
- **[Foundational]** A. Adya, B. Liskov, P. O'Neil. *Generalized Isolation Level Definitions.* ICDE, 2000. — [DBLP](https://dblp.org/rec/conf/icde/AdyaLO00.html)
- **[SOTA]** K. Kingsbury, P. Alvaro. *Elle: Inferring Isolation Anomalies from Experimental Observations.* VLDB, 2020. — [DOI](https://doi.org/10.14778/3430915.3430918)
- **[SOTA]** C. Tan, C. Zhao, S. Mu, M. Walfish. *Cobra: Making Transactional Key-Value Stores Verifiably Serializable.* OSDI, 2020. — [USENIX](https://www.usenix.org/conference/osdi20/presentation/tan)
- **[SOTA]** R. Biswas, C. Enea. *On the Complexity of Checking Transactional Consistency.* OOPSLA, 2019. — [DOI](https://doi.org/10.1145/3360591)
- **[Foundational]** A. Cerone, A. Gotsman. *Analysing Snapshot Isolation.* JACM, 2018 (PODC 2016). — [DOI](https://doi.org/10.1145/3152396)

## 10. Worked Example

Observe a history over items $x, y$ with three transactions; reads show which write they observed:

- $T_1$: `w1[x=1]`
- $T_2$: `r2[x=1] w2[y=1]`
- $T_3$: `r3[y=1] w3[x=2]`

Build the conflict (serialization) graph $\mathrm{SG}(H)$, one vertex per transaction:
- $T_2$ reads $x{=}1$ from $T_1$ ⇒ $\mathsf{wr}$ edge $T_1 \to T_2$.
- $T_3$ reads $y{=}1$ from $T_2$ ⇒ $\mathsf{wr}$ edge $T_2 \to T_3$.
- $T_3$ writes $x{=}2$; $T_1$ also writes $x$, and $T_2$ read $T_1$'s version, so $T_3$'s write must order *after* $T_2$'s read ⇒ anti-dependency $\mathsf{rw}$ edge $T_2 \to T_3$ (already present) and version order $T_1 \to T_3$ on $x$.

The graph $T_1 \to T_2 \to T_3$ (plus $T_1 \to T_3$) is **acyclic**, so by the conflict-serializability theorem $H$ is serializable, witnessed by the topological order $T_1, T_2, T_3$. Cost: with read-from observed, edges are read off directly and acyclicity is $O(|O| + n^2) = O(5 + 9)$ here (5 listed operations, $n^2 = 9$) — the *easy* regime Elle exploits. Had $T_3$ instead read $x{=}1$ (stale), we'd get $T_3 \to T_1$, closing a cycle $T_1 \to \dots \to T_3 \to T_1$, and the checker would report non-serializability with that cycle as the witness.

---
*Part of the [DBMS Research catalog](../../README.md).*
