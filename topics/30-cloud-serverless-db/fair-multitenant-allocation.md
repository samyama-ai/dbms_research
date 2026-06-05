# Fair resource allocation across tenants

> **Topic:** Cloud & Serverless Databases · **ID:** `30-cloud-serverless-db/fair-multitenant-allocation` · **Status:** open

## 1. Problem Statement
A multi-tenant cloud database shares a finite pool of CPU, memory, I/O bandwidth, and buffer-cache capacity across many tenants whose demands fluctuate. The operator must allocate these *multiple* resources so the policy is simultaneously:
(i) **fair** — no tenant is starved; a tenant cannot improve its share by lying about demand (strategyproofness);
(ii) **work-conserving** — no resource sits idle while some tenant has demand for it;
(iii) **SLO-respecting** — each tenant's latency/throughput SLA is met when its demand is within its contracted envelope.

- **Decision variant:** Given per-tenant demand vectors and SLOs, does a feasible allocation satisfying all three properties exist?
- **Optimization variant:** Maximize aggregate utilization (or a fairness welfare function) subject to SLOs and a fairness axiom set.
- **Online variant:** Maintain such an allocation as demands change, minimizing reallocation churn and SLO violations.

## 2. Mathematical Foundations
With a *single* divisible resource, **max-min fairness** is the canonical answer. With **multiple heterogeneous resources** (CPU + RAM + I/O), the right notion is **Dominant Resource Fairness (DRF)** (Ghodsi et al., NSDI 2011): each tenant's *dominant share* is its largest share across resource types, and DRF max-min-fairly equalizes dominant shares. DRF uniquely satisfies four axioms: **sharing incentive, strategyproofness, Pareto efficiency (work-conservation), and envy-freeness**.

Formally, tenant $i$ has demand vector $d_i \in \mathbb{R}^k_{\ge 0}$ over $k$ resources of capacities $C\in\mathbb{R}^k$. Allocate $a_i = x_i d_i$ (scaled demand); dominant share $s_i = \max_r a_{ir}/C_r$. DRF solves
$$
\max\ \min_i s_i \quad\text{s.t.}\quad \sum_i a_{ir} \le C_r\ \forall r,\quad a_i \parallel d_i .
$$
DRF reduces to max-min when $k=1$ and to proportional sharing under weights. Alternatives: **Competitive Equilibrium from Equal Incomes (CEEI)** / **Nash social welfare** (maximize $\prod_i u_i$) gives Pareto-efficient envy-free allocations of divisible goods but is *not* strategyproof for $k>1$. The tension: the **Hylland–Zeckhauser / impossibility results** show no mechanism for multiple divisible resources is simultaneously strategyproof, Pareto-efficient, *and* envy-free beyond DRF's specific structure — and adding hard **SLO (latency) constraints**, which are non-linear and queueing-dependent, breaks DRF's clean axioms.

## 3. State of the Art (SOTA)
**Theory-SOTA.** **DRF** (NSDI 2011) and its extensions: DRFH (heterogeneous servers), weighted/hierarchical DRF, and DRF for indivisible tasks. CEEI / Nash-welfare fair division (Caragiannis et al., EC 2016, "unreasonable fairness of Nash welfare").

**Systems-SOTA.** Cluster managers **Mesos** and **YARN** ship DRF schedulers. Database-specific multi-tenancy: **SQLVM / Azure SQL DB** resource governance, **Amazon RDS/Aurora** I/O and ACU isolation, **Snowflake** virtual-warehouse isolation (isolation by provisioning rather than sharing), and research systems like **Pisces** (predictable shared storage, OSDI 2012), **Cake** (consolidated I/O scheduling), and **PerfIso / Retro** (OSDI 2015, resource management across the stack). **Mittos** (OSDI 2017) gives SLO-aware millisecond tail-latency I/O.

## 4. Upper Bound
DRF computes the fair allocation in polynomial time (a sequence of water-filling steps), is **strategyproof, Pareto-optimal, envy-free, and sharing-incentive-satisfying** — an exact, not approximate, guarantee for *divisible* resources without SLO constraints. For *indivisible* allocation maximizing Nash welfare, there are constant-factor and PTAS-type approximations; envy-freeness-up-to-one-good (EF1) plus Pareto-efficiency is achievable in poly time for goods.

## 5. Lower Bound
Adding strict latency SLOs makes the joint problem hard. Indivisible fair allocation that is *exactly* envy-free is **NP-hard** to even decide; maximizing Nash social welfare with indivisible goods is **APX-hard** (NP-hard to approximate beyond a constant). For mechanism design, **impossibility theorems** (in the spirit of Hylland–Zeckhauser; and Gibbard–Satterthwaite for general social choice) show no mechanism over multiple resources gives strategyproofness + efficiency + envy-freeness once preferences are unrestricted. Queueing-theoretic lower bounds (work-conservation vs. isolation) imply you *cannot* guarantee both full work-conservation and hard per-tenant tail-latency isolation under bursty demand — a fundamental tension.

## 6. The Gap
DRF closes the divisible, SLO-free case optimally. The **open** gap is the *combination*: no allocation rule is known to be simultaneously DRF-style fair, fully work-conserving, **and** SLO-respecting under fluctuating demand, because SLOs are non-linear queueing constraints that conflict with both fairness axioms and work-conservation. There is no matching upper/lower bound for "fair + work-conserving + tail-SLO." Closing it needs either a new axiomatization that admits latency constraints or an impossibility result pinning down exactly which two of the three properties can coexist.

## 7. Current Research (as of June 2026)
- SLO-aware fair scheduling that trades a controlled amount of work-conservation for tail isolation. *(frontier — verify)*
- Learning-based admission/throttling that predicts per-tenant burst and pre-reserves headroom; active in serverless-DB autoscaling teams. *(frontier — verify)*
- Fair allocation for **disaggregated** memory/CXL pools, where the "resources" are now remote-memory bandwidth.
- Groups: Ghodsi/Stoica lineage (Berkeley Sky/RISE), Microsoft Research multi-tenant DB (SQLVM), fair-division theory community (Caragiannis, Moulin).

## 8. Future Work
- An impossibility/possibility map for fairness × work-conservation × SLO.
- Strategyproof mechanisms robust to tenants gaming burst patterns.
- Hierarchical fairness across nested tenants (orgs → teams → apps).

## 9. Key References
- **[Foundational]** Ghodsi, A. et al. *Dominant Resource Fairness: Fair Allocation of Multiple Resource Types.* NSDI, 2011. — [USENIX](https://www.usenix.org/conference/nsdi11/dominant-resource-fairness-fair-allocation-multiple-resource-types)
- **[SOTA]** Caragiannis, I. et al. *The Unreasonable Fairness of Maximum Nash Welfare.* ACM EC, 2016. — [DOI](https://doi.org/10.1145/2940716.2940726)
- **[Systems]** Shue, D., Freedman, M., Shaikh, A. *Performance Isolation and Fairness for Multi-Tenant Cloud Storage (Pisces).* OSDI, 2012. — [USENIX](https://www.usenix.org/conference/osdi12/technical-sessions/presentation/shue)
- **[Systems]** Mace, J., Bodik, P., Fonseca, R., Musuvathi, M. *Retro: Targeted Resource Management in Multi-tenant Distributed Systems.* NSDI, 2015. — [USENIX](https://www.usenix.org/conference/nsdi15/technical-sessions/presentation/mace)
- **[Foundational]** Moulin, H. *Fair Division and Collective Welfare.* MIT Press, 2003. — [DOI](https://doi.org/10.7551/mitpress/2954.001.0001)

## 10. Worked Example

**DRF in action.** Capacity $C = (\text{9 CPU},\ \text{18 GB})$. Two tenants:
- Tenant A's tasks each need $(1\text{ CPU},\ 4\text{ GB})$. Shares per task: CPU $1/9$, RAM $4/18 = 2/9$. **Dominant resource = RAM** (larger fraction).
- Tenant B's tasks each need $(3\text{ CPU},\ 1\text{ GB})$. Shares per task: CPU $3/9 = 1/3$, RAM $1/18$. **Dominant resource = CPU**.

DRF equalizes *dominant shares*. Let A run $x$ tasks, B run $y$ tasks. Dominant shares: A $= \tfrac{2x}{9}$ (RAM), B $= \tfrac{3y}{9}$ (CPU). Set equal and respect capacity:
$$\tfrac{2x}{9} = \tfrac{3y}{9}\ \Rightarrow\ 2x = 3y,\qquad x + 3y \le 9\ (\text{CPU}),\quad 4x + y \le 18\ (\text{RAM}).$$
Solving: $x = 3,\ y = 2$. Check: CPU used $= 3 + 6 = 9$ (full), RAM used $= 12 + 2 = 14 \le 18$. Each tenant's dominant share $= \tfrac{2\cdot3}{9} = \tfrac{6}{9} = \tfrac{2}{9}\cdot3 = 0.67$ — **equalized**.

So A gets $(3\text{ CPU},12\text{ GB})$, B gets $(6\text{ CPU},2\text{ GB})$. CPU is saturated (work-conserving); neither tenant envies the other's bundle given its own demands. Note: adding a *latency SLO* — say B must finish within $T$ — could force $y > 2$, breaking the clean equal-dominant-share solution. That is precisely the open tension in §6.

---
*Part of the [DBMS Research catalog](../../README.md).*
