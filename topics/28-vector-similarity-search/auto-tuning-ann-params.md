# Right-sizing index parameters automatically

> **Topic:** Vector Databases & Similarity Search · **ID:** `28-vector-similarity-search/auto-tuning-ann-params` · **Status:** empirically-open

## 1. Problem Statement
Every ANN index exposes parameters that trade build cost, memory, query latency, and recall: HNSW's graph degree $M$ and build beam $\mathit{efConstruction}$; the *query* beam $\mathit{efSearch}$; IVF's list count and probe count $n_{\text{probe}}$; PQ/quantization bit budgets. Practitioners hand-tune these per dataset and per SLO — slow, brittle, and dataset-specific. The problem: **automatically select the parameter vector $\theta=(M,\mathit{efConstruction},\mathit{efSearch},n_{\text{probe}},\text{bits},\dots)$ that meets a recall target $\rho$ at minimum cost** (latency, memory, or build time), for a given dataset and query distribution, ideally without exhaustively building many indexes.

Variants:
- **Decision:** is recall target $\rho$ achievable within budget $B$ (memory/latency) for this dataset?
- **Optimization (constrained):** $\min_\theta \mathrm{cost}(\theta)$ s.t. $\mathrm{recall}(\theta)\ge\rho$.
- **Query-time-only:** with the index fixed, choose $\mathit{efSearch}/n_{\text{probe}}$ — possibly *per query* — to hit recall at minimum work.
- **Online/adaptive:** retune as the data distribution drifts.

## 2. Mathematical Foundations
Treat $\mathrm{recall}(\theta)$ and $\mathrm{cost}(\theta)$ as unknown functions estimable only by *building and probing* an index (expensive, noisy black-box evaluations).

Key scaffolding:
- **Black-box / Bayesian optimization.** Recall–cost surfaces are smooth and largely monotone in most knobs (recall ↑ in $\mathit{efSearch},n_{\text{probe}},M$, cost ↑ too), making them amenable to Gaussian-process / bandit search; but build cost makes each sample costly, so *sample efficiency* is the crux.
- **Monotonicity / Pareto structure.** Many parameters induce a monotone recall–cost tradeoff; the feasible-at-$\rho$, minimum-cost point lies on the *Pareto frontier*. Query-time knobs ($\mathit{efSearch}$) are *anytime*-monotone (recall nondecreasing in work), enabling cheap 1-D calibration without rebuilding.
- **Generalization / sampling.** Estimating recall on a query *sample* of size $m$ gives a confidence interval of width $O(1/\sqrt m)$ (Hoeffding); per-dataset tuning is a learning problem with a generalization gap from train queries to deployment queries (distribution shift).
- **Cost models.** Analytic cost models (distance evals $\approx \mathit{efSearch}\cdot \bar{\deg}$ for graphs; $\approx n_{\text{probe}}\cdot \bar{|\text{list}|}$ for IVF) let some knobs be set analytically rather than by search.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** Vendor auto-tuners and recall-target APIs exist — e.g., parameter advisors in Milvus/pgvector/pgvectorscale and managed services that grid- or Bayesian-search a few configs and pick the cheapest meeting $\rho$ *(frontier — verify)*. ann-benchmarks publishes the empirical recall–QPS Pareto fronts that tuning targets. Query-time $\mathit{efSearch}/n_{\text{probe}}$ calibration to a recall target is standard and cheap.
- **Learned-tuner-SOTA:** Learned cost/recall predictors and learned query-difficulty estimators that set *per-query* search budgets are emerging in research and some engines *(frontier — verify)*. DB knob-tuning systems (OtterTune-style ML tuning; ML-based query optimizers) are the methodological ancestors.
- **Theory-SOTA:** essentially none — there is no proven sample complexity or regret bound for hitting a recall target on graph/IVF indexes.

## 4. Upper Bound
No problem-specific provable bound. Transferable guarantees: Bayesian optimization / Lipschitz black-box optimization gives convergence to a near-optimal $\theta$ with sample count growing with the (effective) parameter dimension; bandit/best-arm-identification gives $O(\log(1/\delta)/\Delta^2)$ samples to identify the cheapest config meeting $\rho$ with confidence $1-\delta$, where $\Delta$ is the cost gap. Query-time-only tuning is cheap: 1-D monotone search over $\mathit{efSearch}$ calibrates recall in $O(\log(1/\varepsilon))$ probes against a held-out query sample. These bound *the tuning procedure*, not index quality.

## 5. Lower Bound
- **Information-theoretic / sampling:** estimating recall to additive $\varepsilon$ with confidence $1-\delta$ needs $\Omega(\varepsilon^{-2}\log(1/\delta))$ query evaluations (matching Hoeffding) — an unavoidable measurement cost per candidate $\theta$.
- **Black-box hardness:** without structural assumptions (monotonicity/Lipschitz), finding the cost-minimal feasible $\theta$ over a $p$-dimensional grid of size $g$ requires $\Omega(g^p)$ evaluations in the worst case — the combinatorial barrier that motivates exploiting monotonicity.
- **Distribution shift:** any tuner has irreducible error when deployment queries differ from the tuning sample; no finite sample certifies recall under arbitrary shift (a generalization lower bound).

## 6. The Gap
Open in theory, maturing in practice. Empirically, monotonicity and analytic cost models make tuning tractable and vendors ship advisors; but there is no proven sample complexity for *jointly* setting build-time knobs ($M,\mathit{efConstruction}$, bits) under expensive rebuilds, no regret guarantee robust to query drift, and no agreed benchmark for *auto-tuning quality* (vs. an oracle). Closing it needs (i) exploiting recall monotonicity to prove sample-efficient joint tuning, and (ii) drift-robust recall certification.

## 7. Current Research (as of June 2026)
Active directions: learned recall/cost predictors that avoid full rebuilds by extrapolating from cheap proxies *(frontier — verify)*; per-query adaptive $\mathit{efSearch}/n_{\text{probe}}$ via query-difficulty models *(frontier — verify)*; constrained Bayesian optimization specialized to monotone recall–cost surfaces; and "recall-target" first-class APIs in vector DBs. Methodological roots in ML-based DB knob tuning (Pavlo/CMU OtterTune lineage) and learned query optimization. Contributors: vector-DB vendors, the ann-benchmarks community, and DB+ML systems labs.

## 8. Future Work
- Sample-complexity / regret bounds for joint build+query tuning under expensive rebuilds.
- Drift-robust online retuning with recall guarantees.
- Transferable tuners that warm-start from dataset descriptors (intrinsic dimension, scale).
- Standard auto-tuning benchmark measuring distance-to-oracle Pareto frontier.

## 9. Key References
- **[Foundational]** Y. Malkov, D. Yashunin. *Efficient and Robust Approximate Nearest Neighbor Search using HNSW graphs.* IEEE TPAMI, 2020 (arXiv:1603.09320).
- **[Foundational]** H. Jégou, M. Douze, C. Schmid. *Product Quantization for Nearest Neighbor Search.* IEEE TPAMI, 2011.
- **[SOTA]** D. Van Aken, A. Pavlo, G. J. Gordon, B. Zhang. *Automatic Database Management System Tuning Through Large-scale Machine Learning (OtterTune).* SIGMOD, 2017.
- **[Foundational]** B. Shahriari, K. Swersky, Z. Wang, R. P. Adams, N. de Freitas. *Taking the Human Out of the Loop: A Review of Bayesian Optimization.* Proceedings of the IEEE, 2016.
- **[SOTA]** M. Aumüller, E. Bernhardsson, A. Faithfull. *ANN-Benchmarks: A Benchmarking Tool for Approximate Nearest Neighbor Algorithms.* Information Systems, 2020.
- **[SOTA]** S. J. Subramanya, et al. *DiskANN: Fast Accurate Billion-point Nearest Neighbor Search on a Single Node.* NeurIPS, 2019.

---
*Part of the [DBMS Research catalog](../../README.md).*
