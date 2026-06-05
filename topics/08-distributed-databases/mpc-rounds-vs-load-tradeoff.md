# Multi-Round Tradeoffs in MPC Joins

> **Topic:** Distributed Query Processing · **ID:** `08-distributed-databases/mpc-rounds-vs-load-tradeoff` · **Status:** open

## 1. Problem Statement

In the Massively Parallel Computation (MPC) model, $p$ servers evaluate a query in synchronous rounds; in each round every server may send and receive at most $L$ tuples (its *load*), then compute locally for free. For a fixed full conjunctive (join) query $Q$ over relations $R_1,\dots,R_m$ with total input size $N$, two resources trade off against each other: the number of synchronous rounds $r$ and the per-server load $L$. The problem is to characterize, for every $Q$, the achievable region of $(r,L)$ pairs — its **Pareto frontier** — and to determine, given a round budget $r$, the minimum load $L^*(Q,r,p,N)$ (and the inverse: minimum $r$ at a given $L$).

- **Optimization variant:** minimize $L$ subject to a round bound $r$, or minimize $r$ given $L$.
- **Decision variant:** is a target $(r,L)$ achievable for $Q$ on inputs of size $N$ with $p$ servers?
- **Output-sensitive variant:** parameterize by the actual output size $\mathrm{OUT}$ rather than the worst-case AGM bound.

The frontier is well understood only at its endpoints ($r=1$; or "free" load $L=N/p$); the interior is genuinely open.

## 2. Mathematical Foundations

The MPC model (Beame–Koutris–Suciu) abstracts MapReduce/Spark: total space is $\le p\cdot L$, and $Q$ is *one-round computable* with load $L$ iff a hashing scheme places every matching combination of tuples on a common server. For a conjunctive query $Q$ with hypergraph $\mathcal H=(V,E)$ the relevant combinatorial quantities are:

- The **fractional edge cover number** $\rho^*(Q)=\min\sum_e u_e$ s.t. $\sum_{e\ni v}u_e\ge1$, giving the AGM bound $\mathrm{OUT}\le\prod_e N_e^{u_e}$.
- The **maximum fractional edge packing** $\psi^*(Q)=\max\sum_e u_e$ s.t. $\sum_{e\ni v}u_e\le1$, which governs one-round load:
$$ L_{1\text{-round}}(Q)\;=\;\tilde\Theta\!\left(\frac{N}{p^{1/\psi^*(Q)}}\right)\quad\text{(skew-free)}. $$

Multi-round lower bounds rely on a **degree/output routing argument**: any algorithm computing all $\mathrm{OUT}$ output tuples in $r$ rounds at load $L$ must satisfy an information-theoretic inequality linking $r$, $L$, and $\mathrm{OUT}$ (each output tuple's "witnesses" must co-locate, bounding how much can be produced per byte routed). The conjectured behavior for many queries is that load drops toward $\tilde\Theta(N/p^{1/\rho^*})$ once $r=O(\log p)$, but the per-round refinement of the curve is unresolved.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** Koutris–Beame–Suciu (ICDT 2016, *Worst-Case Optimal Algorithms for Parallel Query Processing*) give matching one-round bounds for many queries; Beame–Koutris–Suciu (PODS 2013 / JACM 2017) establish the model and first lower bounds. Hu–Yi (*Instance and Output Optimal Parallel Algorithms for Acyclic Joins*, PODS 2019) achieve output-optimal load; Hu (PODS 2021) gives tight multi-round load for several query families.
- **Systems-SOTA:** Spark (Photon), Snowflake, and Trino realize multi-round shuffles with hand-tuned (not provably optimal) round counts; Adaptive Query Execution chooses round structure heuristically from runtime statistics.

## 4. Upper Bound

For acyclic $Q$, the multi-round semijoin (Yannakakis / GYM) approach computes $Q$ in $O(\log p)$ rounds at load $\tilde O(N/p)$. The Hu–Yi instance-optimal algorithm achieves load $\tilde O\!\big(N/p^{1/\rho^*}+\mathrm{OUT}/p\big)$ in $O(1)$ rounds — holding in the **MPC model** (tuple-based, randomized hashing). For Berge-acyclic queries, $r=O(1)$ with $L=\tilde O(N/p)$ is achievable.

## 5. Lower Bound

Beame–Koutris–Suciu prove, in the **tuple-based MPC model**, that one round requires $L=\Omega(N/p^{1/\psi^*})$, and that some queries cannot be solved in $r$ rounds below a load threshold without violating an information-theoretic routing bound. Conditional lower bounds tie $\omega(1)$ rounds for connectivity-type queries to the **one-cycle-vs-two-cycles conjecture** (Roughgarden–Vassilvitskii–Wang) in MPC. No *unconditional* super-constant round lower bound for joins at load $N/p^{1-\epsilon}$ is known — this is the heart of the openness.

## 6. The Gap

For $r=1$ the bounds are tight (matching $\psi^*$). For $r\ge2$, upper bounds give $\tilde O(N/p)$ for many queries while the strongest lower bounds only forbid load below $N/p^{1/\psi^*}$ at $r=1$ — leaving the *shape* of the interior frontier (how load decays as rounds grow from $1$ to $\log p$) essentially open. Closing it requires either an MPC algorithm beating $\tilde O(N/p)$ for cyclic queries at small constant $r$, or a super-constant-round lower bound, likely via new connections to communication complexity or the MPC-vs-circuit barrier.

## 7. Current Research (as of June 2026)

Active threads: output-optimal multi-round joins (Hu, Yi, Tao, HKUST); MPC lower bounds via the one-cycle/two-cycles barrier (Roughgarden, Im, Moseley); and fine-grained round/load tradeoffs for specific motifs like cycles and Loomis–Whitney joins. Recent work connects MPC rounds to the *Adaptive MPC* (AMPC) model with a distributed hash-table oracle *(frontier — verify)*. Suciu's group continues on the load–round frontier for unions of conjunctive queries.

## 8. Future Work

- Prove or refute an $\omega(1)$-round lower bound at load $N/p^{1-\epsilon}$ for triangle/cycle joins.
- Extend instance/output-optimality to arbitrary $r$, parameterized by $\mathrm{OUT}$.
- Unify the AMPC hash-map oracle model with classic MPC frontiers.
- Bridge provable frontiers to adaptive query execution heuristics in real engines.

## 9. Key References

- **[Foundational]** P. Beame, P. Koutris, D. Suciu. *Communication Steps for Parallel Query Processing.* PODS 2013 (journal version JACM 2017).
- **[Foundational]** P. Koutris, P. Beame, D. Suciu. *Worst-Case Optimal Algorithms for Parallel Query Processing.* ICDT 2016.
- **[SOTA]** X. Hu, K. Yi. *Instance and Output Optimal Parallel Algorithms for Acyclic Joins.* PODS 2019.
- **[SOTA]** X. Hu. *Cover or Pack: New Upper and Lower Bounds for Massively Parallel Joins.* PODS 2021.
- **[Survey]** P. Koutris, S. Salihoglu, D. Suciu. *Algorithmic Aspects of Parallel Query Processing.* Foundations and Trends in Databases, 2018.

---
*Part of the [DBMS Research catalog](../../README.md).*
