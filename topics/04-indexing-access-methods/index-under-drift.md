# Index maintenance under schema/data drift

> **Topic:** Indexing & Access Methods · **ID:** `04-indexing-access-methods/index-under-drift` · **Status:** empirically-open

## 1. Problem Statement
**Learned and adaptive indexes** replace or augment B-trees with models that map a key to its position (or to a page), trading branch traversals for model inference. Their accuracy depends on the **key distribution** $F$. The problem: keep such an index **accurate and cheap as the data drifts** — inserts/deletes shift $F$ (data drift) or the schema/key semantics change (schema drift) — without full rebuilds. Concretely, bound the **prediction error** (last-mile search window) and amortized **maintenance cost** under a stream of updates while query latency stays competitive. Variants: the **detection** variant (decide when drift has degraded the model enough to act), the **repair/retrain** variant (minimize cost to restore an error target), and the **stability-vs-accuracy** variant (trade model freshness against rebuild cost). It is *empirically open*: many systems exist, but there is no agreed theory predicting when a learned index beats a B-tree under drift, nor an optimal maintenance policy.

## 2. Mathematical Foundations
A learned index models the **CDF** $F$: predicted position $\hat{p}(x)=N\cdot \hat{F}(x)$, and the search cost is governed by the **max prediction error** $\Delta = \max_x |\hat F(x)-F(x)|\cdot N$, since the engine binary/exponential-searches a window of size $O(\Delta)$. For **piecewise-linear (PGM/spline)** models, $\Delta$ is a tunable error parameter $\varepsilon$ giving $O(\log_{N/\varepsilon} N)$ levels and provable worst-case search $O(\log \varepsilon + \log\log N)$. Drift is formalized as a change in $F$ over time, measured by statistical distance (KS-statistic $\sup_x|F_t(x)-F_{t_0}(x)|$, or Wasserstein $W_1$); the model's error inflates roughly with this distance. Online-learning regret and **concept-drift** theory (Gama et al.) supply detection bounds; the trade-off resembles a **competitive/MWU** problem: choose retrain times to minimize $\sum(\text{staleness cost} + \text{retrain cost})$ against an adversarial drift sequence. VC/PAC bounds limit how few samples certify the post-drift error.

## 3. State of the Art (SOTA)
- **Foundational:** **RMI** — *The Case for Learned Index Structures* (Kraska, Beutel, Chi, Dean, Polyzotis, SIGMOD 2018), read-only.
- **Updatable learned indexes:** **ALEX** (Ding et al., SIGMOD 2020) — gapped arrays + adaptive model nodes for inserts; **PGM-index** (Ferragina–Vinciguerra, VLDB 2020) — worst-case-optimal piecewise-linear, with a dynamic variant; **LIPP** (Wu et al., VLDB 2021) — precise positions, no last-mile search; **FITing-tree** (Galakatos et al., SIGMOD 2019); **APEX** (persistent-memory learned index).
- **Benchmarks/empirical:** **SOSD** and **GRE** (Wongkham et al., VLDB 2022) benchmark updatable learned indexes vs. B-trees/ART under insert-heavy and shifting workloads, showing learned indexes can degrade sharply under adversarial/append patterns.
- **Adaptive (non-learned):** **Database Cracking** (Idreos, Kersten, Manegold, CIDR 2007) and **adaptive merging** — indexes built incrementally from the query workload, a different "drift = workload" lens.

## 4. Upper Bound
The **PGM-index** gives a clean upper bound: for error parameter $\varepsilon$, it occupies space adapting to the data's "linear approximability," answers queries in $O(\log_{2\varepsilon} N)$ I/Os in the EM model with worst-case guarantees *independent of distribution*, and supports updates in the dynamic variant with $O(\log N)$ amortized cost. ALEX/LIPP give strong **empirical** insert performance with bounded local error via node splits/expansions. Cracking gives $O(N)$ total work amortized over the first queries that touch a region. These are the best guarantees under updates; PGM's worst-case bound is the strongest distribution-robust one.

## 5. Lower Bound
Predecessor/range search inherits the **cell-probe** lower bound $\Omega(\log_w N/\log\log N)$ (Pătrașcu–Thorup, STOC 2006), which learned indexes cannot beat in the worst case — confirming that with adversarial distributions a learned index degrades to comparison-search cost. For **drift detection**, online concept-drift has information-theoretic limits: distinguishing a distribution shift of statistical distance $\delta$ requires $\Omega(1/\delta^2)$ samples, lower-bounding detection latency. No specific super-constant lower bound separates learned from B-tree maintenance cost *under drift*; the hardness is the adversarial-distribution worst case plus detection sample complexity.

## 6. The Gap
The gap is between **strong worst-case guarantees** (PGM) and **strong empirical average-case wins** (ALEX/LIPP/RMI) on the one hand, and the **absence of a predictive theory of maintenance under drift** on the other. We lack: (i) a model that says, given a drift process, when retrain/rebuild beats incremental repair; (ii) an optimal (or competitive) online retraining policy with proven guarantees; (iii) a characterization of which distributions/drift regimes make learned indexes robustly better than B-trees/ART. So this is empirically open: systems work, but the cost/benefit boundary under drift is not theoretically pinned down.

## 7. Current Research (as of June 2026)
Active: **drift-aware, self-tuning learned indexes** that monitor error and trigger localized retraining; **updatable benchmarks** (GRE/SOSD extensions) stress-testing adversarial and time-evolving workloads; integration of learned indexes into real engines and LSM trees (e.g., learned LSM, *Bourbon*); and **online-learning-theoretic** retrain policies *(frontier — verify)*. Groups: Kraska/Marcus (MIT, learned systems and *self-driving DBMS* lineage with Pavlo/CMU), Ferragina–Vinciguerra (Pisa, PGM), Idreos (Harvard, adaptive/cracking and the *data-structure design space*), Athanassoulis (BU). Open debate on reproducibility and on whether learned indexes pay off once update cost is counted.

## 8. Future Work
- A competitive online policy for retrain-vs-repair under adversarial drift, with proven ratio.
- Predictive model linking drift magnitude ($W_1$/KS) to required maintenance cost and error.
- Robust worst-case-and-adaptive hybrids (PGM-style guarantees + ALEX-style update speed).
- Schema-drift handling (key re-encoding, multi-column/correlated drift).
- Unified evaluation tying into a general access-method cost model (see `access-method-cost-model`).

## 9. Key References
- **[Foundational]** T. Kraska, A. Beutel, E. H. Chi, J. Dean, N. Polyzotis. *The Case for Learned Index Structures.* SIGMOD, 2018.
- **[SOTA]** P. Ferragina, G. Vinciguerra. *The PGM-index: A Fully-Dynamic Compressed Learned Index with Provable Worst-Case Bounds.* VLDB, 2020.
- **[SOTA]** J. Ding, U. F. Minhas, J. Yu, C. Wang, et al. *ALEX: An Updatable Adaptive Learned Index.* SIGMOD, 2020.
- **[SOTA]** C. Wongkham, B. Lu, C. Liu, Z. Zhong, E. Lo, T. Wang. *Are Updatable Learned Indexes Ready? (GRE benchmark).* VLDB, 2022.
- **[Foundational]** S. Idreos, M. L. Kersten, S. Manegold. *Database Cracking.* CIDR, 2007.
- **[Foundational]** M. Pătrașcu, M. Thorup. *Time–Space Trade-Offs for Predecessor Search.* STOC, 2006.
- **[Survey]** J. Gama, I. Žliobaitė, A. Bifet, M. Pechenizkiy, A. Bouchachia. *A Survey on Concept Drift Adaptation.* ACM Computing Surveys, 2014.

---
*Part of the [DBMS Research catalog](../../README.md).*
