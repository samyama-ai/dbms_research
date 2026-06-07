---
id: 27-learned-db-components/training-serving-cost-amortization
title: "Training and Serving Cost Amortization"
topic: 27-learned-db-components
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Training and Serving Cost Amortization

> **Topic:** Learned Database Components · **ID:** `27-learned-db-components/training-serving-cost-amortization` · **Status:** empirically-open

## 1. Problem Statement

A *learned database component* (a learned index, cardinality estimator, query optimizer, knob tuner, or scheduler) replaces a hand-engineered heuristic with a model $f_\theta$ fit to data and/or workload. Unlike its classical counterpart, $f_\theta$ incurs a **one-time (or recurring) offline cost** $C_{\text{train}}$ to collect training data and fit/refit parameters, plus a **per-invocation inference cost** $C_{\text{inf}}$. The benefit is a per-query speedup $\Delta_q \ge 0$ versus the best classical baseline.

The amortization problem: *under what workload, data, and drift conditions is the total learned cost repaid by accumulated speedups before the model must be retrained?*

- **Decision variant:** Given a finite horizon of $N$ queries, decide whether deploying $f_\theta$ yields net positive savings.
- **Optimization variant:** Choose retraining cadence, model capacity, and which sub-decisions to learn to *maximize* net savings.
- **Counting/accounting variant:** Attribute realized speedup per query and amortize $C_{\text{train}}$ correctly across a non-stationary stream (the speedup itself decays as data drifts away from the training distribution).

This is empirically-open: there is no agreed cost model, and reported "wins" frequently exclude training/data-collection time.

## 2. Mathematical Foundations

Let the workload be a (possibly non-stationary) stream $q_1, q_2, \dots$ drawn from distributions $\mathcal{D}_1, \mathcal{D}_2, \dots$. Net savings over horizon $N$ with retraining set $R \subseteq \{1,\dots,N\}$:

$$
\mathrm{Net}(N) \;=\; \sum_{i=1}^{N}\big(\Delta_{q_i} - C_{\text{inf}}\big) \;-\; |R|\cdot C_{\text{train}}.
$$

The realized speedup degrades with distribution shift; model it as $\Delta_{q_i} = \Delta_0 - \lambda \cdot d\big(\mathcal{D}_{t(q_i)}, \mathcal{D}_{\text{train}}\big)$ where $d(\cdot)$ is a divergence (e.g. total variation or Wasserstein) and $\lambda$ a sensitivity constant. The **break-even horizon** is the smallest $N^\*$ with $\mathrm{Net}(N^\*) \ge 0$.

Retraining cadence selection under drift maps onto **online/competitive analysis** (ski-rental: pay $C_{\text{inf}}$ repeatedly vs. pay $C_{\text{train}}$ once to reset accuracy). The classic deterministic ski-rental gives a $2$-competitive policy and the randomized version $\frac{e}{e-1}\approx 1.58$; these bound how far an online retraining schedule can be from the offline optimum that knows the drift trajectory.

## 3. State of the Art (SOTA)

- **Systems-SOTA:** The original *Learned Index* (Kraska et al., SIGMOD 2018) reported lookup wins but separated build cost; **ALEX** (Ding et al., SIGMOD 2020) and **PGM-index** (Ferragina–Vinciguerra, VLDB 2020) made updates/builds cheap enough that amortization becomes plausible for read-heavy workloads. For optimizers, **Bao** (Marcus et al., SIGMOD 2021) explicitly targets *fast* online learning to keep $C_{\text{train}}$ small, while **Neo** (Marcus et al., VLDB 2019) needs hours of training. **Balsa** (Yang et al., SIGMOD 2022) reduces dependence on an expert optimizer for bootstrap data.
- **Theory-SOTA:** competitive analysis for "rent-or-buy"/caching gives principled retraining cadence bounds; algorithms-with-predictions frames learned components as warm starts whose worst case is protected by a classical fallback.

## 4. Upper Bound

Treating retrain-vs-pay as ski-rental yields a **2-competitive** deterministic retraining policy and a randomized $\frac{e}{e-1}$-competitive policy against the drift-aware offline optimum (online algorithms model). For amortized *build* cost, in-place learned indexes (ALEX, PGM) achieve $O(\log n)$ amortized insert and $O(\log n)$ lookup, matching B-tree asymptotics while reusing the model — so $C_{\text{train}}$ is paid down incrementally rather than as a lump.

## 5. Lower Bound

No nontrivial speedup is guaranteed in the worst case: if the workload is adversarial or the data has no exploitable regularity, $\Delta_q = 0$ and $\mathrm{Net}(N) = -\,|R| C_{\text{train}} - N C_{\text{inf}} < 0$ for all $N$. This is an **information-theoretic** floor — a model cannot extract structure that is not present (cf. no-free-lunch). Competitively, ski-rental admits a matching deterministic $2$ and randomized $\frac{e}{e-1}$ lower bound (online adversary model), so no retraining policy can do uniformly better without distributional assumptions.

## 6. The Gap

The gap is not an asymptotic complexity gap but a **modeling and measurement** gap: there is no standardized, drift-aware cost accounting that includes data collection, feature extraction, training, validation, and the decay of $\Delta_q$. Closing it requires (a) a benchmark protocol that reports end-to-end TCO including $C_{\text{train}}$, and (b) a drift model that predicts $N^\*$ from measurable workload statistics. Genuinely open empirically.

## 7. Current Research (as of June 2026)

Active directions: *algorithms-with-predictions* costing for learned components; cheap online learners (Bao-style) that shrink $C_{\text{train}}$; transfer/foundation models for cardinality estimation that amortize training across databases *(frontier — verify)*. Groups: Kraska/Marcus (MIT, ex-MIT), Kemper/Neumann (TUM), Ferragina–Vinciguerra (Pisa). There is growing emphasis on reporting "wins" net of training, pushed by the redbench/learned-component reproducibility community *(frontier — verify)*.

## 8. Future Work

- A canonical drift-aware amortization cost model with confidence intervals on $N^\*$.
- Auto-tuning of model capacity to *minimize* $C_{\text{train}} + N\,C_{\text{inf}}$ for a target accuracy.
- Multi-tenant amortization: share training across databases/instances.
- Online retraining triggers driven by measured divergence $d(\mathcal{D}_t,\mathcal{D}_{\text{train}})$ rather than fixed schedules.

## 9. Key References

- **[Foundational]** Kraska, Beutel, Chi, Dean, Polyzotis. *The Case for Learned Index Structures.* SIGMOD 2018. — [arXiv](https://arxiv.org/abs/1712.01208) — [DOI](https://doi.org/10.1145/3183713.3196909)
- **[SOTA]** Marcus, Negi, Mao, Tatbul, Kraska, et al. *Bao: Making Learned Query Optimization Practical.* SIGMOD 2021. — [DOI](https://doi.org/10.1145/3448016.3452838) — [DBLP](https://dblp.org/rec/conf/sigmod/MarcusNMTAK21.html)
- **[SOTA]** Ding, Minhas, Yu, et al. *ALEX: An Updatable Adaptive Learned Index.* SIGMOD 2020. — [arXiv](https://arxiv.org/abs/1905.08898) — [DOI](https://doi.org/10.1145/3318464.3389711)
- **[SOTA]** Ferragina, Vinciguerra. *The PGM-index: a fully-dynamic compressed learned index with provable worst-case bounds.* PVLDB 2020. — [DOI](https://doi.org/10.14778/3389133.3389135) — [DBLP](https://dblp.org/rec/journals/pvldb/FerraginaV20.html)
- **[Foundational]** Karlin, Manasse, Rudolph, Sleator. *Competitive Snoopy Caching* (ski-rental / rent-or-buy). Algorithmica 1988. — [DOI](https://doi.org/10.1007/BF01762111)
- **[Survey]** Mitzenmacher, Vassilvitskii. *Algorithms with Predictions.* Communications of the ACM, 2022. — [arXiv](https://arxiv.org/abs/2006.09123) — [DOI](https://doi.org/10.1145/3528087)

## 10. Worked Example

A learned cardinality estimator costs $C_{\text{train}}=2{,}000$ ms to collect data and fit, and $C_{\text{inf}}=0.2$ ms per query. On the current workload it saves $\Delta_0=3$ ms per query versus the histogram baseline (better plans). Net after $N$ queries, no retraining:

$$\mathrm{Net}(N)=N(\Delta_0-C_{\text{inf}})-C_{\text{train}}=N(3-0.2)-2000=2.8N-2000.$$

Break-even: $N^\*=\lceil 2000/2.8\rceil=715$ queries. Below that the learned component is a net loss.

Now add drift. Suppose the realized speedup decays as $\Delta_{q_i}=3-\lambda\,d_i$ with $\lambda=10$ and divergence growing $d_i=0.0005\,i$ (TV distance from the training distribution). The per-query net contribution hits zero when $3-0.2-10(0.0005\,i)=0\Rightarrow i=560$; past query $560$ each query *loses* money even though build cost is sunk. Cumulative net peaks around there, well before the static $N^\*=715$ is reached — so under this drift the model **never** breaks even and must be retrained earlier.

Retraining cadence as ski-rental: paying $C_{\text{inf}}$-degradation repeatedly vs. paying $C_{\text{train}}$ once to reset accuracy. The deterministic $2$-competitive rule retrains once accumulated degradation reaches $C_{\text{train}}=2000$ ms, guaranteeing total cost within $2\times$ the drift-aware offline optimum.

---
*Part of the [DBMS Research catalog](../../README.md).*
