---
id: 03-query-processing/adaptive-hash-vs-sort
title: "Robust adaptive hash vs. sort decisions"
topic: 03-query-processing
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Robust adaptive hash vs. sort decisions

> **Topic:** Query Processing & Execution · **ID:** `03-query-processing/adaptive-hash-vs-sort` · **Status:** open

## 1. Problem Statement

For both **equi-joins** and **grouping/aggregation**, an engine must choose between two
algorithmic families: **hash-based** (build a hash table, probe / hash-aggregate) and
**sort-based** (sort inputs, then merge-join / sort-aggregate). The choice is classically made
by the optimizer using cardinality and sortedness estimates, but those estimates are
frequently wrong, and the *wrong* choice can be catastrophic: hashing degrades under heavy
key skew, high distinct-value counts, and memory pressure (spilling); sorting wastes work
when output order is not needed and when inputs are far from sorted.

Problem: design an **online, robust** mechanism that selects (or smoothly blends) hashing and
sorting **during execution**, using only cheaply observable runtime signals, with a provable
or empirically robust **worst-case regret** against the better of the two — *without* relying
on accurate prior statistics.

Variants: **decision** (pick one family given partial runtime observations); **competitive/
online** (minimize regret vs. the offline-optimal family); **hybrid** (interleave or switch
mid-operator, e.g., start hashing and fall back to sort-based partitioning under skew/spill).

## 2. Mathematical Foundations

For aggregation over $n$ tuples with $g$ distinct groups, hash-aggregation costs $\Theta(n)$
expected time and $\Theta(g)$ space, but suffers $\Theta(n)$ extra cache misses when $g$
exceeds cache capacity. Sort-aggregation costs $\Theta(n\log n)$ comparisons (or $\Theta(n
\log_{M/B} (n/B))$ I/Os in external memory) but is cache-friendly and skew-immune. The
crossover depends on $g/n$, key distribution, available memory $M$, and whether the output is
consumed in sorted order downstream.

The robust-choice problem is naturally framed as **online algorithm selection / metrical task
systems**: an adversary picks the data; the engine commits to (or switches between) algorithms
based on a prefix. A core tool is **competitive analysis** — the engine seeks bounded
competitive ratio against the offline optimal family. Skew is captured by the distribution's
**$\ell_2$ frequency moment** $F_2 = \sum_j f_j^2$; hashing's collision cost scales with
$F_2$, while sort cost is skew-insensitive (depending only on $n\log n$). This asymmetry is the
mathematical heart of the trade-off.

## 3. State of the Art (SOTA)

- **Systems SOTA.** Most engines decide statically in the optimizer (Selinger-style costing,
  SIGMOD 1979). Postgres, HyPer, DuckDB choose hash vs. sort from estimated cardinalities and
  required orderings. *Generalized Hash Teams* and *Eddies*/Tukwila pioneered runtime
  adaptivity (Avnur & Hellerstein, SIGMOD 2000; Ives et al.).
- **G-join / sort-merge resurgence.** Graefe's "**A Generalized Join Algorithm**" (BTW 2011)
  argues a single robust join that degrades gracefully between hash and sort-merge, motivated
  precisely by estimation error.
- **Adaptive aggregation.** Müller et al. and others show runtime switching between hash and
  sort aggregation based on observed distinct-value growth, which is the closest practical
  realization of the robust decision.

## 4. Upper Bound

The strongest practical guarantee is a **graceful-degradation hybrid**: run radix/hash
partitioning, but cap partition fan-out and *fall back to sorting* any partition that does not
shrink (skew detection), yielding $O(n\log n)$ worst case and $O(n)$ on benign inputs — i.e.,
never asymptotically worse than sort, and hash-fast when data is well-behaved. In the
external-memory model this matches sort's $O(\frac{n}{B}\log_{M/B}\frac{n}{B})$ I/O bound as a
ceiling while approaching the $O(n/B)$ scan bound when partitioning succeeds. No tighter
*competitive* upper bound (small constant regret vs. the offline-best family) is known for the
fully online setting.

## 5. Lower Bound

Lower bounds combine **comparison/algebraic** and **online** arguments. (i) Sorting-based
methods inherit the $\Omega(n\log n)$ comparison lower bound and the external-memory
$\Omega(\frac{n}{B}\log_{M/B}\frac{n}{B})$ I/O bound (Aggarwal–Vitter, 1988). (ii) Set
intersection / join lower bounds: under SETH-style assumptions, certain join detection cannot
beat near-quadratic in worst case (cf. set-disjointness / OV). (iii) **Online:** any
deterministic selection policy that commits early can be forced into the wrong family by an
adversary that hides skew in the unseen suffix — giving an $\Omega(\text{ratio})$ competitive
lower bound that depends on how much of the input must be processed before $F_2$ is revealed.
This is why the problem is **open**: there is no algorithm with a proven small competitive
ratio against the offline-best family without statistics.

## 6. The Gap

We have robust *engineering* hybrids (cap-and-fall-back, G-join) that avoid catastrophe, and
we have asymptotic bounds for each family individually — but **no algorithm with a proven
worst-case regret guarantee for the online choice itself**. Closing the gap means either (a)
an online selection algorithm with bounded competitive ratio under adversarial skew, or (b) a
matching lower bound proving no statistics-free policy can be $o(\log n)$-competitive. Both are
open.

## 7. Current Research (as of June 2026)

- **Learned / runtime-feedback selection**: using cheap sketches (HyperLogLog for distinct
  counts, Count-Min for skew) computed on a prefix to drive the choice; integrates with
  runtime reoptimization. Active in the TUM, CWI, and MIT (Madden/Kraska) lines.
- **Unified degrade-gracefully operators** continuing Graefe's G-join program, now retargeted
  to vectorized/SIMD engines. *(frontier — verify)*
- **Skew-aware adaptive aggregation** that splits heavy hitters into a separate sort path while
  hashing the tail. *(frontier — verify)*

## 8. Future Work

- A competitive-analysis result (or impossibility) for statistics-free online hash-vs-sort.
- Co-design with spilling: the choice must be robust under dynamically shrinking memory.
- Tight integration with skew-resilient parallel scheduling so the per-partition choice and
  the load-balancing decision are made together.

## 9. Key References

- **[Foundational]** Selinger et al. *Access Path Selection in a Relational Database Management System.* SIGMOD 1979. — [DOI](https://doi.org/10.1145/582095.582099)
- **[Foundational]** Aggarwal, Vitter. *The Input/Output Complexity of Sorting and Related Problems.* CACM 1988. — [DOI](https://doi.org/10.1145/48529.48535)
- **[SOTA]** Graefe. *A Generalized Join Algorithm.* BTW 2011. — [DBLP](https://dblp.org/rec/conf/btw/Graefe11.html)
- **[Foundational]** Avnur, Hellerstein. *Eddies: Continuously Adaptive Query Processing.* SIGMOD 2000. — [DOI](https://doi.org/10.1145/342009.335420)
- **[SOTA]** Müller, Buchholz, et al. *Adaptive Aggregation on Modern Hardware.* (hash/sort runtime switching) *(unverified; the canonical hash-as-sort switching paper is Müller, Sanders, Lacurie, Lehner, Färber. Cache-Efficient Aggregation: Hashing Is Sorting. SIGMOD 2015 — [DOI](https://doi.org/10.1145/2723372.2747644))* — see also Schuh, Chen, Dittrich. *An Experimental Comparison of Thirteen Relational Equi-Joins in Main Memory.* SIGMOD 2016. — [DOI](https://doi.org/10.1145/2882903.2882917)

## 10. Worked Example

Group-by-aggregate over $n=10^8$ rows. Cache holds $M=4{\times}10^6$ entries.

**Case A — few groups.** $g=10^3$ distinct keys. The hash table (1000 slots) fits entirely in L2, so hash-aggregation runs at $\Theta(n)$ with essentially zero capacity misses: $\approx 10^8$ probes, all cache hits. Sort-aggregation would pay $\Theta(n\log n)\approx 10^8\times 27\approx 2.7{\times}10^9$ comparisons. **Hash wins.**

**Case B — many groups, skew hidden in the suffix.** $g=5{\times}10^7$ distinct keys, $g\gg M$. Now every hash probe misses cache: $\approx 10^8$ random misses at $\sim 100$ cycles $=10^{10}$ cycles. Sort-aggregation stays cache-friendly with external-memory I/Os $\Theta(\tfrac{n}{B}\log_{M/B}\tfrac{n}{B})$. **Sort wins.**

The trap: a policy that commits after sampling the first $10^6$ rows — which happen to contain only $200$ distinct keys — would pick hashing, then be ambushed when the remaining suffix explodes $g$ past $M$. This adversarial concealment of the $\ell_2$ moment $F_2=\sum_j f_j^2$ is exactly why a statistics-free online policy cannot guarantee small competitive ratio.

---
*Part of the [DBMS Research catalog](../../README.md).*
