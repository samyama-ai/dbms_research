# Hot/Cold Classification with Bounded Misclassification

> **Topic:** Storage & Buffer Management · **ID:** `07-storage-buffer/hot-cold-classification` · **Status:** open

## 1. Problem Statement

A tiered store places each page on fast tier (DRAM/NVM) or slow tier (SSD/disk). An online classifier must label pages **hot** (keep fast) or **cold** (demote) from an unbounded request stream with shifting access skew. A misclassification costs: labeling a truly hot page cold incurs repeated promotion/miss latency; labeling a truly cold page hot wastes scarce fast capacity. The goal is an online policy that **bounds the regret / misclassification cost** relative to the best decision in hindsight (or relative to an offline optimum that knows future accesses), under a fast-tier capacity budget $k$.

Variants:
- **Decision:** Is there a labeling achieving total cost $\le B$ offline? (Reduces to $k$-server/paging-style optimal eviction.)
- **Online optimization:** Minimize competitive ratio / regret under distribution shift.
- **Bounded-misclassification:** Achieve $\le \epsilon$ false-hot + false-cold rate with minimal sample/space, treating it as online binary classification with delayed, cost-weighted feedback.

## 2. Mathematical Foundations

Two lenses:

**(a) Competitive eviction.** Offline-optimal demotion is Bélády's MIN under a capacity constraint; the online version is **paging/$k$-server**, with deterministic ratio $k$ and randomized $\Theta(\log k)$ (marking algorithms, Fiat et al.).

**(b) Online learning with shift.** Treat each page's hotness as a label from a drifting distribution $D_t$. The frequency/recency signal is a feature; the classifier is an online predictor with **regret** $R_T = \sum_t \ell_t(\hat y_t) - \min_{h\in\mathcal H}\sum_t \ell_t(h)$. Under **adversarial drift**, track-the-best (Fixed-Share / shifting experts, Herbster–Warmuth) gives regret $O(\sqrt{T(k\log n + S\log T)})$ for $S$ switches. Sketches (Count-Min, Space-Saving) estimate frequencies in $O(1/\epsilon)$ space with $\pm\epsilon N$ error, bounding the feature error that propagates to misclassification.

The cost is asymmetric: let $c_h$ = penalty for false-cold, $c_c$ = penalty for false-hot; the Bayes-optimal threshold is $\Pr[\text{hot}] \ge c_c/(c_h+c_c)$, but $\Pr[\text{hot}]$ is non-stationary.

## 3. State of the Art (SOTA)

**Systems-SOTA.** Hekaton/SQL Server **Siberia** (Levandoski et al., ICDE 2013) — offline access-frequency-based hot/cold classification with logging-based sampling. **Anti-caching** (DeBrabant et al., VLDB 2013), **Project Siberia**, LRU-K (O'Neil et al., SIGMOD 1993), ARC (Megiddo–Modha, FAST 2003), and learned admission (**LRB/Cache Replacement via Belady-imitation**, Song et al., NSDI 2020) are the practical state. Modern NVM/SSD tiering uses access-counter + decay heuristics (e.g., **TMTS / Memtis**, page-temperature sampling).

**Theory-SOTA.** No policy provably bounds asymmetric misclassification cost under arbitrary skew shift; the closest guarantees are paging competitiveness and shifting-experts regret, applied separately.

## 4. Upper Bound

- **Caching framing:** randomized marking is $O(\log k)$-competitive; deterministic $k$-competitive (standard paging model).
- **Learning framing:** Fixed-Share / shifting experts achieve regret $\tilde O(\sqrt{ST})$ against the best sequence with $S$ shifts; learning-augmented caching (predictions) attains consistency $1+O(\eta)$ and robustness $O(\log k)$ simultaneously (Lykouris–Vassilvitskii; Rohatgi).
- **Frequency estimation:** Space-Saving gives top-$k$ hot detection in $O(k)$ space with deterministic error guarantee — bounding false-hot/false-cold from estimation error.

## 5. Lower Bound

- Online paging: deterministic $\Omega(k)$, randomized $\Omega(\log k)$ (Fiat, Karp, Luby, McGeoch, Sleator, Young).
- Shifting-experts regret: $\Omega(\sqrt{ST})$ is tight under adversarial shifts.
- **Frequency lower bound:** distinguishing hot from cold to additive $\epsilon N$ needs $\Omega(1/\epsilon)$ space (streaming, communication-complexity reduction).
- No known matching lower bound for the **asymmetric-cost, capacity-constrained, drifting** objective as a single quantity — that combination is the open part.

## 6. The Gap

Each component (competitive eviction, shifting regret, streaming frequency) is tightly bounded in isolation. The **open gap** is a unified bound on *asymmetric misclassification cost under bounded distribution shift with a hard capacity*: no algorithm provably ties false-hot and false-cold penalties to a single regret/competitive quantity, and no lower bound forbids it. Closing it requires a model coupling capacity-constrained eviction with cost-sensitive online classification and a matching impossibility.

## 7. Current Research (as of June 2026)

- **Learned caching/tiering:** Belady-imitation and RL admission extended to multi-tier with cost-sensitive loss (Stanford/MIT/Google). *(frontier — verify)* on regret guarantees under shift.
- **Tiered-memory OS/DB co-design:** CXL tiering, Memtis-style hotness sampling with statistical error bounds. *(frontier — verify)*
- **Robust online classification:** bounded-misclassification guarantees under covariate shift applied to page temperature. *(frontier — verify)*

## 8. Future Work

- A single competitive/regret bound for asymmetric-cost tiering under $S$-bounded skew shifts.
- Sample- and space-optimal hotness sketches with provable false-hot/false-cold rates.
- Learning-augmented tiering with robustness when predictions degrade during shift.
- Energy-/endurance-aware classification (write amplification on flash as a third cost).

## 9. Key References

- **[Foundational]** O'Neil, O'Neil, Weikum. *The LRU-K Page Replacement Algorithm.* SIGMOD, 1993.
- **[Foundational]** Megiddo, Modha. *ARC: A Self-Tuning, Low Overhead Replacement Cache.* FAST, 2003.
- **[SOTA]** Levandoski, Larson, Stoica. *Identifying Hot and Cold Data in Main-Memory Databases (Siberia).* ICDE, 2013.
- **[SOTA]** Song, Berger, Li, Lloyd. *Learning Relaxed Belady for Content Distribution Network Caching (LRB).* NSDI, 2020.
- **[Foundational]** Herbster, Warmuth. *Tracking the Best Expert.* Machine Learning, 1998.
- **[Survey]** Metwally, Agrawal, El Abbadi. *Efficient Computation of Frequent and Top-k Elements (Space-Saving).* ICDT, 2005.

---
*Part of the [DBMS Research catalog](../../README.md).*
