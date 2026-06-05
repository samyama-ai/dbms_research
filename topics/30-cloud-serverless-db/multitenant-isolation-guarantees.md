# Multi-tenant performance isolation guarantees

> **Topic:** Cloud & Serverless Databases · **ID:** `30-cloud-serverless-db/multitenant-isolation-guarantees` · **Status:** open

## 1. Problem Statement

A multi-tenant serverless database packs many tenants onto shared compute, shared buffer pool, and shared storage bandwidth to raise utilization. A heavy or adversarial tenant — a *noisy neighbor* — can degrade a co-located tenant's latency. The **isolation-guarantee problem**: design a scheduler / admission-and-allocation policy that **provably bounds** any tenant's worst-case latency (or throughput) degradation due to others, ideally as a function of that tenant's reservation, while keeping aggregate utilization high.

Variants: (a) **decision** — can all tenants' SLOs be met simultaneously on this hardware (feasibility/packing)? (b) **guarantee design** — give a policy with a proven degradation bound $\rho$ (e.g., a tenant gets $\ge 1/\rho$ of its standalone performance); (c) **fairness vs. utilization** — maximize utilization subject to per-tenant isolation floors.

## 2. Mathematical Foundations

Two formal lenses. **(1) Scheduling / fair queuing:** generalized processor sharing (GPS) and its packet/IO approximations (WFQ, DRR, mClock) give each tenant a weighted share with bounded latency error; for a tenant with reservation $r_i$ and total capacity $C$, GPS guarantees rate $r_i$ and bounds delay by $O(L_{\max}/r_i)$. **(2) Shared buffer pool / cache partitioning:** allocating cache among tenants to bound miss-rate inflation is a **submodular / convex resource-allocation** problem; miss-ratio curves (MRCs) are typically convex, so marginal-gain (greedy) allocation is near-optimal. Dominant-Resource Fairness (DRF, Ghodsi et al.) extends max-min fairness to multiple resources (CPU, memory, IO) with strategy-proofness and sharing-incentive guarantees. The worst-case-degradation question maps to bounding the *competitive* slowdown a tenant suffers versus its isolated baseline.

## 3. State of the Art (SOTA)

- **Systems-SOTA:** mClock (Gulati et al., OSDI 2010) provides proportional-share + reservation + limit for shared storage IO; PARDA and Pisces (Shue et al., OSDI 2012) deliver per-tenant fairness in shared key-value stores; Retro (NSDI 2015) and Cake offer cross-stack resource control; Snowflake/Aurora use per-tenant resource governors and warehouse isolation; CPU schedulers use cgroups/CFS bandwidth control. Shared-buffer isolation uses per-tenant cache quotas and MRC-guided partitioning (e.g., based on Mattson/LRU stack distances).
- **Theory-SOTA:** WFQ/GPS delay bounds and DRF fairness guarantees are the rigorous core; tail-latency isolation under bursty workloads lacks tight theory.

## 4. Upper Bound

WFQ achieves per-flow delay within $L_{\max}/C$ of ideal GPS, giving each tenant a **provable rate guarantee** and bounded worst-case queuing delay. DRF guarantees sharing-incentive, strategy-proofness, Pareto-efficiency, and envy-freeness for multi-resource allocation. For cache, greedy MRC-based partitioning is a $(1-1/e)$-style near-optimal allocation when miss-reduction is submodular. These bound a tenant's degradation to a function of its weight/reservation.

## 5. Lower Bound

Strong **impossibility** results frame the limits: you cannot simultaneously have perfect work-conservation (full utilization), perfect isolation (zero cross-tenant interference), and arbitrary burst tolerance — some axis must yield. Cache contention has an information-theoretic floor: with a shared pool of size $M$ and $k$ tenants, no policy can give every tenant its full standalone hit rate unless $\sum_i$ working-set$_i \le M$ (a packing lower bound). Tail-latency interference from shared-resource contention (memory bandwidth, LLC) is **not fully controllable** by software scheduling alone — a hardware-rooted lower bound.

## 6. The Gap

Rate/throughput isolation is largely *solved* (WFQ/DRF/mClock). The open gap is **tail-latency** isolation under shared *memory hierarchy and buffer pool*: there is no policy with a proven p99-degradation bound that also keeps utilization high under bursty, antagonistic workloads. Closing it requires either hardware QoS integration (Intel RDT/CAT-style) with provable bounds, or a tight characterization of achievable (utilization, p99-isolation) trade-offs.

## 7. Current Research (as of June 2026)

Active: hardware-assisted isolation (Intel RDT/MBA), interference-aware placement, learned co-location predictors (Google's Borg/PerfIso lineage), and buffer-pool partitioning for cloud DBs. Groups: MIT (Heracles/PerfIso lineage), Stanford, CMU, Microsoft Research, and cloud vendors. *(frontier — verify)* 2025–2026 work explores ML interference predictors combined with formal admission control to give probabilistic tail-isolation SLAs; provable worst-case p99 bounds under shared LLC remain unsettled.

## 8. Future Work

- Provable p99-degradation bounds for shared buffer pools and LLC.
- Co-design of software schedulers with hardware QoS (CAT/MBA) under formal guarantees.
- Strategy-proof multi-resource allocation that also bounds tail latency.
- Isolation guarantees that survive scale-to-zero / dynamic tenant churn.

## 9. Key References

- **[Foundational]** Demers, Keshav, Shenker. *Analysis and Simulation of a Fair Queueing Algorithm.* SIGCOMM, 1989.
- **[Foundational]** Ghodsi, Zaharia, et al. *Dominant Resource Fairness: Fair Allocation of Multiple Resource Types.* NSDI, 2011.
- **[SOTA]** Gulati, Merchant, Varman. *mClock: Handling Throughput Variability for Hypervisor IO Scheduling.* OSDI, 2010.
- **[SOTA]** Shue, Freedman, Shaikh. *Performance Isolation and Fairness for Multi-Tenant Cloud Storage (Pisces).* OSDI, 2012.
- **[SOTA]** Lo, Cheng, et al. *Heracles: Improving Resource Efficiency at Scale.* ISCA, 2015.

---
*Part of the [DBMS Research catalog](../../README.md).*
