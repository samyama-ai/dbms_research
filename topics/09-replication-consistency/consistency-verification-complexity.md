---
id: 09-replication-consistency/consistency-verification-complexity
title: "Complexity of verifying consistency from histories"
topic: 09-replication-consistency
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Complexity of verifying consistency from histories

> **Topic:** Replication & Consistency · **ID:** `09-replication-consistency/consistency-verification-complexity` · **Status:** partially-solved

## 1. Problem Statement
Fix a consistency model $\mathcal{C} \in \{$ causal, PRAM, read-atomic, snapshot isolation (SI), serializability (SER), linearizability $\}$. Given a finite observed history $H$ (operations with arguments and return values, possibly with version metadata), decide whether $H$ admits an abstract execution witnessing $H \models \mathcal{C}$.

The goal is to *settle the exact computational complexity* of this decision problem, as a function of:
- the model $\mathcal{C}$,
- the **data type** (read/write registers vs. arbitrary RDTs),
- structural parameters: number of variables $k$, number of sessions/threads, presence of write-version information (data independence).

Companion variants: the **counting** variant (how many valid linearizations), and the **optimization** variant (minimum edits to make $H$ consistent — distance to $\mathcal{C}$).

## 2. Mathematical Foundations
Model each candidate witness as relations $(\mathsf{vis},\mathsf{ar})$ extending program order $\to_{po}$ and reads-from $\to_{rf}$. $H\models\mathcal{C}$ iff a *consistent extension* exists. SER/SI reduce to **acyclicity** of a dependency graph $G_H = \mathsf{WR}\cup\mathsf{WW}\cup\mathsf{RW}$ (Adya). When $\mathsf{WW}$ is determined (versioned writes), checking acyclicity is in $\mathsf{P}$; when $\mathsf{WW}$ must be *chosen*, the problem is an existential-cycle-avoidance choice, generically NP-hard.

Key parametric phenomenon (Biswas–Enea): for a fixed number of variables, many weak models become polynomial because the search over orderings factorizes per variable. Formally, the problems are fixed-parameter tractable in $k$ for causal/PRAM/read-atomic but **not** for SER/SI (W[1]-hard / NP-hard even for small $k$ in the unbounded case). Causal consistency splits into CC, CCv, CM variants with *different* complexities — a striking non-uniformity.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Bouajjani, Enea, Guerraoui, et al. (POPL 2017) classified causal consistency variants: CC and CCv are polynomial, CM is NP-complete. Biswas–Enea (OOPSLA 2019) gave a near-complete map for transactional models: SER, SI, prefix-consistency NP-complete in general but polynomial for a bounded number of sessions or with versioned writes. Gibbons–Korach (1997) anchor linearizability/sequential consistency hardness.
- **Systems-SOTA:** Elle and COBRA exploit the polynomial (versioned) regime; PolySI and Viper (VLDB 2023) give practical SMT-free SI/SER checkers leveraging these complexity results.

## 4. Upper Bound
With write-version information (data independence):
- Causal (CC, CCv): $O(n^k)$ / polynomial; PRAM and read-atomic: polynomial.
- SER / SI: polynomial via dependency-graph acyclicity (Adya), $\tilde{O}(n+m)$.
Without version info, but with bounded sessions $s$: SER is in $\mathsf{P}$ with exponent depending on $s$ (Biswas–Enea), i.e., $n^{O(s)}$ — XP in $s$. Linearizability with unique values and bounded concurrency $c$: $n^{O(c)}$.

## 5. Lower Bound
- **CM (causal memory)**, **SER**, **SI** without versions: **NP-complete** (Bouajjani et al. POPL 2017; Papadimitriou 1979; Biswas–Enea 2019). Model: classical NP, reductions from variants of SAT / cyclic-ordering.
- **Linearizability / sequential consistency**: NP-complete in general (Gibbons–Korach). Model: combinatorial decision.
- Parameterized: SER is **W[1]-hard** in the number of variables without version info, ruling out FPT under standard assumptions. No nontrivial fine-grained (SETH/3SUM) conditional lower bounds are yet established for the *polynomial* cases — leaving room for, e.g., a possible $n^{2-o(1)}$ barrier on acyclicity-based checks.

## 6. The Gap
The **coarse** map (P vs. NP-complete) is largely **closed** across the major models. The open frontier is *fine-grained*: for the polynomial cases (versioned SER/SI, CC), are the current $\tilde{O}(n+m)$ or $n^{O(s)}$ bounds optimal, or do SETH/APSP-conditional lower bounds forbid improvement? Also open: tight complexity of the **counting** and **minimum-repair (distance)** variants, where even membership in NP vs. #P-hardness is not fully settled for SI.

## 7. Current Research (as of June 2026)
Active groups: Enea & Bouajjani (IRIF), Constantin Enea (École Polytechnique) on parametric complexity and efficient checkers; Burckhardt (MSR) on the unifying axiomatic framework; the PolySI/Viper line (NUS, Lei et al.) pushing practical polynomial checkers. Recent threads: fine-grained conditional lower bounds for dependency-graph cycle detection *(frontier — verify)*; complexity of consistency checking for **CRDT/RDT-specific** semantics beyond registers *(frontier — verify)*; complexity of *quantitative* distance-to-serializability.

## 8. Future Work
- Establish SETH/3SUM-conditional lower bounds (or improved algorithms) for the polynomial regimes.
- Complete the complexity map for arbitrary replicated data types, not just registers.
- Settle #P-hardness vs. tractability for counting linearizations under each model.

## 9. Key References
- **[Foundational]** Bouajjani, Enea, Guerraoui, Hamza. *On Verifying Causal Consistency.* POPL, 2017. — [DOI](https://doi.org/10.1145/3009837.3009888)
- **[Foundational]** Papadimitriou. *The Serializability of Concurrent Database Updates.* JACM, 1979. — [DOI](https://doi.org/10.1145/322154.322158)
- **[Foundational]** Gibbons, Korach. *Testing Shared Memories.* SIAM J. Computing, 1997. — [DOI](https://doi.org/10.1137/S0097539794279614)
- **[SOTA]** Biswas, Enea. *On the Complexity of Checking Transactional Consistency.* OOPSLA, 2019. — [DOI](https://doi.org/10.1145/3360591)
- **[SOTA]** Adya. *Weak Consistency: A Generalized Theory and Optimistic Implementations for Distributed Transactions.* PhD thesis, MIT, 1999. — [MIT DSpace](https://dspace.mit.edu/handle/1721.1/149899)
- **[Survey]** Burckhardt. *Principles of Eventual Consistency.* Foundations and Trends in PL, 2014. — [DOI](https://doi.org/10.1561/2500000011)

## 10. Worked Example

Take a history on one register $x$ with two writer sessions and one reader, all *unversioned* (reads return values, not versions):

- $T_1$: `write(x,1)`
- $T_2$: `write(x,2)`
- $T_3$: `read(x)→1`, then `read(x)→2`

Is this serializable? The reads-from edges are fixed ($T_1\to_{rf}$ first read, $T_2\to_{rf}$ second read), but the **WW** order between $T_1$ and $T_2$ is *not* given — the checker must choose it. Here the reader saw $1$ then $2$, forcing $T_1 \xrightarrow{ww} T_2$; the dependency graph $G_H$ is then $T_1\to T_2\to T_3$, acyclic, so **serializable**.

Now add $T_3$: `read→2` then `read→1`. This forces *both* $T_1\to T_2$ (from one read pair) and $T_2\to T_1$ — a cycle — so **not serializable**.

The lesson the complexity map captures: when WW is *determined* (versioned writes), acyclicity is checkable in $\tilde{O}(n+m)$ (in $\mathsf{P}$); when WW must be *chosen* over $k$ variables and unbounded sessions, the existential search for an acyclic orientation is NP-complete (Papadimitriou; Biswas–Enea), dropping to $n^{O(s)}$ for $s$ fixed sessions.

---
*Part of the [DBMS Research catalog](../../README.md).*
