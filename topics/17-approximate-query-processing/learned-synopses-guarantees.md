# Learned Synopses with Guarantees

> **Topic:** Approximate Query Processing · **ID:** `17-approximate-query-processing/learned-synopses-guarantees` · **Status:** empirically-open

## 1. Problem Statement

Classical synopses (samples, histograms, wavelets, sketches) come with *worst-case* error guarantees that hold for any data and any query in a class. **Learned synopses** replace or augment them with ML models — density estimators, autoregressive models, mixtures, neural nets — that answer aggregates by integrating a learned distribution rather than scanning data, and empirically dominate classical synopses on accuracy-per-byte. The problem: **reconcile** the strong average-case accuracy of learned models with the *provable, per-query, worst-case error bounds* of classical synopses, so a learned synopsis can be deployed where correctness contracts (error SLOs, confidence intervals) are required.

Variants:
- **Calibration (estimation):** wrap a learned answer with a *valid* confidence interval.
- **Hybrid (optimization):** allocate space between a learned model and a classical "residual" synopsis to minimize worst-case error at fixed budget.
- **Verification (decision):** given a learned synopsis and a query, certify $|\hat A - A| \le \varepsilon$ without touching $R$ — generally impossible, motivating residual structures.

## 2. Mathematical Foundations

A learned synopsis approximates the data density $p(x)$ (or a conditional answer function) by $\hat p_\theta$. An aggregate becomes an integral:

$$\widehat{\texttt{SUM}}(\sigma_\theta) = N \int_{\theta(x)} g(x)\,\hat p_\theta(x)\,dx,$$

so error is governed by a divergence $D(p \,\|\, \hat p_\theta)$ (TV / KL / Wasserstein) between true and learned densities. Classical synopses bound error by *combinatorial/geometric* arguments (e.g. a histogram's error $\le$ total variation within buckets; a sketch's error $\le \varepsilon\|f\|_p$). Learned models bound error only through **generalization theory** — Rademacher/VC complexity, PAC bounds — which give *in-distribution average* guarantees, not the *per-query worst-case* guarantees AQP contracts need.

Bridging tools: **conformal prediction** converts any point predictor into a distribution-free interval with finite-sample coverage $1-\alpha$, *exchangeability* permitting; **residual/correction synopses** keep a classical sketch of $(f - \hat f_\theta)$ so the *sum* of a model and a worst-case-bounded residual inherits the worst-case bound. The core tension: a model trained on $R$ at time $t$ has *no* guarantee on a query whose answer depends on a measure-zero or out-of-distribution region — exactly where classical synopses still pay their $\varepsilon\|f\|_p$ cost.

## 3. State of the Art (SOTA)

- **Systems-SOTA:** **DeepDB** (Hilprecht et al., VLDB 2020) uses Relational Sum-Product Networks for AQP and cardinality estimation; **DBEst / DBEst++** (Ma & Triantafillou, SIGMOD 2019/2021) fits regression + density models per query template; **Naru / NeuroCard** (Yang et al., VLDB 2019/2020) deep autoregressive models for selectivity. **Thalamus / electricity-grid AQP** and **FACE** (normalizing-flow synopsis, Wang et al., VLDB 2021) push density-model AQP. These dominate empirically but ship *heuristic* error estimates.
- **Theory-SOTA:** there is, as yet, **no learned synopsis with a classical-style worst-case guarantee**; the closest principled results are conformalized/PAC wrappers and hybrid model-plus-residual designs that *inherit* the residual's bound (the residual, not the model, carries the proof).

## 4. Upper Bound

Hybrid construction yields the only honest worst-case bound: with a learned model plus a residual Count-Min/wavelet of width $w$, total error $\le \varepsilon\|f - \hat f\|_p$, which is **never worse** than the classical synopsis on $f$ and is *empirically* far better when the model captures most mass. Conformal wrappers give *valid* $1-\alpha$ intervals of data-dependent (typically small) width under exchangeability — an average-case-tight, worst-case-honest guarantee. No purely-learned synopsis is known to beat the classical $\Omega(\varepsilon^{-2})$-style space bound *with a proof*.

## 5. Lower Bound

Information-theoretic: any synopsis of size $s$ answering all queries in a class $\mathcal{Q}$ to error $\varepsilon$ must satisfy $s \ge \log_2(\\#\text{distinguishable answer profiles})$ — learning cannot beat this counting bound; a model is just a (clever) lossy code. For *adversarial* / out-of-distribution queries, **no** finite training set bounds worst-case error: an adversary perturbs $R$ in a region the model never saw, so any model-only estimator has unbounded worst-case error — an impossibility that forces residual access or distributional assumptions. Under distribution shift, conformal coverage guarantees provably break (exchangeability violated).

## 6. The Gap

The gap is **genuinely open and primarily empirical** (hence the status). Learned synopses *empirically* dominate classical ones by large margins, yet possess *no matching worst-case theory*; classical synopses have airtight worst-case bounds but lose on accuracy-per-byte. What would close it: (i) a learned synopsis whose architecture *provably* meets a classical $\varepsilon\|f\|_p$-style bound (not merely a residual bolted on); (ii) tight characterization of when model-plus-residual beats either alone as a function of data "learnability"; (iii) robust coverage under the realistic distribution shift of an evolving database.

## 7. Current Research (as of June 2026)

Active: **conformalized AQP** giving distribution-free intervals over learned estimators *(frontier — verify)*; **model-plus-residual** hybrids that provably dominate classical synopses; **PAC-style guarantees** for sum-product-network and normalizing-flow synopses; uncertainty-quantified learned cardinality estimators feeding the optimizer. Robustness to drift (retraining triggers, online calibration) is a hot subtopic, tied to the *Sample Maintenance Under Updates* problem. Groups: Kraska (MIT, learned data systems), Binnig/Hilprecht (TU Darmstadt, DeepDB), Triantafillou (Warwick, DBEst), Stoica/Yang (Berkeley, Naru/NeuroCard), Kossmann/Markl. The unifying open question — *can a learned synopsis carry a worst-case certificate?* — is being actively framed but not answered *(frontier — verify)*.

## 8. Future Work

- A learned synopsis architecture with an intrinsic (not bolted-on) worst-case error proof.
- Distribution-shift-robust conformal coverage for AQP under data updates.
- A theory of "learnability budget": when a learned model provably saves space over the information-theoretic classical bound for a given data distribution.
- Optimizer integration: propagating learned-synopsis uncertainty through query plans (links to AQP plan optimization).

## 9. Key References

- **[Foundational]** G. Cormode, M. Garofalakis, P. J. Haas, C. Jermaine. *Synopses for Massive Data.* Foundations and Trends in Databases, 2011. — [DOI](https://doi.org/10.1561/1900000004)
- **[SOTA]** B. Hilprecht, A. Schmidt, M. Kulessa, A. Molina, K. Kersting, C. Binnig. *DeepDB: Learn from Data, not from Queries!* VLDB, 2020. — [DOI](https://doi.org/10.14778/3384345.3384349) · [arXiv](https://arxiv.org/abs/1909.00607)
- **[SOTA]** Q. Ma, P. Triantafillou. *DBEst: Revisiting Approximate Query Processing Engines with Machine Learning Models.* SIGMOD, 2019. — [DOI](https://doi.org/10.1145/3299869.3324958)
- **[SOTA]** Z. Yang et al. *Deep Unsupervised Cardinality Estimation (Naru).* VLDB, 2019. — [DOI](https://doi.org/10.14778/3368289.3368294) · [arXiv](https://arxiv.org/abs/1905.04278)
- **[SOTA]** J. Wang, C. Chai, J. Liu, G. Li. *FACE: A Normalizing Flow based Cardinality Estimator.* VLDB, 2021. — [DOI](https://doi.org/10.14778/3485450.3485458)
- **[Foundational]** V. Vovk, A. Gammerman, G. Shafer. *Algorithmic Learning in a Random World (Conformal Prediction).* Springer, 2005. — [DOI](https://doi.org/10.1007/b106715)

## 10. Worked Example

Table $R$ has $N=1000$ rows; column $X$ takes values in $\{1,\dots,10\}$ with true counts $f=(50,50,50,50,50,50,50,50,300,300)$ — most mass piled on $X\in\{9,10\}$. Query: $\texttt{SELECT COUNT(*) WHERE } X=9$, true answer $A=300$.

A **learned synopsis** fits a density $\hat p_\theta$ and (say) over-smooths the spike, estimating $\hat p_\theta(9)=0.27$, so $\hat A=N\hat p_\theta(9)=270$ — error $30$, with no certificate.

**Model + residual.** Keep a Count-Min sketch of the residual $g = f - N\hat p_\theta$ over the 10 cells. Here $g(9)=300-270=30$. A CM sketch of width $w$ answers $\hat g(9)$ with error $\le \varepsilon\|g\|_1$ where $\varepsilon=e/w$. With $\|g\|_1=\sum_x|f(x)-N\hat p_\theta(x)|$; suppose the model is good elsewhere so $\|g\|_1=80$. Choosing $w=e/\varepsilon$ with $\varepsilon=0.05$ gives additive error $\le 0.05\cdot 80=4$. Final estimate $\hat A = 270 + \hat g(9) \in [296,304]$ — a *worst-case* bound the bare model could not give. The residual, not the model, carries the proof, illustrating Section 4's hybrid construction.

---
*Part of the [DBMS Research catalog](../../README.md).*
