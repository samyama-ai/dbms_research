---
id: 33-benchmarking-testing/isolation-level-conformance
title: "Checking Isolation-Level Conformance Empirically"
topic: 33-benchmarking-testing
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Checking Isolation-Level Conformance Empirically

> **Topic:** Benchmarking, Testing & Verification · **ID:** `33-benchmarking-testing/isolation-level-conformance` · **Status:** partially-solved

## 1. Problem Statement
Treat a DBMS as a **black box**. From a collection of observed client **histories** $H$ — recorded transactions with their read/write operations and observed values, partially ordered by real-time (session/start-commit) constraints — decide which **isolation level** $I$ (serializability, snapshot isolation, repeatable read, read-committed, …) or which **anomalies** ($G0, G1a/b/c, G2$, lost update, write skew, …) the system actually exhibits.

Variants:
- **Decision (single level):** is $H$ admissible under isolation level $I$? (e.g., is $H$ serializable? SI-valid?)
- **Anomaly detection:** does $H$ witness a specific anomaly $\phi$ (a refutation that the system provides $I$)?
- **Inference/characterization:** infer the *strongest* level consistent with all observed histories — an empirical lower-bounding of the system's guarantees.

The black-box constraint is essential: no access to the version chain, lock manager, or commit timestamps — only what clients can observe. This is the *testing/auditing* counterpart to formal CC verification.

## 2. Mathematical Foundations
A history is interpreted via a **dependency graph (DSG/serialization graph)** over committed transactions with **ww** (version order), **wr** (read-from), and **rw** (anti-dependency) edges (Adya–Liskov–O'Neil, ICDE 2000). Isolation levels are characterized by *prohibited cycles*: serializability forbids all cycles; SI forbids cycles without ≥2 consecutive rw-edges (Cahill–Röhm–Fekete); read-committed forbids $G1$, etc.

The core difficulty is **version-order recovery**: clients observe read-from (wr) edges directly, but the *write order* (ww) — needed to complete the graph — is hidden, so checking requires searching over consistent version orders. Serializability checking of a history is **NP-complete** (Papadimitriou, JACM 1979) because of this search. Modern checkers exploit **per-key version recovery**: when each write installs a unique value, the read-from relation pins much of the order, collapsing the search and yielding **polynomial** anomaly detection in practice (the **Elle** insight). The framework rests on graph cycle-detection and on encoding the remaining choices as a SAT/constraint problem.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** **Elle** (Alvaro–Kingsbury, VLDB 2020), the checker behind **Jepsen**, recovers dependency edges from list-append/register histories and detects anomalies up to serializability with *witnesses* (human-readable cycles); it has found isolation violations in many commercial databases.
- **Cobra** (Tan, Zhao, Mu, Walfish, OSDI 2020) verifies **serializability** of black-box key-value histories at scale using a SMT/SAT encoding accelerated with domain-specific pruning and GPU.
- **PolySI / Viper / IsoVista** (recent SIGMOD/VLDB 2023–2024) check **snapshot isolation** and other levels with SMT/graph methods and provide counterexample visualization. **dbcop** (Biswas–Enea, OOPSLA 2019) checks several isolation levels with complexity results for bounded parameters.
- **Theory-SOTA:** Biswas–Enea (OOPSLA 2019) give **polynomial-time** algorithms for checking many isolation levels when the number of sessions/values is bounded, plus NP-hardness without those bounds.
- Mature, deployed, witness-producing checkers exist — hence **partially-solved**; complete + scalable checking across *all* levels on *unrestricted* histories remains open.

## 4. Upper Bound
With **unique-value writes** (traceable version recovery), Elle detects $G0/G1/G2$ anomalies and serializability violations in time near-linear/polynomial in history size via cycle detection on the recovered DSG. Biswas–Enea prove **polynomial-time** checking for read-committed, read-atomic, causal, prefix, snapshot isolation, and serializability *when sessions and/or value-multiplicity are bounded*. Cobra/PolySI decide serializability/SI on real workloads by SAT/SMT with pruning, scaling to millions of operations despite worst-case NP-hardness.

## 5. Lower Bound
Without traceability, the problems are **NP-complete**: deciding serializability of a history is NP-complete (Papadimitriou, JACM 1979); Biswas–Enea show checking SI and several other levels is **NP-complete** in the unrestricted (unbounded sessions, repeated values) setting. The hardness stems precisely from recovering the hidden **ww** version order. These are unconditional NP-hardness results in the history-checking model — the polynomial algorithms only escape them via the bounded-parameter or unique-value assumptions.

## 6. The Gap
The gap is between **polynomial, witness-producing checking under benign assumptions** (unique values / bounded sessions — largely closed, and the basis of Elle/Cobra/PolySI) and **general, unrestricted black-box histories**, where checking is NP-complete and current SMT tools rely on workload-specific pruning that can blow up adversarially. Also open: *completeness* across the full isolation lattice (most tools target serializability or SI, not every intermediate level uniformly) and inferring the *exact* strongest guarantee rather than checking one level. Closing it needs either tighter parameterized algorithms or principled, provably-bounded SAT encodings.

## 7. Current Research (as of June 2026)
Directions: (1) unified checkers spanning the whole isolation lattice with counterexample visualization (IsoVista-style) *(frontier — verify)*; (2) SMT encodings with provable scalability and incremental/online checking of live traffic *(frontier — verify)*; (3) characterizing distributed/causal+ and transactional-causal-consistency conformance for geo-replicated stores; (4) combining empirical checking with formal CC verification so observed violations become regression specs. Groups: Kingsbury & Alvaro (Jepsen/Elle), Enea/Bouajjani (parameterized isolation checking), the Cobra/PolySI authors (MIT/Aarhus/National Univ. of Singapore lineage), and active Jepsen audits of commercial NewSQL systems.

## 8. Future Work
- Provably scalable checkers for unrestricted histories (beyond pruning heuristics).
- Uniform, complete coverage of every level in the isolation hierarchy with minimal-witness extraction.
- Online/streaming conformance monitoring integrated into production observability.
- Inference of the *exact* strongest guarantee a system provides, with statistical confidence bounds.

## 9. Key References
- **[Foundational]** Papadimitriou. *The Serializability of Concurrent Database Updates.* JACM, 1979. — [DOI](https://doi.org/10.1145/322154.322158)
- **[Foundational]** Adya, Liskov, O'Neil. *Generalized Isolation Level Definitions.* ICDE, 2000. — [DOI](https://doi.org/10.1109/ICDE.2000.839388) — [DBLP](https://dblp.org/rec/conf/icde/AdyaLO00)
- **[SOTA]** Alvaro, Kingsbury. *Elle: Inferring Isolation Anomalies from Experimental Observations.* PVLDB, 2020. — [arXiv](https://arxiv.org/abs/2003.10554) — [DOI](https://doi.org/10.14778/3430915.3430918)
- **[SOTA]** Tan, Zhao, Mu, Walfish. *Cobra: Making Transactional Key-Value Stores Verifiably Serializable.* OSDI, 2020. — [USENIX](https://www.usenix.org/conference/osdi20/presentation/tan) — [DBLP](https://dblp.org/rec/conf/osdi/TanZMW20)
- **[SOTA]** Biswas, Enea. *On the Complexity of Checking Transactional Consistency.* OOPSLA, 2019. — [arXiv](https://arxiv.org/abs/1908.04509) — [DOI](https://doi.org/10.1145/3360591)
- **[SOTA]** Huang, Liu, et al. *Efficient Black-Box Checking of Snapshot Isolation in Databases (PolySI).* PVLDB, 2023. — [arXiv](https://arxiv.org/abs/2301.07313) — [DOI](https://doi.org/10.14778/3583140.3583145)

## 10. Worked Example

Two transactions over keys $x,y$ (both initially 0), each write installs a *unique* value (Elle's trick):

- $T_1$: $w(x{=}1)$, then $r(y) \to 0$.
- $T_2$: $w(y{=}1)$, then $r(x) \to 0$.

Recover dependency edges. $T_1$ read $y{=}0$, but $T_2$ wrote $y{=}1$, so $T_1$ did *not* read $T_2$'s write — $T_1$ must be ordered before $T_2$ on $y$: edge $T_1 \xrightarrow{\text{rw}} T_2$ (anti-dependency). Symmetrically $T_2$ read $x{=}0$ while $T_1$ wrote $x{=}1$: edge $T_2 \xrightarrow{\text{rw}} T_1$.

The DSG has a **cycle** $T_1 \to T_2 \to T_1$ formed by two rw anti-dependency edges. Serializability forbids *all* cycles, so this history is **not serializable** — it is the classic **write-skew** anomaly. But snapshot isolation only forbids cycles with $<2$ consecutive rw edges; this cycle has exactly two, so SI *permits* it. Thus the history is a witness that the system is at most SI, not serializable. Because each value is unique, version order needs no search — cycle detection is near-linear, sidestepping the worst-case NP-completeness of recovering hidden ww order.

---
*Part of the [DBMS Research catalog](../../README.md).*
