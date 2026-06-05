# SLA-Constrained Self-Tuning

> **Topic:** Self-Driving / Autonomous Databases · **ID:** `35-autonomous-db/sla-constrained-tuning` · **Status:** open

## 1. Problem Statement
A shared / multi-tenant autonomous database must optimize a **global objective** (aggregate throughput, total cost, energy) while honoring **per-tenant SLAs as hard constraints** — e.g., tenant $i$'s p99 latency must stay below $\ell_i$, availability above $a_i$. The controller continually changes configurations (resource allocation, knobs, indexes, placement), and any change that pushes *any* tenant above its SLA is a violation, possibly with penalty/refund. The problem: **maximize the global objective subject to all per-tenant SLA constraints holding, simultaneously and continually, under uncertainty and drift.**

Formally, choose configuration/allocation $\theta_t$ to
$$\max_{\theta_t}\ \sum_t g(\theta_t)\quad \text{s.t.}\quad \forall i,t:\ \Pr\big[\,\mathrm{SLA}_i(\theta_t)\text{ met}\,\big]\ge 1-\delta_i.$$
Variants. **(i) Decision/feasibility:** does a configuration satisfying all SLAs exist (admission control)? **(ii) Constrained optimization:** optimize $g$ over the feasible set. **(iii) Online/regret:** unknown reward & constraint functions learned on the fly — minimize objective regret *and* cumulative constraint violation. The hard part is that constraints are **stochastic, coupled** (tenants contend for shared resources), and must hold **per round**, not just on average.

## 2. Mathematical Foundations
- **Constrained MDP (CMDP) / constrained online convex optimization:** the controller solves an MDP with per-step or cumulative cost constraints; Lagrangian / primal-dual methods (Lagrange multiplier $\lambda_i$ per SLA) are standard.
- **Bandits with knapsacks / constraints (BwK):** learning to optimize under budget/resource constraints with regret bounds.
- **Safe / constrained Bayesian optimization:** model each $\mathrm{SLA}_i$ as a GP; restrict search to the high-probability feasible set (SafeOpt-style).
- **Chance constraints & concentration:** p99 / tail-latency SLAs are chance constraints; bound violation probability via Bernstein / conformal prediction.
- **Admission control & feasibility:** packing tenants under resource bounds is a (bin-packing / generalized-assignment) feasibility problem — NP-hard.
- **Duality gap:** strong duality (Slater's condition) governs when the Lagrangian relaxation is tight.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** Cloud DBs enforce SLAs mostly by **conservative over-provisioning + isolation** (resource governors, per-tenant quotas) rather than provably-tight tuning. **SQLVM / resource-governance** work (Narasayya et al., CIDR 2013) reserves per-tenant resources; **PerfGuard / WiSeDB** and admission controllers schedule under SLA penalties. RL tuners with **safety layers** add penalty terms for SLA breaches; OnlineTune adds context-aware safety *(frontier — verify)*. Microsoft/AWS auto-tuners gate changes on regression detection to protect tenants.
- **Theory-SOTA:** primal-dual CMDP algorithms with **sublinear regret and sublinear constraint violation** (Efroni et al.; Ding et al.) and **safe BO under unknown constraints** are the formal SOTA; bandits-with-knapsacks (Badanidiyuru–Kleinberg–Slivkins) bounds the constrained-online case.

## 4. Upper Bound
For online constrained convex/CMDP settings, primal-dual algorithms achieve objective regret $\tilde O(\sqrt{T})$ **and** cumulative constraint violation $\tilde O(\sqrt{T})$ simultaneously (Mahdavi et al.; Efroni–Mannor–Pirotta 2020) — sublinear in both. Under a known Slater margin, **zero** asymptotic violation with $\tilde O(\sqrt T)$ regret is attainable. Safe-BO (SafeOpt-style) guarantees **no** high-probability constraint violation under RKHS smoothness of $\mathrm{SLA}_i$. The static feasibility/packing subproblem admits constant-factor approximations (e.g., for vector bin packing) under bounded item sizes.

## 5. Lower Bound
- **NP-hardness of feasibility:** packing tenants under multi-resource SLAs reduces from bin packing / multidimensional knapsack — deciding feasibility is **NP-hard**, and vector bin packing is hard to approximate within better than logarithmic factors.
- **Regret–violation tradeoff:** in constrained online learning, no algorithm can simultaneously beat $\Omega(\sqrt T)$ on *both* regret and violation in the worst case; achieving *exactly zero* per-round violation while still learning is impossible without a Slater-margin / safe-set assumption (safe-exploration impossibility).
- **Hard per-round chance constraints** with unknown distributions are info-theoretically unsatisfiable w.p. 1 from finite samples — only high-probability guarantees are possible.

## 6. The Gap
**Open.** Theory gives $\tilde O(\sqrt T)$ regret-and-violation for abstract CMDPs, and safe-BO gives violation-free guarantees under smoothness — but neither matches the DBMS reality of **coupled multi-tenant contention, tail-latency (p99) chance constraints, non-stationary workloads, and expensive irreversible actions**. There is no controller that provably maximizes a global objective with **hard, per-round, per-tenant** SLA guarantees under realistic shared-resource interference. The gap between "sublinear *cumulative* violation" (theory) and "*never* break a tenant's p99" (requirement) is the crux; closing it needs interference-aware constrained learning with conformal tail guarantees.

## 7. Current Research (as of June 2026)
Threads: (a) **constrained / safe RL** for tuning with per-tenant penalty shaping and Lagrangian duals *(frontier — verify)*; (b) **conformal prediction** for distribution-free p99 SLA bounds feeding a constrained optimizer; (c) interference modeling for shared-resource multi-tenancy (learned contention curves) to make constraints separable; (d) admission control + tuning co-design (which tenants to co-locate). Groups: Narasayya/Chaudhuri (Microsoft Research, SQLVM/multi-tenancy), Pavlo/CMU, Li/Cui (PKU, OnlineTune), constrained-RL theorists (Mannor, Brunskill, Zhang). Cloud vendors push the engineering edge with isolation + auto-rollback.

## 8. Future Work
- Controllers with certified per-round, per-tenant tail-SLA guarantees under contention.
- Interference-aware constrained models that keep tenant constraints separable.
- Conformal / distribution-free chance-constraint handling integrated with online optimization.
- Joint admission-control and tuning with provable global-objective optimality on the feasible set.

## 9. Key References
- **[Foundational]** A. Badanidiyuru, R. Kleinberg, A. Slivkins. *Bandits with Knapsacks.* JACM, 2018 (FOCS 2013). — [arXiv](https://arxiv.org/abs/1305.2545)
- **[SOTA]** Y. Efroni, S. Mannor, M. Pirotta. *Exploration-Exploitation in Constrained MDPs.* arXiv:2003.02189, 2020. — [arXiv](https://arxiv.org/abs/2003.02189)
- **[Foundational]** V. Narasayya, S. Das, M. Syamala, B. Chandramouli, S. Chaudhuri. *SQLVM: Performance Isolation in Multi-Tenant Relational Database-as-a-Service.* CIDR, 2013. — [PDF](https://www.cidrdb.org/cidr2013/Papers/CIDR13_Paper25.pdf)
- **[SOTA]** Y. Sui, A. Gotovos, J. Burdick, A. Krause. *Safe Exploration for Optimization with Gaussian Processes (SafeOpt).* ICML, 2015. — [PMLR](https://proceedings.mlr.press/v37/sui15.html)
- **[Foundational]** M. Mahdavi, R. Jin, T. Yang. *Trading Regret for Efficiency: Online Convex Optimization with Long-Term Constraints.* JMLR, 2012. — [JMLR](https://www.jmlr.org/papers/v13/mahdavi12a.html)
- **[Survey]** A. Pavlo et al. *Self-Driving Database Management Systems.* CIDR, 2017. — [PDF](https://www.cidrdb.org/cidr2017/papers/p42-pavlo-cidr17.pdf)

## 10. Worked Example

Two tenants share one server. Global objective $g$ = aggregate throughput; the controller picks how to split 10 CPU cores. Each tenant has a hard SLA: p99 latency $\le 100$ ms. Measured contention curves: with $c$ cores, tenant A's p99 $= 250/c$ ms and throughput $=40c$; tenant B's p99 $=180/c$ ms, throughput $=30c$.

Feasibility (admission): A needs $250/c_A\le100\Rightarrow c_A\ge2.5$; B needs $180/c_B\le100\Rightarrow c_B\ge1.8$. So $c_A+c_B\ge 4.3 \le 10$ — admissible.

Constrained optimization: maximize $40c_A+30c_B$ s.t. $c_A+c_B\le10,\ c_A\ge2.5,\ c_B\ge1.8$. A has higher marginal throughput, so push spare cores to A: $c_A=10-1.8=8.2,\ c_B=1.8$, giving throughput $40(8.2)+30(1.8)=328+54=382$.

Online/Lagrangian view: with unknown curves, run primal-dual. If a round measures B's p99 at 105 ms (violation), the multiplier $\lambda_B$ rises, reallocating a core to B next round. Over $T$ rounds, regret and cumulative violation both stay $\tilde O(\sqrt T)$ — but a single round's p99 breach already cost a refund, illustrating the "sublinear cumulative" vs. "never breach" gap of section 6.

---
*Part of the [DBMS Research catalog](../../README.md).*
