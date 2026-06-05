# Consistency model checking at runtime

> **Topic:** Replication & Consistency · **ID:** `09-replication-consistency/runtime-consistency-checking` · **Status:** partially-solved

## 1. Problem Statement
Given a stream of operation events (reads, writes, transaction commits with their arguments and return values) observed from a running replicated/distributed store, decide *online* — incrementally, with bounded memory and per-event latency — whether the observed history is consistent with a declared target model $\mathcal{C}$ (e.g., linearizability, sequential consistency, causal consistency, read-atomic, snapshot isolation, serializability).

Variants:
- **Online monitoring (decision):** maintain a verdict "no violation so far" and emit a witness as soon as a violation is detectable.
- **Sliding-window / bounded-staleness:** check $\mathcal{C}$ restricted to a window, trading completeness for $O(w)$ state.
- **Quantitative:** measure *how far* a history is from $\mathcal{C}$ (e.g., $k$-atomicity, $\Delta$-staleness) rather than a boolean.

The core tension: the offline decision problem is often NP-hard (or worse), yet runtime checking demands near-constant per-event cost.

## 2. Mathematical Foundations
A history is a partial order $H=(E,\to_{po},\to_{rf})$ of events with program order $\to_{po}$ and a reads-from relation $\to_{rf}$. A model $\mathcal{C}$ is a set of axioms over an *abstract execution* — a tuple $(E, \mathsf{vis}, \mathsf{ar})$ with a visibility relation $\mathsf{vis}$ and arbitration order $\mathsf{ar}$ (Burckhardt's framework). $H \models \mathcal{C}$ iff there exist $\mathsf{vis},\mathsf{ar}$ extending $H$ satisfying $\mathcal{C}$'s axioms. Linearizability requires a total order $\mathsf{ar}$ respecting real-time precedence; serializability a total order over transactions consistent with $\to_{rf}$.

Checking reduces to acyclicity of a derived relation: SI/serializability checking corresponds to detecting a cycle in a *dependency graph* $\mathsf{WR}\cup\mathsf{WW}\cup\mathsf{RW}$ (Adya's framework). The hardness lever is *inferring* the unknown $\mathsf{WW}$ order: with versioned writes it is fixed (polynomial); without, it is a combinatorial choice (NP-hard).

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Gibbons–Korach showed linearizability checking is NP-complete in general but polynomial under bounded concurrency/uniqueness. Biswas–Enea (OOPSLA 2019) gave polynomial algorithms for serializability/SI/causal under data-independence assumptions.
- **Systems-SOTA:** **Jepsen/Knossos** and **Elle** (Kingsbury–Alvaro, VLDB 2020) infer SI/serializability violations from real systems via dependency-graph cycle detection using versioned registers; **Anna/COBRA** (Tan et al., OSDI 2020) verifies serializability at scale using SMT + hardware acceleration. Online monitors: **MonkeyDB** and runtime-verification engines for causal/read-atomic.

## 4. Upper Bound
Linearizability of a register history with unique values: $O(n\log n)$ per the Wing–Gong/Lowe automaton when concurrency is bounded. Elle's serializability check via cycle detection on the recovered dependency graph runs in near-linear time $\tilde{O}(n+m)$ in the graph size when writes are version-traceable (RAM model). Causal/PRAM consistency with version info is checkable in polynomial time (Biswas–Enea). Online sliding-window monitors run in $O(\log w)$ amortized per event under a window of $w$ live operations.

## 5. Lower Bound
- **Linearizability** checking is **NP-complete** in general (Gibbons–Korach, 1997) — model: combinatorial decision, reduction from a SAT-like ordering problem; remains hard even for a single register without value uniqueness.
- **Serializability** of a history is NP-complete (Papadimitriou 1979) when the write order is not given.
- Online lower bounds are *space* lower bounds: any monitor detecting all linearizability violations needs $\Omega(n)$ memory in the worst case (communication-complexity argument) — full online detection cannot be done in sublinear state without giving up completeness.

## 6. The Gap
The decision-complexity gap is essentially **resolved per-model** (poly with version info / NP-hard without). The genuinely open part is the *runtime* gap: bridging the offline NP-hardness with hard real-time per-event budgets. We lack tight characterizations of the **space–completeness Pareto frontier** for online monitors, and tight bounds for *quantitative* distance-to-consistency under streaming constraints.

## 7. Current Research (as of June 2026)
Active lines: Enea, Bouajjani (IRIF/Paris) on polynomial-time consistency checking and parametric data-independence; Kingsbury/Alvaro (Jepsen, UC Santa Cruz) extending Elle to weaker isolation and online operation; Wattenhofer/ETH and the runtime-verification (RV) community on streaming monitors with formal completeness guarantees. Emerging work couples consistency monitoring with **eBPF/in-network telemetry** for low-overhead capture *(frontier — verify)*, and LLM-assisted witness minimization for violation reports *(frontier — verify)*.

## 8. Future Work
- A unified online-monitoring framework parameterized by model axioms with provable per-event and space bounds.
- Sound-and-complete sublinear monitors for restricted (data-independent, bounded-staleness) workloads.
- Quantitative runtime metrics (continuous "consistency SLO" gauges) with statistical guarantees.

## 9. Key References
- **[Foundational]** Gibbons, Korach. *Testing Shared Memories.* SIAM J. Computing, 1997. — [DOI](https://doi.org/10.1137/S0097539794279614)
- **[Foundational]** Papadimitriou. *The Serializability of Concurrent Database Updates.* JACM, 1979. — [DOI](https://doi.org/10.1145/322154.322158)
- **[Foundational]** Burckhardt. *Principles of Eventual Consistency.* Foundations and Trends in PL, 2014. — [DOI](https://doi.org/10.1561/2500000011)
- **[SOTA]** Kingsbury, Alvaro. *Elle: Inferring Isolation Anomalies from Experimental Observations.* VLDB, 2020. — [DOI](https://doi.org/10.14778/3430915.3430918)
- **[SOTA]** Biswas, Enea. *On the Complexity of Checking Transactional Consistency.* OOPSLA, 2019. — [DOI](https://doi.org/10.1145/3360591)
- **[SOTA]** Tan, Zhao, et al. *COBRA: Making Transactional Key-Value Stores Verifiably Serializable.* OSDI, 2020. — [USENIX](https://www.usenix.org/conference/osdi20/presentation/tan)

## 10. Worked Example

Stream of three transactions on keys $x,y$ (versioned writes, so $\mathsf{WW}$ order is known):

| Txn | ops | reads-from |
|----|----|----|
| $T_1$ | $W(x{=}1)$ | — |
| $T_2$ | $R(x{=}1),\,W(y{=}1)$ | $x$ from $T_1$ |
| $T_3$ | $R(y{=}0),\,W(x{=}2)$ | $y$ initial (v0), $x{:}\,1\!\to\!2$ |

Build the dependency graph (Adya $\mathsf{WR}\cup\mathsf{WW}\cup\mathsf{RW}$):
- $T_1 \xrightarrow{\mathsf{WR}} T_2$ ($T_2$ reads $T_1$'s $x$).
- $T_1 \xrightarrow{\mathsf{WW}} T_3$ ($T_3$ overwrites $x{=}1$ with $x{=}2$).
- $T_3 \xrightarrow{\mathsf{RW}} T_2$ ($T_3$ read $y$'s *initial* version, but $T_2$ later wrote $y{=}1$ — a read overwritten by $T_2$).
- $T_2 \xrightarrow{\mathsf{RW}} T_3$ ($T_2$ read $x{=}1$, which $T_3$ overwrites to $x{=}2$).

Edges $T_2 \to T_3$ and $T_3 \to T_2$ form a **2-cycle** $\Rightarrow$ no serial order exists $\Rightarrow$ the history is **not serializable**. The online monitor emits $\{T_2,T_3\}$ as the witness the instant both RW edges materialize — exactly Elle's cycle-detection strategy, running in $\tilde{O}(n+m)$ because versions are traceable.

---
*Part of the [DBMS Research catalog](../../README.md).*
