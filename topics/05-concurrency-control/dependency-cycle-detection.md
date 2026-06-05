# Conflict-Graph Cycle Detection at Scale

> **Topic:** Concurrency Control · **ID:** `05-concurrency-control/dependency-cycle-detection` · **Status:** empirically-open

## 1. Problem Statement
Serializable Snapshot Isolation (SSI) and certification-based protocols detect non-serializable executions by finding **dangerous cycles** in a dynamically changing conflict (serialization) graph. Exact online cycle detection over the full dependency graph is expensive; production SSI uses a *sufficient* (not necessary) heuristic — abort whenever a transaction has both an incoming and an outgoing rw-antidependency (the "two consecutive rw-edges" pivot), causing false aborts. The problem:

> **Detect dangerous dependency-graph cycles online, with bounded per-transaction overhead and bounded false-positive rate, at high core counts / large in-flight transaction sets.**

Variants:
- **Decision variant:** On each new conflict edge, decide whether a (dangerous) cycle now exists.
- **Optimization variant:** Minimize false aborts subject to $O(1)$ or $O(\text{polylog})$ amortized overhead per edge insertion.
- **Streaming variant:** Maintain cycle-freedom certificates under an online stream of edge insertions/commits (transactions leave the graph on commit/abort).

## 2. Mathematical Foundations
The conflict graph $G=(V,E)$ has active/recently-committed transactions as vertices and dependency edges $ww, wr, rw$. Serializability $\equiv$ acyclicity of $G$ (over the relevant edge set). **Online cycle detection** is the *incremental topological order / incremental SCC* problem: maintain a topological order under edge insertions, detecting the first inserting edge that creates a cycle.

Best incremental algorithms (Bender–Fineman–Gilbert–Tarjan) maintain topological order under $m$ edge insertions in $O(m^{3/2})$ total (dense) or $O(m \cdot \min(m^{1/2}, n^{2/3}))$ time — i.e. *amortized* $\tilde{O}(\sqrt m)$ per edge, far from $O(1)$. SSI sidesteps full detection using Fekete's theorem: every SI cycle contains a vertex $T_2$ with $T_1 \xrightarrow{rw} T_2 \xrightarrow{rw} T_3$ both edges "pivot" edges; flag-and-abort on this *local* pattern needs only per-transaction in/out flags ($O(1)$ state) but is conservative.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Incremental cycle detection / topological ordering: Bender, Fineman, Gilbert, Tarjan (TALG 2016) and Bernstein–Chechik dynamic-graph results give the asymptotic frontier for general online cycle detection.
- **Systems-SOTA:** PostgreSQL SSI (Ports–Grittner, VLDB 2012) uses the $O(1)$-flag pivot heuristic with SIREAD locks. **PSSI / precise SSI** (Revilak, O'Neil, O'Neil, ICDE 2011) builds the actual MVSG and tests real cycles, reducing false aborts at higher tracking cost. In-memory: TicToc (Yu et al., SIGMOD 2016) and Cicada (Lim et al., SIGMOD 2017) use timestamp-range certification instead of explicit graph cycle search; Sundial (Yu et al., VLDB 2018) does logical-leasing to avoid materializing the graph.

## 4. Upper Bound
Two regimes: (1) **Heuristic SSI** — $O(1)$ state per transaction, $O(\text{degree})$ work to set pivot flags, *sound but not precise* (over-aborts). (2) **Precise cycle detection** — incremental SCC at amortized $\tilde{O}(\sqrt m)$ per edge (Bender et al.) in the RAM model, exact but with overhead that grows with graph size and is hard to bound per transaction. Timestamp-certification approaches (TicToc/Sundial) achieve effectively $O(\text{read+write set})$ validation per transaction without maintaining a global graph — the systems upper bound at scale.

## 5. Lower Bound
For fully dynamic graphs, maintaining reachability/cycle information has conditional lower bounds: under the **Online Matrix-Vector (OMv) conjecture**, no algorithm maintains single-source reachability (hence incremental cycle detection in the fully dynamic setting) with both $O(n^{1-\epsilon})$ update and query time — implying you cannot get truly cheap *exact* dynamic cycle detection in the worst case. This is the relevant fine-grained barrier; it is why production systems accept conservative $O(1)$ heuristics rather than exact detection.

## 6. The Gap
Empirically open: heuristic SSI is cheap but over-aborts (false positives grow with contention and long transactions); precise detection is exact but its overhead grows with in-flight graph size and OMv-conditional barriers suggest it cannot be made worst-case cheap. The gap is the *false-abort vs. overhead* tradeoff at high core counts and large transaction footprints. Closing it needs either a sharper sufficient-and-near-necessary local condition with provably bounded false positives, or scalable approximate cycle detection with tunable error.

## 7. Current Research (as of June 2026)
Active: scalable certification (TicToc/Sundial lineage) and decentralized validation that avoids a global graph; bounded-staleness conflict graphs; GPU/SIMD batch cycle search (cf. Cobra's offline approach pushed toward online). *(frontier — verify)* 2025–2026 work on approximate/sketched dynamic cycle detection for serializable in-memory and disaggregated-storage engines, and on reducing SSI false aborts via finer-grained antidependency tracking, appears to be an active frontier at SIGMOD/VLDB/OSDI.

## 8. Future Work
- A precise-but-cheap pivot condition closing the false-abort gap.
- Approximate dynamic cycle detection with provable error/overhead bounds.
- Hardware-accelerated online serialization-graph maintenance at 1000+ cores.

## 9. Key References
- **[Foundational]** Fekete, Liarokapis, O'Neil, O'Neil, Shasha. *Making Snapshot Isolation Serializable.* TODS, 2005. — [DOI](https://doi.org/10.1145/1071610.1071615)
- **[SOTA]** Ports, Grittner. *Serializable Snapshot Isolation in PostgreSQL.* VLDB, 2012. — [arXiv](https://arxiv.org/abs/1208.4179)
- **[SOTA]** Revilak, O'Neil, O'Neil. *Precisely Serializable Snapshot Isolation (PSSI).* ICDE, 2011. — [DBLP](https://dblp.org/search?q=Precisely%20Serializable%20Snapshot%20Isolation)
- **[SOTA]** Bender, Fineman, Gilbert, Tarjan. *A New Approach to Incremental Cycle Detection and Related Problems.* ACM TALG, 2016. — [arXiv](https://arxiv.org/abs/1105.2397)
- **[SOTA]** Yu, Pavlo, Sanchez, Devadas. *TicToc: Time Traveling Optimistic Concurrency Control.* SIGMOD, 2016. — [DOI](https://doi.org/10.1145/2882903.2882935)
- **[Foundational]** Henzinger, Krinninger, Nanongkai, Saranurak. *Unifying and Strengthening Hardness for Dynamic Problems via the Online Matrix-Vector Conjecture.* STOC, 2015. — [arXiv](https://arxiv.org/abs/1511.06773)

## 10. Worked Example

The classic SI write-skew anomaly. Two on-call doctors $x_1, x_2$ are "on duty"; the rule is at least one must stay on duty. Two concurrent transactions each read both rows and set their own doctor off duty:

- $T_1$: reads $x_1, x_2$ (both on), writes $x_1 \leftarrow$ off.
- $T_2$: reads $x_1, x_2$ (both on), writes $x_2 \leftarrow$ off.

Under SI both commit (disjoint write sets, no ww-conflict), but the result violates the invariant — a non-serializable execution. The conflict graph has two **rw-antidependencies**: $T_1$'s read of $x_2$ precedes $T_2$'s write of $x_2$, giving $T_1 \xrightarrow{rw} T_2$; symmetrically $T_2 \xrightarrow{rw} T_1$. That is a cycle.

**Fekete's pivot.** Every SI cycle has a vertex with two consecutive incoming+outgoing rw-edges. Here both $T_1$ and $T_2$ qualify. PostgreSQL SSI keeps one bit each for "has inEdge" and "has outEdge" ($O(1)$ state); when both fire on one transaction it aborts — sound, but it would also abort some safe schedules (false positives), the cost of avoiding full $\tilde{O}(\sqrt m)$ cycle search.

---
*Part of the [DBMS Research catalog](../../README.md).*
