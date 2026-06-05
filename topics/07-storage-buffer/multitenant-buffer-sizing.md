# Buffer Pool Sizing Under Multi-Tenant Contention

> **Topic:** Storage & Buffer Management · **ID:** `07-storage-buffer/multitenant-buffer-sizing` · **Status:** partially-solved

## 1. Problem Statement

A shared buffer pool of $M$ frames serves $n$ tenants, each with its own access pattern and a hit-rate (or latency) function $U_i(m_i)$ giving utility from allocation $m_i$. Allocate $\sum_i m_i \le M$ to **maximize aggregate utility** $\sum_i U_i(m_i)$ subject to fairness (e.g., max-min, or per-tenant SLA floors). Allocations must adapt online as miss-ratio curves (MRCs) drift.

Variants:
- **Static optimization:** given MRCs $U_i$, maximize $\sum U_i(m_i)$ under the budget — a separable resource-allocation / knapsack-style program.
- **Fair variant:** maximize aggregate utility subject to max-min fairness or proportional fairness (Nash bargaining).
- **Online:** allocate without knowing future MRCs; bound regret vs. best fixed partition.
- **Strategyproof:** tenants may misreport demand; design a mechanism resistant to gaming.

## 2. Mathematical Foundations

**Separable concave maximization.** If each $U_i$ is **concave and non-decreasing** in $m_i$ (true for many MRCs — diminishing returns), maximizing $\sum_i U_i(m_i)$ over $\sum m_i \le M$ with integer $m_i$ is solved exactly by the **greedy marginal-allocation (Fox) algorithm**: repeatedly give the next frame to the tenant with the largest marginal gain $U_i(m_i+1)-U_i(m_i)$. This is optimal for concave separable objectives in $O(M\log n)$. Equivalently it is **maximizing a monotone submodular function under a cardinality/partition constraint** — but separability makes it exactly (not $1-1/e$) solvable.

**Non-convex MRCs.** Real miss-ratio curves have "cliffs" (working-set steps), so $U_i$ is **non-concave**; the problem becomes a multiple-choice knapsack — NP-hard, but with an FPTAS.

**Fairness.** Max-min and proportional (Nash) fairness give different optima; **Dominant Resource Fairness (DRF)** generalizes to multi-resource and is the canonical strategyproof, sharing-incentive mechanism.

MRCs are estimated cheaply via **reuse-distance histograms** (Mattson stack distance), computable in one pass with **SHARDS/MiniSim** sampling at $O(1)$ space.

## 3. State of the Art (SOTA)

**Systems-SOTA.** **SHARDS** (Waldspurger et al., FAST 2015) and **Counter Stacks** (Wires et al., OSDI 2014) make online MRC estimation cheap, enabling utility-driven sizing. **Memshare** (Cidon et al., ATC 2017) and **Cliffhanger** (Cidon et al., NSDI 2016) do online cross-tenant cache reallocation via marginal hit-rate gradients. Cloud DBs (Amazon Aurora, Azure SQL, Snowflake) partition buffer/cache per tenant with SLA floors. DRF (Ghodsi et al., NSDI 2011) underpins fair multi-resource sharing in YARN/Mesos.

**Theory-SOTA.** Greedy marginal allocation is exactly optimal for concave separable utilities (classical, Fox 1966); the cliff/non-concave case has an FPTAS via multiple-choice knapsack.

## 4. Upper Bound

- **Concave $U_i$:** **exact** optimum in $O(M\log n)$ (greedy marginal allocation / Galil–Megiddo); no approximation loss.
- **Non-concave (cliffy) MRCs:** **FPTAS** — $(1-\epsilon)$ in time poly$(n,1/\epsilon)$ via multiple-choice knapsack DP.
- **Online:** gradient-based reallocation (Cliffhanger) has strong empirical convergence; framed as online convex resource allocation, no-regret algorithms give $\tilde O(\sqrt{T})$ regret vs. the best fixed allocation when $U_i$ are concave (standard OCO).
- **Fair:** DRF is strategyproof, Pareto-efficient, and envy-free (proven, NSDI 2011).

## 5. Lower Bound

- The **non-concave** (multiple-choice knapsack) variant is **NP-hard** (weakly — pseudo-poly DP exists; the FPTAS is best possible unless P=NP for strong hardness).
- **Online:** $\Omega(\sqrt{T})$ regret is unavoidable for adversarial concave utilities (OCO lower bound).
- **Mechanism side:** no allocation can be simultaneously strategyproof, Pareto-efficient, and envy-free beyond what DRF achieves; tightening fairness vs. efficiency hits classical mechanism-design impossibilities.

## 6. The Gap

This is **partially solved**: the concave case is closed (exact, optimal, fast) and the cliffy case has a tight FPTAS. The remaining gaps are (i) **online sizing under drifting, non-concave MRCs with worst-case regret** — current results are empirical or assume concavity; (ii) **joint efficiency–fairness with SLA floors** lacks a clean optimal mechanism when utilities are non-concave; (iii) strategyproof sizing when tenants game MRC estimates. These are open but narrow — hence partially-solved rather than open.

## 7. Current Research (as of June 2026)

- **Learned/online MRC + reallocation** in serverless and disaggregated-memory settings (CXL pooled memory across tenants). *(frontier — verify)* on regret guarantees with cliffy MRCs.
- **Auction/market-based memory sharing** with budgets and incentive compatibility (cloud-DB economics). *(frontier — verify)*
- **RL controllers** for buffer sizing in autonomous DBs (CMU self-driving lineage, MSR). *(frontier — verify)*

## 8. Future Work

- No-regret online buffer sizing that provably handles non-concave MRCs and shifts.
- Optimal joint utility-maximization + max-min fairness with hard SLA floors.
- Strategyproof mechanisms robust to manipulated MRC reports.
- Cross-host buffer pooling over disaggregated/CXL memory with network-cost terms.

## 9. Key References

- **[Foundational]** Mattson, Gecsei, Slutz, Traiger. *Evaluation Techniques for Storage Hierarchies (stack distance).* IBM Systems Journal, 1970. — [DOI](https://doi.org/10.1147/sj.92.0078)
- **[SOTA]** Waldspurger, Park, Garthwaite, Ahmad. *Efficient MRC Construction with SHARDS.* FAST, 2015. — [USENIX](https://www.usenix.org/conference/fast15/technical-sessions/presentation/waldspurger)
- **[SOTA]** Cidon, Eisenman, Alizadeh, Katti. *Cliffhanger: Scaling Performance Cliffs in Web Memory Caches.* NSDI, 2016. — [USENIX](https://www.usenix.org/conference/nsdi16/technical-sessions/presentation/cidon)
- **[Foundational]** Ghodsi, Zaharia, Hindman, Konwinski, Shenker, Stoica. *Dominant Resource Fairness.* NSDI, 2011. — [USENIX](https://www.usenix.org/conference/nsdi11/dominant-resource-fairness-fair-allocation-multiple-resource-types)
- **[Foundational]** Fox. *Discrete Optimization via Marginal Analysis.* Management Science, 1966. — [DOI](https://doi.org/10.1287/mnsc.13.3.210)
- **[SOTA]** Wires, Ingram, Drudi, Harvey, Warfield. *Characterizing Storage Workloads with Counter Stacks.* OSDI, 2014. — [USENIX](https://www.usenix.org/conference/osdi14/technical-sessions/presentation/wires)

## 10. Worked Example

Budget $M=4$ frames, $n=2$ tenants with concave hit-rate utilities $U_i(m)$ (cumulative hits):

| frames $m$ | $U_1(m)$ | $U_2(m)$ |
|---|---|---|
| 0 | 0 | 0 |
| 1 | 50 | 30 |
| 2 | 70 | 55 |
| 3 | 80 | 72 |
| 4 | 85 | 85 |

Marginal gains: $U_1$: $50,20,10,5$; $U_2$: $30,25,17,13$. **Greedy marginal allocation (Fox 1966)** hands each frame to the largest remaining marginal:

1. give to $T_1$ (50) → $m=(1,0)$
2. give to $T_1$ (20) → $(2,0)$
3. give to $T_2$ (30) → $(2,1)$
4. give to $T_2$ (25) → $(2,2)$

Result $m^*=(2,2)$, total $U=70+55=125$. Check vs alternatives: $(3,1)=80+30=110$, $(1,3)=50+72=122$, $(4,0)=85$. The greedy $(2,2)$ is optimal — guaranteed because both $U_i$ are concave, so marginals are non-increasing and greedy never regrets an early choice.

---
*Part of the [DBMS Research catalog](../../README.md).*
