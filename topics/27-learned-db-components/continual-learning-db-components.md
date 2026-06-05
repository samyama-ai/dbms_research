# Lifelong / Continual Learning for DB Components

> **Topic:** Learned Database Components · **ID:** `27-learned-db-components/continual-learning-db-components` · **Status:** open

## 1. Problem Statement

Databases are non-stationary: data is inserted/updated/deleted and the query workload shifts (new templates, seasonal patterns, schema changes). A learned component trained once becomes stale. **Continual (lifelong) learning for DB components** asks for models that *adapt online* to the current regime while *retaining* competence on past regimes that may recur — without paying full retraining cost and without **catastrophic forgetting** (where adapting to new data erases accuracy on old data the workload still touches).

- **Decision variant:** After absorbing a stream of updates/queries, does the component still meet an accuracy/latency SLO on both current and historical regimes?
- **Optimization variant:** Choose an update rule minimizing time-averaged regret over a drifting sequence subject to a per-update compute budget.
- **Stability/plasticity variant:** Balance *plasticity* (adapt fast to drift) against *stability* (don't forget recurring regimes) — the central tension.

## 2. Mathematical Foundations

Model the world as a sequence of tasks/regimes $T_1, T_2, \dots$ from distributions $\mathcal{D}_1, \mathcal{D}_2, \dots$. After training on $T_t$, **catastrophic forgetting** is the loss increase on an earlier task:

$$
\mathrm{Forget}_{t}(j) \;=\; \ell_{\mathcal{D}_j}(\theta_t) - \ell_{\mathcal{D}_j}(\theta_j), \qquad j < t,
$$

and the goal is small *average* loss $\frac{1}{t}\sum_{j\le t}\ell_{\mathcal{D}_j}(\theta_t)$. The clean theoretical frame is **online learning / regret**: minimize $\mathrm{Regret}_T = \sum_{t} \ell_t(\theta_t) - \min_\theta \sum_t \ell_t(\theta)$, with **dynamic regret** $\sum_t \ell_t(\theta_t) - \sum_t \ell_t(\theta_t^\*)$ against a *changing* comparator $\theta_t^\*$ — the right notion under drift. Online gradient methods achieve $O(\sqrt{T})$ static regret and $O(\sqrt{T(1+P_T)})$ dynamic regret where $P_T = \sum_t \|\theta_{t}^\* - \theta_{t-1}^\*\|$ is the **path length** of the optimum. Mitigations such as **EWC** (Kirkpatrick et al. 2017) add a Fisher-information penalty $\sum_i F_i(\theta_i - \theta^\*_{j,i})^2$ to keep parameters important for old tasks near their old values. Learnability under adversarial regime sequences is governed by the **Littlestone dimension**.

## 3. State of the Art (SOTA)

- **ML-SOTA:** regularization (EWC, Synaptic Intelligence), replay/rehearsal (store or generate past examples), and dynamic-architecture methods (progressive nets) for continual learning.
- **Systems-SOTA:** updatable learned indexes — **ALEX** (SIGMOD 2020), **PGM-index** (PVLDB 2020), **LIPP/FITing-tree** — adapt structure to inserts in-place with worst-case guarantees. For optimizers, **Bao** (SIGMOD 2021) does cheap *online* learning over a hint space, retraining continually from production feedback, which is the closest deployed continual-learning loop; **Balsa** (SIGMOD 2022) learns from execution feedback. Cardinality estimators with incremental/online updates (e.g. update-aware DeepDB variants) exist but forgetting under drift is not solved.

## 4. Upper Bound

For the structural side, updatable learned indexes give worst-case bounds while absorbing change: **PGM** supports updates with $O(\log n)$ amortized cost keeping $O(\log n)$ lookup (RAM model); **ALEX** gives expected $O(\log n)$ inserts/lookups under its model assumptions. For the learning side, online convex optimization yields $O(\sqrt{T})$ static regret and $O(\sqrt{T(1+P_T)})$ dynamic regret (online learning model) — so adaptation cost grows sublinearly with the stream when drift (path length $P_T$) is bounded. EWC-style methods bound forgetting empirically but lack tight guarantees on non-convex models.

## 5. Lower Bound

There is a **stability–plasticity impossibility**: with bounded model capacity and no stored history, *some* forgetting is unavoidable — fitting a new regime that conflicts with an old one must move shared parameters (an information-theoretic capacity argument; a fixed-size model cannot losslessly retain unboundedly many distinct regimes). In online learning, **dynamic regret is $\Omega(\sqrt{T(1+P_T)})$** in the worst case, so no continual learner can adapt for free when drift is large. Under fully adversarial regime sequences with unbounded Littlestone dimension, no-regret learning is impossible — i.e. there exist workloads on which any fixed-capacity component must perform badly somewhere.

## 6. The Gap

The gap: structural adaptation (updatable indexes) is essentially **solved** with worst-case bounds, but *model* adaptation for optimizers/estimators is **open** — there is no method with provable bounded forgetting *and* bounded per-update cost *and* fast plasticity for the non-convex models used in practice. Bao demonstrates a working continual loop but offers no forgetting guarantee. Closing the gap needs: drift-rate-aware retraining/replay policies with dynamic-regret bounds, capacity-aware forgetting analyses, and detection of *recurring* regimes to reuse past parameters.

## 7. Current Research (as of June 2026)

Directions: drift detection triggering selective replay/refit; replay buffers of representative past queries for estimators; parameter-isolation/adapters to protect recurring-regime competence; foundation-model estimators fine-tuned continually per-database, with open concerns about forgetting pretraining knowledge *(frontier — verify)*. Groups: Kraska/Marcus (online learned optimization), Kemper/Neumann (TUM, updatable estimation), Ferragina–Vinciguerra (dynamic learned indexes), and the continual-learning ML community (EWC lineage). Interest is rising in *workload-drift benchmarks* to actually measure forgetting in DB settings *(frontier — verify)*.

## 8. Future Work

- Dynamic-regret-bounded continual learners for cardinality estimation and join ordering.
- Capacity-aware forgetting theory tying model size to the number of retainable regimes.
- Cheap recurring-regime detection enabling parameter reuse instead of refit.
- Replay-buffer design for query workloads (which historical queries to keep).
- SLO-aware update schedulers under a fixed per-update compute budget.

## 9. Key References

- **[Foundational]** Kirkpatrick, Pascanu, Rabinowitz, et al. *Overcoming Catastrophic Forgetting in Neural Networks (EWC).* PNAS 2017.
- **[SOTA]** Ding, Minhas, Yu, et al. *ALEX: An Updatable Adaptive Learned Index.* SIGMOD 2020.
- **[SOTA]** Ferragina, Vinciguerra. *The PGM-index: a fully-dynamic compressed learned index.* PVLDB 2020.
- **[SOTA]** Marcus, Negi, Mao, et al. *Bao: Making Learned Query Optimization Practical.* SIGMOD 2021.
- **[Foundational]** Zinkevich. *Online Convex Programming and Generalized Infinitesimal Gradient Ascent.* ICML 2003.
- **[Foundational]** Littlestone. *Learning Quickly When Irrelevant Attributes Abound: A New Linear-threshold Algorithm.* Machine Learning, 1988.
- **[Survey]** Parisi, Kemker, Part, Kanan, Wermter. *Continual Lifelong Learning with Neural Networks: A Review.* Neural Networks, 2019.

---
*Part of the [DBMS Research catalog](../../README.md).*
