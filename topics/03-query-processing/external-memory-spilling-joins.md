---
id: 03-query-processing/external-memory-spilling-joins
title: "Optimal external-memory and spilling joins"
topic: 03-query-processing
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Optimal external-memory and spilling joins

> **Topic:** Query Processing & Execution · **ID:** `03-query-processing/external-memory-spilling-joins` · **Status:** partially-solved

## 1. Problem Statement

When a join or aggregation cannot fit its working set in main memory, the engine must *spill* intermediate state to secondary storage and stream it back, paying I/O cost. The goal is an execution strategy that is **I/O-optimal under a fixed memory budget $M$** and degrades *gracefully* and *predictably* as data grows past $M$ — no cliff where performance collapses by orders of magnitude, no unbounded memory blowup, and ideally a runtime that scales linearly in the number of spilled passes.

Variants: (a) the **binary equi-join** variant (Grace/hybrid hash join, sort-merge join under bounded $M$); (b) the **aggregation/group-by** variant (spilling hash aggregation with high group cardinality and skew); (c) the **multi-way / pipeline** variant (memory shared across several concurrent spilling operators); (d) the **adversarial-skew** variant (one key dominates, defeating naive partitioning). Decision form: given $M$, can the join complete in $\le k$ I/O passes? Optimization form: minimize total block transfers (and, secondarily, random-access count).

## 2. Mathematical Foundations

The standard cost model is the **External Memory (EM) / I/O model** of Aggarwal–Vitter: memory of $M$ words, block transfer size $B$, input size $N$ (in words); cost = number of block transfers between disk and memory. Fundamental bounds in this model:
$$\text{scan}(N)=\Theta(N/B),\qquad \text{sort}(N)=\Theta\!\Big(\tfrac{N}{B}\log_{M/B}\tfrac{N}{B}\Big).$$
A join producing output $Z$ tuples costs $\Omega(\text{scan}(N+Z))$ trivially; sort-based and hash-based equi-joins both achieve $O(\text{sort}(N)+\text{scan}(Z))$. The **cache-oblivious model** (Frigo–Leiserson–Prokop–Ramachandran) asks for the same bounds *without knowing $M,B$*, via funnelsort/distribution. For skew, the relevant object is the degree/heavy-hitter distribution; partitioning quality is governed by hashing concentration (Chernoff bounds on bucket loads) and, adversarially, by the largest group size $\Delta$, which lower-bounds any single partition's residency.

## 3. State of the Art (SOTA)

**Theory-SOTA:** Sort-merge and hybrid hash join both meet $O(\text{sort}(N))$ I/O; cache-oblivious sorting and joins (funnelsort, lazy funnels) achieve it obliviously. The optimal join under output sensitivity is captured by the same $\text{sort}(N)+\text{scan}(Z)$ frontier. **Systems-SOTA:** Modern engines — DuckDB, Umbra, Hyper, Snowflake, Spark — implement **radix/partitioned hash join** with recursive repartitioning when a partition overflows $M$, plus **graceful spilling** of hash aggregation. Umbra/Hyper's morsel-driven, memory-managed operators and DuckDB's out-of-core hash join and external sort (2022–2024) are the practical reference points. Spark's sort-based shuffle and Tungsten spilling handle petabyte joins but with coarser I/O optimality.

## 4. Upper Bound

In the EM model, both Grace hash join and external sort-merge join achieve $O\!\big(\tfrac{N}{B}\log_{M/B}\tfrac{N}{B} + \tfrac{Z}{B}\big)$ block transfers for an equi-join of total input $N$ producing $Z$ output tuples — matching $\text{sort}(N)$ up to the output term. Hybrid hash join improves the *leading constant* by keeping one partition resident, using $\sim 2(N/B)$ transfers when $\sqrt{N}\lesssim M$. Cache-obliviously, the same $O(\text{sort}(N))$ bound is attained without tuning $M,B$. Hash aggregation with $G$ groups spills in $O(\text{sort}(N))$ when $G$ exceeds memory, $O(\text{scan}(N))$ when it fits.

## 5. Lower Bound

The **sorting lower bound** $\Omega(\text{sort}(N))$ in the EM comparison/indivisibility model (Aggarwal–Vitter) carries over to joins that must group equal keys, since key-equality grouping is at least as hard as sorting the join keys. For set-intersection-style joins this is tight. Under **adversarial skew**, a single key of multiplicity $\Delta$ forces $\Omega(\Delta/B)$ residency for that partition, so no partitioning scheme can guarantee sub-$\Delta$ memory — partition-based spilling has an intrinsic skew floor. Permutation/transposition lower bounds (also Aggarwal–Vitter) bound the I/O of the repartition phase. These are I/O lower bounds, not time lower bounds.

## 6. The Gap

Asymptotic I/O optimality for *single* equi-joins and aggregations is essentially **closed** ($\Theta(\text{sort}(N))$). The open part is (1) **constants and predictability**: real spilling shows non-graceful cliffs from recursive repartitioning fan-out limits, OS page-cache interference, and random vs. sequential I/O the EM model conflates; (2) **adversarial skew**: provably bounded-memory execution when one group dominates, without quadratic fallbacks; (3) **shared-budget multi-operator** spilling, where allocating $M$ across concurrent pipelines to minimize *total* I/O is an unsolved online/scheduling problem. There is no clean theory matching the empirically observed "graceful degradation" desideratum.

## 7. Current Research (as of June 2026)

Active directions: out-of-core query execution in DuckDB and Umbra emphasizing *robust* spilling with bounded memory amplification; **anti-caching** and buffer-managed operators (CMU/Pavlo); memory-management policies that spill the right operator under pressure (morsel-driven, NUMA-aware). Theory side: continued work on cache-oblivious and output-sensitive joins, and on skew-resilient partitioning. *(frontier — verify)* 2025–2026 work reports near-linear-degradation external hash joins and "spill-aware" cost models that the optimizer uses to choose join order under memory limits. Groups/people: Neumann/Leis (TUM, Umbra), Boncz/Raasveldt (CWI/DuckDB), Pavlo (CMU), Idreos (Harvard, self-designing/learned data systems).

## 8. Future Work

- A cost model that distinguishes sequential vs. random I/O and predicts the *shape* of degradation, not just asymptotics.
- Provably skew-robust spilling joins with bounded worst-case memory under adversarial key distributions.
- Online memory-budget allocation across concurrent spilling operators minimizing total transfers.
- Integration with modern storage (NVMe, CXL, persistent memory) where the $B$/latency assumptions of the classic EM model break.
- Tight constants for graceful-degradation guarantees, bridging theory and the empirical "no cliffs" requirement.

## 9. Key References

- **[Foundational]** Aggarwal, Vitter. *The Input/Output Complexity of Sorting and Related Problems.* CACM, 1988. — [DOI](https://doi.org/10.1145/48529.48535)
- **[Foundational]** DeWitt, Katz, Olken, Shapiro, Stonebraker, Wood. *Implementation Techniques for Main Memory Database Systems* / Grace & hybrid hash join, SIGMOD, 1984. — [DOI](https://doi.org/10.1145/971697.602261)
- **[Foundational]** Frigo, Leiserson, Prokop, Ramachandran. *Cache-Oblivious Algorithms.* FOCS, 1999. — [DBLP](https://dblp.org/rec/conf/focs/FrigoLPR99.html)
- **[SOTA]** Leis, Boncz, Kemper, Neumann. *Morsel-Driven Parallelism: A NUMA-Aware Query Evaluation Framework.* SIGMOD, 2014. — [DOI](https://doi.org/10.1145/2588555.2610507)
- **[SOTA]** Raasveldt, Mühleisen. *DuckDB: an Embeddable Analytical Database.* SIGMOD (demo), 2019; with out-of-core operator work, 2022–2024. — [DOI](https://doi.org/10.1145/3299869.3320212)
- **[Survey]** Graefe. *Query Evaluation Techniques for Large Databases.* ACM Computing Surveys, 1993. — [DOI](https://doi.org/10.1145/152610.152611)

## 10. Worked Example

Grace hash join of $R \bowtie S$ on disk. Let total input $N = 10^9$ tuples, block size
$B = 10^6$ tuples/block ($N/B = 10^3$ blocks), and memory $M = 32\times10^6$ tuples
($M/B = 32$ partitions per pass).

I/O cost is $\text{sort}(N) = \tfrac{N}{B}\log_{M/B}\tfrac{N}{B}
= 10^3 \cdot \log_{32}(10^3) \approx 10^3 \cdot 1.99 \approx 1.99\times10^3$ block transfers
(2 partitioning passes: $\lceil\log_{32}10^3\rceil = 2$), then a final scan to probe — total
$\approx 3$ passes over the data.

**Skew floor.** Now suppose one key has multiplicity $\Delta = 50\times10^6$ tuples. That
single key cannot be split by hashing: its partition needs $\Delta/B = 50$ blocks resident,
which exceeds $M/B = 32$. No partition scheme avoids this — the build side for that key alone
forces $\Omega(\Delta/B)$ memory, illustrating the intrinsic adversarial-skew lower bound and
why naive recursive repartitioning loops without progress on a dominant key.

---
*Part of the [DBMS Research catalog](../../README.md).*
