# Multi-Tenant Shared-Resource Tuning

> **Topic:** Self-Driving / Autonomous Databases · **ID:** `35-autonomous-db/multi-tenant-tuning` · **Status:** open

## 1. Problem Statement
In a shared (cloud, multi-tenant) deployment, many tenants run on **shared physical resources** — buffer pool, CPU, I/O bandwidth, log, shared storage, even shared indexes/caches. An autonomous tuner acting for one tenant can **externalize cost** onto others: aggressively caching pages evicts a neighbor's working set; building a large index consumes I/O that starves co-tenants; a knob change that helps one workload degrades the noisy-neighbor's tail latency.

Sub-problems:
- **Global optimization vs. per-tenant agents:** a per-tenant greedy tuner reaches a *Nash-like* configuration that can be globally inefficient; a global tuner is optimal but must respect per-tenant SLOs and fairness.
- **Fair, incentive-compatible allocation (optimization):** allocate shared resources / approve tuning actions to maximize total utility subject to fairness and SLO constraints, internalizing externalities.
- **Pricing / mechanism (decision):** charge actions their true marginal social cost so selfish agents behave well.
- **Isolation guarantee:** bound the performance degradation any one tenant can impose on another.

## 2. Mathematical Foundations
- **Game theory:** model tenants as players; per-tenant tuning is a **congestion / resource-allocation game**. The inefficiency of selfish equilibria is the **Price of Anarchy** $\mathrm{PoA} = \frac{\max_{\text{NE}} \mathrm{cost}}{\mathrm{OPT}}$ (Koutsoupias–Papadimitriou; Roughgarden's smoothness framework bounds it). Externalities make the social cost differ from the sum of private costs.
- **Mechanism design:** a **VCG** mechanism charging each agent its externality is incentive-compatible and efficient; budget-balance and computational tractability are the obstructions. Pricing shared resources at marginal congestion cost (Pigouvian) restores efficiency.
- **Fair division:** fairness via **max-min / proportional fairness** or **Dominant Resource Fairness (DRF)** for multi-resource sharing (Ghodsi et al.), which is sharing-incentive, strategy-proof, Pareto-efficient, and envy-free.
- **Constrained optimization / control:** global tuning is $\max \sum_i U_i(c_i)$ s.t. $\sum_i r_i(c_i) \le R$ and $\mathrm{SLO}_i$ — a knapsack/packing problem (NP-hard) with online/stochastic demand; submodular utilities admit greedy $(1-1/e)$ approximations.
- **Isolation:** performance isolation as a *capacity-provisioning* guarantee; admission control + reservations bound the externality each tenant can inflict.

## 3. State of the Art (SOTA)
**Systems-SOTA:** Multi-tenant resource governance is mature operationally — Azure SQL Database / elastic pools, AWS Aurora Serverless, Snowflake virtual warehouses isolate via reservations, governors, and (in Snowflake) compute/storage separation. **DRF** underpins cluster schedulers (Mesos, YARN). Tenant placement/consolidation and *performance-isolation* research (e.g., SQLVM, Pythia-style noisy-neighbor detection, work from Microsoft on multi-tenant DBaaS) targets SLOs. But **autonomous tuning that jointly optimizes across tenants while internalizing externalities** is largely unrealized — production tuners act per-database. *(frontier — verify)*

**Theory-SOTA:** PoA bounds for congestion games, VCG efficiency, and DRF fairness are established but **not specialized** to the DB-tuning action space (indexes/knobs/layout) with its switching costs and SLO constraints.

## 4. Upper Bound
- **Efficiency:** VCG yields a socially-efficient, truthful allocation of tuning actions when externalities are computable; for submodular global utility under a packing constraint, **greedy gives $(1-1/e)$** of optimum.
- **Fairness:** DRF gives a polynomial-time allocation that is strategy-proof, envy-free, Pareto-efficient, and sharing-incentive for multi-resource sharing.
- **PoA bound:** in $(\lambda,\mu)$-smooth resource games, selfish per-tenant tuning is within $\frac{\lambda}{1-\mu}$ of optimal (e.g., PoA $\le 2$ for many load-balancing/congestion instances), bounding the loss from decentralization. These hold in the game-theoretic / approximation-algorithm models.

## 5. Lower Bound
- **PoA $>1$:** selfish per-tenant tuning is provably suboptimal — congestion games have PoA bounded away from 1 (e.g., $4/3$ for nonatomic affine, up to $5/2$ atomic), so decentralization has an unavoidable efficiency loss.
- **VCG infeasibility:** no mechanism is simultaneously efficient, strategy-proof, and budget-balanced (Myerson–Satterthwaite); pricing externalities exactly forces a budget deficit or inefficiency.
- **NP-hardness:** global resource-constrained configuration selection is NP-hard (knapsack/packing); with index interactions it inherits the hardness of index selection.
- **Isolation impossibility:** with fully shared resources and work-conserving scheduling, perfect isolation contradicts high utilization — a fundamental tension (you cannot give both full isolation and full statistical multiplexing).

## 6. The Gap
**Open.** Game-theoretic and fair-division theory bound efficiency and fairness *abstractly*, and systems isolate resources *heuristically*, but no framework unifies them for **autonomous tuning**: an action-level mechanism that (a) internalizes cross-tenant externalities of index/knob/layout changes, (b) respects per-tenant SLOs and switching costs, and (c) achieves provable PoA / fairness with tractable computation. Closing it needs a DB-tuning-specific congestion-game model with matching PoA bounds and an implementable, near-budget-balanced pricing/scheduling mechanism.

## 7. Current Research (as of June 2026)
- Cross-tenant / fleet-level autonomous tuning and consolidation in cloud DBaaS, internalizing noisy-neighbor cost. *(frontier — verify)*
- Learned admission control and resource governors coupled to tuning agents. *(frontier — verify)*
- Mechanism-design / fair-RL approaches to shared-resource scheduling migrating into DB tuning. Groups: Microsoft (multi-tenant DBaaS), CMU (Pavlo), Berkeley (RISELab lineage, DRF authors), cloud-vendor research. *(frontier — verify)*

## 8. Future Work
- A congestion-game model of multi-tenant tuning with provable PoA and fairness guarantees.
- Tractable, near-budget-balanced pricing of tuning actions by marginal social cost.
- SLO-aware global tuner with bounded per-tenant blast radius (ties to adversarial-robustness).
- Online/stochastic variants handling tenant churn and demand drift.

## 9. Key References
- **[Foundational]** E. Koutsoupias, C. Papadimitriou. *Worst-Case Equilibria.* STACS, 1999.
- **[Foundational]** T. Roughgarden. *Intrinsic Robustness of the Price of Anarchy.* JACM, 2015 (STOC, 2009).
- **[Foundational]** A. Ghodsi, M. Zaharia, B. Hindman, A. Konwinski, S. Shenker, I. Stoica. *Dominant Resource Fairness: Fair Allocation of Multiple Resource Types.* NSDI, 2011.
- **[Foundational]** R. Myerson, M. Satterthwaite. *Efficient Mechanisms for Bilateral Trading.* J. Economic Theory, 1983.
- **[SOTA]** V. Narasayya et al. *SQLVM: Performance Isolation in Multi-Tenant Relational Database-as-a-Service.* CIDR, 2013.
- **[Survey]** A. Pavlo et al. *Self-Driving Database Management Systems.* CIDR, 2017.

---
*Part of the [DBMS Research catalog](../../README.md).*
