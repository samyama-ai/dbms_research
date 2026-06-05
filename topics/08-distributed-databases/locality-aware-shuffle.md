# Locality-Aware Shuffle Placement

> **Topic:** Distributed Query Processing · **ID:** `08-distributed-databases/locality-aware-shuffle` · **Status:** empirically-open

## 1. Problem Statement

An all-to-all shuffle (the exchange operator) repartitions intermediate tuples by a hash/range key across $p$ workers spread over a multi-tier topology — cores, racks, availability zones, regions — where cross-tier bandwidth is scarce and cross-zone/region egress is *billed*. The problem: assign output partitions to workers (and choose which partition function realizations to use) so that (a) tuples stay local where their producers and consumers already reside, minimizing bytes crossing expensive boundaries, while (b) keeping load balanced and (c) respecting the partitioning semantics the downstream operator requires (co-location of equal keys).

- **Optimization variant:** minimize weighted cross-zone egress cost subject to a per-worker load cap $L$.
- **Decision variant:** does a placement exist with egress $\le B$ and load $\le L$?
- **Online variant:** decide placement before final cardinalities/key distributions are known.

It is "empirically-open": engines use heuristics that work well in practice, but no placement algorithm provably approximates the cost-minimal locality-aware shuffle under realistic tiered-bandwidth/egress-pricing models.

## 2. Mathematical Foundations

Model the topology as a weighted tree (or hierarchical hypergraph) $T$ with leaves = workers and edge weights = per-byte cost across that tier (intra-rack $\approx 0$, cross-zone $> 0$, cross-region $\gg 0$). Let $f_{ij}$ be the byte flow that producer node $i$ must send to the worker holding partition that consumer $j$ reads. A placement is a map $\pi: \text{partitions} \to \text{workers}$. The objective is

$$ \min_{\pi}\; \sum_{i,j} f_{ij}\cdot \mathrm{cost}_T\big(i, \pi(\text{key}(i,j))\big) \quad \text{s.t.}\quad \sum_{q:\pi(q)=w}\! |q| \le L\ \ \forall w. $$

This generalizes **quadratic assignment** and **minimum $k$-cut / graph partitioning with capacity constraints**, both NP-hard. With co-location constraints (equal keys must share a worker) it relates to **balanced graph partitioning** and **hypergraph min-cut** (the producer-consumer hypergraph). Locality bounds connect to *bandwidth* and *cut-sparsifier* theory on the topology tree.

## 3. State of the Art (SOTA)

- **Systems-SOTA:** Spark AQE with *coalesce/skew-join* and locality-preferred scheduling; Sailfish and Riffle's shuffle-merge to cut fan-out; Magnet (push-based shuffle, VLDB 2020) co-locates merged blocks; Cosco/Zeus at Meta optimize shuffle service placement; Google's Dataflow Shuffle and Snowflake's cloud-services layer route to minimize cross-zone traffic. Cloud cost-aware planners (e.g., zone-affinity scheduling) are heuristic.
- **Theory-SOTA:** Topology-aware MapReduce scheduling and the *data-locality* online matching results (Maguluri–Srikant) bound throughput but not egress cost; balanced graph-partitioning approximations (Krauthgamer–Naor–Schwartz) bound cut but ignore tiered/billed weights.

## 4. Upper Bound

On a tree topology with capacities relaxed, the placement reduces to **min-cost assignment** solvable in polynomial time; with balance constraints, the best known is an $O(\log p)$-approximation via balanced-cut machinery (recursive sparsest-cut), holding in the **offline RAM model** with exact flow knowledge. For 2-tier (intra- vs cross-zone) and uniform partition sizes, a $(1+\epsilon)$ bicriteria placement (slightly exceeding $L$) is achievable by LP rounding.

## 5. Lower Bound

The problem is **NP-hard** (reduction from balanced minimum cut / QAP), and balanced graph partitioning has no PTAS unless P=NP; under the **Small-Set-Expansion / Unique-Games** conjectures, even $O(1)$-approximation for the balanced-cut surrogate is ruled out. In the **online** setting (placement before key distribution is revealed), an adversary forces $\Omega(\log p)$ competitive ratio on egress for any deterministic algorithm via a topology-tree adversary argument — an information-theoretic/competitive lower bound.

## 6. The Gap

Offline, the gap is between the $O(\log p)$ balanced-partition approximation and NP/SSE-hardness of $O(1)$ — plausibly closed only up to the partitioning conjectures. The real open gap is *practical*: no deployed scheduler comes with an egress-cost approximation guarantee under tiered bandwidth + billed cross-region traffic + skew, and we lack tight online competitive bounds when cardinalities are revealed incrementally. Closing it needs a model that jointly captures billing, bandwidth tiers, and skew with a provable algorithm validated on cloud workloads.

## 7. Current Research (as of June 2026)

Push-based and disaggregated shuffle services with locality hints (Meta Cosco/Zeus successors, Uber, LinkedIn Magnet line); cost-aware multi-cloud query placement minimizing egress (CMU, MIT, Berkeley Sky Computing) *(frontier — verify)*; learned shuffle partitioners predicting key distribution to pre-place partitions. Theory side: cut-sparsifier-based approximations for tiered topologies and online matching with locality (Srikant, Naor groups).

## 8. Future Work

- A provable bicriteria egress-vs-load approximation under $k$-tier billed topologies.
- Tight online competitive ratios when cardinalities/keys are revealed in stages.
- Integration with skew handling: locality-aware *and* heavy-hitter-aware placement.
- Cross-cloud Sky-Computing shuffle that treats egress price as a first-class cost.

## 9. Key References

- **[SOTA]** M. Shen et al. *Magnet: Push-based Shuffle Service for Large-scale Data Processing.* VLDB 2020.
- **[Foundational]** R. Krauthgamer, J. Naor, R. Schwartz. *Partitioning Graphs into Balanced Components.* SODA 2009.
- **[Foundational]** S. Rao. *Small Distortion and Volume Preserving Embeddings for Planar and Euclidean Metrics.* SoCG 1999 (sparsest-cut machinery underlying balanced partitioning).
- **[SOTA]** S. Rajaraman et al. / Sailfish: S. Rao, R. Ramakrishnan et al. *Sailfish: A Framework for Large Scale Data Processing.* SoCC 2012.
- **[Survey]** P. Carbone et al. *Apache Flink / State and Shuffle Management*, and Spark AQE documentation — systems references for adaptive shuffle.

---
*Part of the [DBMS Research catalog](../../README.md).*
