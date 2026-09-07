---
id: 10-consensus-coordination/consensus-energy-cost
title: "Consensus Energy/Cost Optimality"
topic: 10-consensus-coordination
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Consensus Energy/Cost Optimality

> **Topic:** Consensus & Coordination · **ID:** `10-consensus-coordination/consensus-energy-cost` · **Status:** empirically-open

## 1. Problem Statement

Consensus protocols are traditionally analyzed by **message count**, **round count**, and **latency**. But on a real cloud, what an operator pays is **dollars** and **joules**: cross-AZ/cross-region egress fees, per-request charges, VM-hours for replicas idling to maintain quorum, and the energy of CPU/NIC work for signing, hashing, and persisting. A protocol that is optimal in message count can be far from optimal in cost — e.g., a message that crosses a billed region boundary costs orders of magnitude more than one within an AZ, and a CPU-heavy BFT signature scheme burns energy a crash-fault protocol does not.

The problem: **minimize the expected dollar and energy cost of reaching consensus under a realistic, possibly time-varying cloud pricing and power model, subject to safety, a fault-tolerance target, and a latency SLO.** Variants: (a) *decision* — does a configuration meet a cost budget at a target throughput? (b) *optimization* — choose protocol, replica placement, quorum shape, and batching to minimize $\mathbb{E}[\text{cost}]$; (c) *online* — adapt as spot prices, egress tiers, and carbon intensity fluctuate.

The point is that the **right cost metric is not the right message/round metric**, and protocols Pareto-optimal under one can be dominated under the other.

## 2. Mathematical Foundations

Let a protocol's execution produce messages $m \in M$ with a price function $\text{price}(m)$ depending on source/destination billing zones, and per-node compute work $w_i$ with energy $e_i = \kappa \cdot w_i$ (CPU/crypto/persistence). Total cost per decided command:

$$ \text{Cost} = \underbrace{\sum_{m\in M}\text{price}(m)}_{\text{network }\$} \;+\; \underbrace{\sum_i (\rho_i \cdot \tau_i)}_{\text{VM-hours }\$} \;+\; \underbrace{\beta\sum_i e_i}_{\text{energy/carbon}}, $$

where $\rho_i$ is the instance hourly rate, $\tau_i$ the occupancy, and $\beta$ a $/joule or $/kgCO_2$ weight. Pricing is **non-uniform and non-metric**: intra-AZ ≈ free, inter-AZ cheap, inter-region/egress expensive, and these violate triangle-inequality-style assumptions, so classic latency-optimal placements need not be cost-optimal. Batching amortizes fixed per-message and per-round costs: with batch size $b$, per-command network cost scales like $O(1/b)$ but latency grows with batch fill time — a Pareto trade. Energy adds a term distinguishing **crash-fault** ($f+1$ to $2f+1$ replicas, no crypto) from **BFT** ($3f+1$ replicas, signatures/MACs, $\kappa_{\text{BFT}} \gg \kappa_{\text{CFT}}$). The optimization is a **constrained facility-location / quorum-placement** problem over a non-metric cost space.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** Lower bounds on rounds/messages — **Paxos/Fast Paxos** round-optimality (Lamport), the $3f+1$ BFT replica bound (Castro–Liskov **PBFT**, OSDI 1999), and message-complexity-optimal BFT (**HotStuff**, Yin et al., PODC 2019, linear per-view). These optimize *counts*, not *prices*.
- **Systems-SOTA:** Geo-quorum placement for latency/cost — **WPaxos** (Ailijiang et al., 2019), **DPaxos**, **Spanner**'s placement; energy-aware/green datacenter scheduling literature; **carbon-aware** computing (e.g., Google's carbon-intelligent shifting, Microsoft's carbon-aware SDK) applied to *jobs* but not yet to *consensus quorum shape* *(frontier — verify)*. Cost-aware replica configuration appears in **CockroachDB**/**TiDB** tuning but as heuristics.

## 4. Upper Bound

The best constructive results are *count*-optimal and translate only partially to cost: HotStuff achieves **$O(n)$ messages per decision** (vs. $O(n^2)$ for PBFT), which is a strict cost win when each message is independently billed; batching drives per-command fixed costs to **$O(1/b)$**. Latency-cost placement heuristics (WPaxos-style) reduce inter-region traffic by localizing quorums to the region issuing the writes, empirically cutting egress cost substantially. But there is **no protocol proven cost-optimal against a general cloud pricing model** — only message/round optimality plus empirical cost reductions.

## 5. Lower Bound

- **Round/message lower bounds:** consensus needs $\ge 2$ message delays in the common case (Lamport's lower bound for non-trivial agreement) and BFT needs $\ge 3f+1$ replicas (Lamport–Shostak–Pease / PBFT) and a quadratic worst-case communication without threshold cryptography — these lower-bound the *count*, hence a floor on cost given any positive per-message price.
- **Quorum-cost floor:** any safe quorum must intersect ($|Q_1|+|Q_2|>n$), so a minimum volume of (possibly cross-zone) communication is unavoidable; if the cheapest intersecting quorum still spans a billed boundary, that egress cost is a hard floor.
- **No cost-specific lower bound** matching the pricing model exists: the field lacks an information-theoretic or fine-grained lower bound stated in *dollars/joules* under non-metric pricing — this absence is exactly why the problem is *empirically-open*.

## 6. The Gap

Wide and genuinely empirical. Upper bounds are message/round-count results plus ad-hoc cost-reducing placement; there is **no formal cost model, no cost-stated lower bound, and no protocol proven optimal (or constant-factor) against real cloud pricing and energy**. The gap is both *definitional* (agree on a standard pricing/energy cost model) and *algorithmic* (design + prove cost-optimal quorum/placement/batching, likely showing NP-hardness of exact optimization and giving approximations). Closing it requires importing facility-location/non-metric-optimization theory and carbon-aware scheduling into consensus design with matching bounds.

## 7. Current Research (as of June 2026)

Active directions: carbon-aware and spot-price-aware replica placement and quorum selection for SMR *(frontier — verify)*; energy profiling of BFT crypto (signature aggregation, threshold/BLS) to quantify the joules-per-decision premium of Byzantine tolerance *(frontier — verify)*; cost-model-driven autotuning in distributed SQL (CockroachDB Labs, PingCAP); leaderless/flexible-quorum protocols evaluated under egress-cost metrics rather than latency alone. Sustainable-computing groups (e.g., the carbon-aware systems community) are beginning to target coordination overhead.

## 8. Future Work

- A standardized dollar+energy cost model for consensus, with a cost-stated lower bound under non-metric cloud pricing.
- Provably (constant-factor) cost-optimal quorum placement and batching; hardness classification of exact optimization.
- Online algorithms adapting protocol/quorum to spot-price, egress-tier, and carbon-intensity drift with regret bounds.
- Crypto-cost-aware BFT: choosing signature schemes/aggregation to minimize joules-per-decision at a security target.

## 9. Key References

- **[Foundational]** Miguel Castro, Barbara Liskov. *Practical Byzantine Fault Tolerance.* OSDI, 1999. — [ACM](https://dl.acm.org/doi/10.5555/296806.296824)
- **[SOTA]** Maofan Yin, Dahlia Malkhi, Michael K. Reiter, Guy Golan-Gueta, Ittai Abraham. *HotStuff: BFT Consensus with Linearity and Responsiveness.* PODC, 2019. — [arXiv](https://arxiv.org/abs/1803.05069)
- **[SOTA]** Ailidani Ailijiang, Aleksey Charapko, Murat Demirbas, Tevfik Kosar. *WPaxos: Wide Area Network Flexible Consensus.* IEEE TPDS, 2019. — [DOI](https://doi.org/10.1109/TPDS.2019.2929793)
- **[Foundational]** Leslie Lamport, Robert Shostak, Marshall Pease. *The Byzantine Generals Problem.* ACM TOPLAS, 1982. — [DOI](https://doi.org/10.1145/357172.357176)
- **[SOTA]** Ana Radovanović, et al. *Carbon-Aware Computing for Datacenters.* IEEE Transactions on Power Systems, 2023. — [DOI](https://doi.org/10.1109/TPWRS.2022.3173250)

## 10. Worked Example

A 3-replica Paxos group commits one write. Two placements, same count of cross-node messages, very different bills.

Assume egress pricing: intra-AZ $= \$0$/GB, inter-AZ $= \$0.01$/GB, inter-region $= \$0.09$/GB, and each round's quorum messages move $1$ GB total.

**Placement A — all 3 in one region, spread across AZs.** A leader-to-quorum round crosses AZ boundaries only: network cost $\approx 1\text{ GB} \times \$0.01 = \$0.01$ per decision.

**Placement B — one replica per region (geo-spread for survivability).** The same round now crosses region boundaries: $1\text{ GB} \times \$0.09 = \$0.09$ — a $9\times$ cost for an *identical* message count.

**Energy term.** Switching from CFT to BFT adds signature work. With $\kappa_{\text{BFT}}=10\,\kappa_{\text{CFT}}$ and $\beta\sum_i e_i = \$0.002$ (CFT) vs $\$0.02$ (BFT) per decision, BFT's crypto alone can exceed Placement A's whole network bill — showing why $O(n)$ message-optimality (HotStuff) need not be dollar-optimal.

---
*Part of the [DBMS Research catalog](../../README.md).*
