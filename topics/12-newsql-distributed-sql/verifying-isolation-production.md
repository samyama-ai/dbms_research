---
id: 12-newsql-distributed-sql/verifying-isolation-production
title: "Verifying distributed isolation in production"
topic: 12-newsql-distributed-sql
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Verifying distributed isolation in production

> **Topic:** NewSQL & Distributed SQL · **ID:** `12-newsql-distributed-sql/verifying-isolation-production` · **Status:** empirically-open

## 1. Problem Statement
Given only black-box access to a deployed distributed SQL system (you can submit transactions and observe results, but not inspect internals), decide at runtime whether the observed history actually satisfies the **claimed isolation level** (serializability, snapshot isolation, read committed, etc.), and if not, exhibit a violating witness.

- **Decision variant.** Given an observed history $H$ (sets of transactions with their reads/writes and partial real-time ordering), decide whether $H$ is admissible under isolation level $L$.
- **Counting/auditing variant.** Estimate the *rate* of anomalies over a continuous production stream under sampling.
- **Online/streaming variant.** Detect violations incrementally with bounded memory and latency, suitable for always-on auditing.

This matters because vendors *claim* strong isolation, but bugs, misconfiguration, and clock failures (see "Clock synchronization failure semantics") can silently deliver weaker guarantees; black-box checking is the only recourse without source access.

## 2. Mathematical Foundations
A history $H$ is a set of transactions with read/write events plus a partial **real-time order** (session/wall-clock constraints). Isolation levels are characterized by the **dependency serialization graph (DSG)** with edges for write-dependencies (ww), read-dependencies (wr), and anti-dependencies (rw) (Adya's formalism). Then:
- **Serializability** $\iff$ the DSG is acyclic (after committing the version order).
- **Snapshot isolation** $\iff$ no cycle with two consecutive rw edges among concurrent transactions, plus SI's read-snapshot rule.

The checking problem must *infer the version order* — which writes a read observed and the commit order — from observations. Determining whether a *valid* version order exists making the DSG acyclic is the crux. Papadimitriou (1979) showed deciding serializability of a general history (view-serializability) is **NP-complete**; the practical relief is that *conflict-serializability* is polynomial when the version/order is known. With unknown order, the search reintroduces hardness.

Black-box checkers thus build a constraint problem: a set of transactions, candidate dependency edges, and an existential choice of orientations; "is $H$ isolation-$L$?" becomes a cycle-detection over a graph with *unknown* edge orientations — solvable by SAT/SMT or by polynomial algorithms under structural assumptions (e.g., Elle's recoverability and key-uniqueness exploits).

## 3. State of the Art (SOTA)
- **Systems-SOTA.** **Elle** (Kingsbury & Alvaro, VLDB 2020) infers Adya-style dependency cycles from black-box histories using list-append and register workloads, scaling to real production logs; it underpins Jepsen. **Cobra** (Tan, Jung, et al., OSDI 2020) verifies serializability of black-box histories using SMT plus GPU-accelerated pruning and domain-specific acceleration, handling large histories. **PolySI** (VLDB 2023) extends to snapshot isolation efficiently; **Viper** and **IsoVista** target SI/other levels with better scalability *(frontier — verify)*.
- **Theory-SOTA.** Biswas & Enea (OOPSLA 2019) give complexity results: checking serializability is NP-complete in general but **polynomial** when the number of sessions/keys is bounded, and provide tractable algorithms for several isolation levels under bounded parameters.

## 4. Upper Bound
With bounded sessions/variables, checking serializability and SI is **polynomial** (Biswas–Enea). In the general case, Cobra/PolySI give *practically* efficient SMT-based decision procedures with aggressive polynomial pruning (transitive-closure pre-solving) that make worst-case-exponential SAT tractable on real histories. Elle achieves near-linear inference on workloads engineered for *recoverability* (unique values let it read off the version order directly), giving an effectively polynomial checker for its workload class.

## 5. Lower Bound
Checking general (view-)serializability is **NP-complete** (Papadimitriou, JACM 1979); checking SI and many weak levels for arbitrary histories with unknown version order is likewise NP-hard (Biswas & Enea, OOPSLA 2019). Sampling-based auditing inherits an information-theoretic limit: a low-rate anomaly may be missed unless enough of the history is observed, giving a coverage/confidence tradeoff. Black-box observation also cannot distinguish certain internal states, so some violations are fundamentally unobservable without richer interfaces.

## 6. The Gap
Theory pins the worst case (NP-complete) and the tractable islands (bounded parameters). The *empirically open* part is: (i) always-on, streaming, bounded-memory checking over unbounded production traffic without the engineered-workload crutches Elle relies on; (ii) sound checking for the *full* zoo of vendor-claimed levels (causal, parallel SI, read-atomic) with scalable algorithms; and (iii) statistically rigorous anomaly-rate estimation under sampling. No tool yet offers continuous, general-workload, provably-sound auditing at production scale.

## 7. Current Research (as of June 2026)
Active: scaling SMT-based checkers (PolySI, Viper, IsoVista) to more isolation levels and larger histories *(frontier — verify)*; streaming/incremental verification with sliding windows; integrating checkers into CI and live observability (continuous Jepsen). Groups: Kingsbury (Jepsen) & Alvaro (UC Santa Cruz), Enea (IRIF/Paris), the Cobra authors (UT Austin/MIT lineage), and database-vendor reliability teams. *(frontier — verify)* 2025 work claims real-time SI auditing on live clusters but soundness-vs-throughput tradeoffs are unresolved.

## 8. Future Work
- Sound, streaming, bounded-memory checkers for arbitrary production workloads.
- A unified checker covering the full isolation/consistency lattice with one engine.
- Statistically principled anomaly-rate estimation and SLA-style "isolation auditing."

## 9. Key References
- **[Foundational]** Papadimitriou. *The Serializability of Concurrent Database Updates.* JACM, 1979. — [DOI](https://doi.org/10.1145/322154.322158)
- **[Foundational]** Adya, Liskov, O'Neil. *Generalized Isolation Level Definitions.* ICDE, 2000. — [DOI](https://doi.org/10.1109/ICDE.2000.839388)
- **[SOTA]** Kingsbury, Alvaro. *Elle: Inferring Isolation Anomalies from Experimental Observations.* VLDB, 2020. — [DOI](https://doi.org/10.14778/3430915.3430918)
- **[SOTA]** Tan, Zhao, Jung, et al. *Cobra: Making Transactional Key-Value Stores Verifiably Serializable.* OSDI, 2020. — [USENIX](https://www.usenix.org/conference/osdi20/presentation/tan)
- **[SOTA]** Huang, Liu, Zhang, et al. *PolySI: Efficient Black-Box Checking of Snapshot Isolation.* VLDB, 2023. — [DOI](https://doi.org/10.14778/3583140.3583145)
- **[Survey]** Biswas, Enea. *On the Complexity of Checking Transactional Consistency.* OOPSLA, 2019. — [DOI](https://doi.org/10.1145/3360591)

## 10. Worked Example

A black-box checker observes three transactions on keys $x,y$ (initial $x_0,y_0$):
- $T_1$: write $x{=}1$ (creates $x_1$).
- $T_2$: write $y{=}1$ (creates $y_1$); read $x \Rightarrow$ saw $x_1$.
- $T_3$: read $x \Rightarrow x_1$; read $y \Rightarrow y_0$.

Build the DSG. From $T_2$'s read of $x_1$: a **wr** edge $T_1 \to T_2$. From $T_3$ reading $y_0$ (the version *before* $T_2$'s write $y_1$): an **anti-dependency** $T_3 \to T_2$ (rw). From $T_3$ reading $x_1$: **wr** edge $T_1 \to T_3$.

Edges: $T_1\to T_2,\; T_1\to T_3,\; T_3\to T_2$. No cycle $\Rightarrow$ the history **is serializable**, with the unique order $T_1, T_3, T_2$.

Now suppose instead $T_3$ had also been read by $T_2$ as $y_1$ *and* $T_3$ read $y_0$: that forces both $T_2\to T_3$ and $T_3\to T_2$, a 2-cycle $\Rightarrow$ **non-serializable**, and the cycle is the witness Elle/Cobra would report. The hard part the checker solved here: *inferring* the version order from reads — NP-complete in general (Papadimitriou), tractable because values are unique.

---
*Part of the [DBMS Research catalog](../../README.md).*
