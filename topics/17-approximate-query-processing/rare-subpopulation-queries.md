# Rare Subpopulation and Outlier Queries

> **Topic:** Approximate Query Processing · **ID:** `17-approximate-query-processing/rare-subpopulation-queries` · **Status:** open

## 1. Problem Statement
Answer aggregates over **tiny, highly selective subpopulations** — e.g. `SELECT AVG(amount) FROM T WHERE country='Tuvalu' AND fraud=true` — where the matching rows are a vanishing fraction of $T$ and a uniform sample of feasible size contains **few or zero** of them. Such queries include needle-in-haystack predicates, conjunctions of selective filters, and **outlier/extreme-value** aggregates (`MAX`, top-k, heavy hitters within a sliver). Formally: given selectivity $s=|\sigma_P(T)|/N \ll 1$, estimate $\theta=\text{AGG}(\sigma_P(T))$ to relative error $\epsilon$ with confidence $1-\delta$ under a space/time budget. Variants: **decision** (does the subpopulation satisfy `COUNT`$>\tau$ or contain an outlier?), **counting** (estimate $|\sigma_P(T)|$), **optimization** (estimate the aggregate value). The defining obstacle: uniform sampling's effective sample for the subpopulation is $\approx n\cdot s$, so error scales as $1/\sqrt{ns}$ — uncontrollable as $s\to 0$.

## 2. Mathematical Foundations
A uniform sample of size $n$ yields effective subpopulation size $n_s\sim\text{Binomial}(n,s)$, with $\mathbb E[n_s]=ns$ and $\Pr[n_s=0]=(1-s)^n\approx e^{-ns}$. Any HT estimate has relative standard error $\Theta(1/\sqrt{ns})$, so *uniform sampling is provably hopeless* for $s\ll 1/n$. Mitigations rest on **importance / measure-biased sampling** (oversample likely-matching rows if $P$ is anticipated), **outlier-indexed AQP** (separate the heavy/rare tail into an exact "outlier index" and sample only the body — the AQP++ / outlier-aware design), and **sketches** that preserve heavy hitters: **Count-Min** ($\epsilon\|f\|_1$ error in $O(\epsilon^{-1}\log\delta^{-1})$ space) and **Count-Sketch** ($\ell_2$ guarantee) recover frequent items but not arbitrary selective conjunctions. For unknown predicates, no precomputed bias helps — connecting to a fundamental **information barrier**. Extreme-value queries additionally violate bootstrap consistency, so even CIs are not sample-derivable.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** **Outlier-indexed AQP** (Chaudhuri, Das, Datar, Motwani, Narasayya — *Overcoming Limitations of Sampling for Aggregation Queries*, ICDE 2001) — store outliers exactly, sample the rest; **AQP++ / Sample+Seek** (Ding et al., SIGMOD 2016) — index + measure-biased sample to bound error for selective predicates; **stratified samples** keyed on rare-value columns; heavy-hitter sketches (Count-Min, SpaceSaving) for frequent-item subpopulations.
- **Theory-SOTA:** Charikar–Chaudhuri–Motwani–Narasayya distinct-value/rare-value lower bounds; Cormode–Muthukrishnan Count-Min and Misra–Gries / SpaceSaving heavy-hitter guarantees as the provable backbone for known frequent subpopulations.

## 4. Upper Bound
With an **outlier index** capturing the rare/heavy contribution exactly and a uniform sample of the residual, relative error is bounded by $O(1/\sqrt n)$ *independent of $s$* for the indexed predicates (Chaudhuri et al. ICDE 2001). Sample+Seek gives $\epsilon$ relative error with $\tilde O(1/\epsilon^2)$ sample+index space for predicates the index supports. Heavy-hitter sketches answer "is this a heavy subpopulation" in $O(\epsilon^{-1}\log N)$ space with $\epsilon\|f\|_1$ additive error.

## 5. Lower Bound
**Information-theoretic, unconditional:** for an *arbitrary, unknown* selective predicate with selectivity $s$, any sampling estimator needs $\Omega(1/s)$ samples merely to observe one matching row in expectation, so bounded-relative-error estimation requires $\Omega(1/(s\epsilon^2))$ samples — unbounded as $s\to0$. Estimating $|\sigma_P(T)|$ to constant factor from a sample is $\Omega(N)$ in the worst case (Charikar et al., PODS 2000). For extreme-value/`MAX` queries, sample-derived CIs are provably inconsistent (Bickel–Götze–van Zwet). These hold regardless of computation — the barrier is purely about which rows the sample observes.

## 6. The Gap
**Genuinely open.** For *known/anticipated* selective predicates, outlier-indexing and measure-biased sampling close the gap to $O(1/\sqrt n)$. For *ad-hoc, unknown* selective predicates the lower bound $\Omega(1/s)$ is unbeatable by any sample — so the only path is auxiliary structures (indexes, sketches, exact tail stores), and the open question is how to cover *exponentially many possible* selective conjunctions within a budget. No method gives bounded relative error for arbitrary unknown rare subpopulations without per-predicate precomputation.

## 7. Current Research (as of June 2026)
Directions: learned predicate-importance sampling that predicts which rare regions future queries hit; hybrid exact-tail + sampled-body engines; subpopulation-aware sketches; LLM/workload forecasting to pre-stage likely rare predicates; differentially private rare-subpopulation answering (where privacy *also* suppresses small groups, compounding the problem). Groups: Surajit Chaudhuri / Bolin Ding (MSR/Alibaba), Graham Cormode (sketches), Barzan Mozafari (Keebo). *(frontier — verify)* learned importance samplers claiming bounded error on unanticipated rare conjunctions over cloud-warehouse traces.

## 8. Future Work
Budgeted coverage of exponentially many selective conjunctions; provable guarantees for unanticipated rare predicates via adaptive indexing; unifying outlier indexes with sketches and samples under one error model; private rare-subpopulation estimation with utility floors.

## 9. Key References
- **[Foundational]** Chaudhuri, Das, Datar, Motwani, Narasayya. *Overcoming Limitations of Sampling for Aggregation Queries.* ICDE 2001.
- **[Foundational]** Charikar, Chaudhuri, Motwani, Narasayya. *Towards Estimation Error Guarantees for Distinct Values.* PODS 2000.
- **[SOTA]** Ding, Huang, Chaudhuri, Chakkappen, Zhou. *Sample + Seek: Approximating Aggregates with Distribution Precision Guarantee.* SIGMOD 2016.
- **[Foundational]** Cormode, Muthukrishnan. *An Improved Data Stream Summary: The Count-Min Sketch and its Applications.* J. Algorithms, 2005.
- **[Foundational]** Metwally, Agrawal, El Abbadi. *Efficient Computation of Frequent and Top-k Elements in Data Streams (SpaceSaving).* ICDT 2005.

---
*Part of the [DBMS Research catalog](../../README.md).*
