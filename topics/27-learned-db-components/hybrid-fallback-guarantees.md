# Guaranteed Fallback and Hybrid Designs

> **Topic:** Learned Database Components · **ID:** `27-learned-db-components/hybrid-fallback-guarantees` · **Status:** partially-solved

## 1. Problem Statement
Learned components (indexes, cardinality estimators, schedulers) typically optimize *average-case* behavior on a training distribution but offer no guarantees off-distribution. The hybrid-fallback problem asks: can we wrap a learned fast path in an architecture that **provably preserves the worst-case bounds of a classical structure**, while retaining the learned model's expected-case speedups?

Concretely, let $\mathcal{L}$ be a learned predictor (e.g., a model mapping a key to a predicted position) and $\mathcal{C}$ a classical structure (e.g., a B-tree) with worst-case guarantee $W$. The design goal is a composite $\mathcal{H}(\mathcal{L},\mathcal{C})$ such that:
- **(Safety)** Every operation on $\mathcal{H}$ costs $O(W)$ in the worst case, regardless of $\mathcal{L}$'s error.
- **(Speed)** When $\mathcal{L}$ is accurate, expected cost is $o(W)$ (e.g., $O(1)$ amortized).

Variants: the *decision* variant (does a given hybrid preserve bound $W$?), the *optimization* variant (minimize expected cost subject to a hard worst-case constraint), and the *space* variant (achieve the above within $(1+\varepsilon)$ of the classical structure's space).

## 2. Mathematical Foundations
The canonical example is the **learned index**. A monotone key array of size $n$ is summarized by a model $f$ predicting position; the realized error $\varepsilon_i = |f(k_i) - \mathrm{rank}(k_i)|$ bounds a local search window. If $\max_i \varepsilon_i \le \varepsilon$, lookup is $O(\log \varepsilon)$ via binary search inside the window. The **PGM-index** makes this rigorous: it builds a piecewise-linear $\varepsilon$-approximation in optimal $O(n)$ time and $O(m)$ segments, where $m$ is minimal, giving a recursive structure with provable $O(\log n)$ worst case *and* tunable $\varepsilon$.

Key formal tools:
- **Piecewise-linear approximation (PLA):** minimal number of segments with error $\le\varepsilon$ computable greedily via the convex-hull / streaming algorithm of O'Rourke.
- **Competitive analysis:** treat the learned path as an "advice" oracle; the *algorithms-with-predictions* framework gives bounds parameterized by prediction error $\eta$:
$$\mathrm{cost} \le \min\big(\alpha\cdot \mathrm{OPT} + \beta\cdot\eta,\ \gamma\cdot\mathrm{OPT}\big),$$
combining **consistency** (good when $\eta\to0$) and **robustness** (worst-case $\gamma$ guaranteed).
- **Monotonicity / order-preservation** as the structural invariant the classical fallback enforces.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** The **PGM-index** (Ferragina–Vinciguerra, VLDB 2020) provides worst-case $O(\log n)$ with learned speedups and bounded space — the strongest guaranteed-fallback learned index. **ALEX** (Ding et al., SIGMOD 2020) and **LIPP** add update support with bounded probe depth. **RadixSpline** offers single-pass builds.
- **Theory-SOTA:** The **algorithms-with-predictions** program (Lykouris–Vassilvitskii; Mitzenmacher–Vassilvitskii survey) formalizes consistency/robustness trade-offs and yields hybrids with provable Pareto guarantees for caching, scheduling, and ski-rental that map onto DB components.

## 4. Upper Bound
For lookups on $n$ sorted keys, the PGM-index achieves **worst-case $O(\log n)$ query time** and $O(m)$ space (model RAM, comparison model), with expected $O(\log\log n)$ or better under smooth key distributions. In the predictions framework, learned-augmented data structures achieve $(1+\varepsilon)$-consistency and $O(1)$-robustness simultaneously, i.e., the classical bound is never asymptotically exceeded. These are matched constructions, so the *guarantee-preservation* upper bound is essentially tight for the indexing case.

## 5. Lower Bound
Lower bounds come from the underlying classical problem: predecessor search in the **cell-probe model** requires $\Omega(\log n / \log\log n)$ (Pătraşcu–Thorup) for near-linear space, so no hybrid can beat this worst-case for general key sets — the fallback bound is intrinsic. For algorithms-with-predictions, there are **Pareto lower bounds**: improving consistency below a threshold provably degrades robustness (Wei–Zhang), meaning a hybrid cannot be simultaneously optimally fast *and* optimally safe. No fabricated tighter bound is claimed.

## 6. The Gap
For **static learned indexes**, the gap is essentially closed: PGM matches cell-probe lower bounds while delivering learned speedups. The open part is **dynamic / multi-component** settings: under inserts, deletes, and adversarial drift, no construction simultaneously guarantees (i) worst-case update cost, (ii) worst-case query cost, and (iii) graceful learned speedup — current systems (ALEX/LIPP) give strong empirical results but weaker worst-case update guarantees. Extending consistency–robustness Pareto-optimality to *learned cardinality estimation* and *learned schedulers* remains genuinely open.

## 7. Current Research (as of June 2026)
Active directions: (a) provably-safe learned indexes under adversarial updates, extending PGM with deamortized rebuild; (b) applying algorithms-with-predictions to query optimization so a bad learned plan can never exceed a classical plan by more than a constant (*frontier — verify*); (c) "safe-by-construction" wrappers that monitor realized error online and switch to fallback when a confidence bound is violated. Groups: Ferragina–Vinciguerra (Pisa); Vassilvitskii / Mitzenmacher (predictions theory); Kraska / Alizadeh (MIT, learned systems).

## 8. Future Work
- Unified theory of hybrid bounds across *all* learned components, not just indexes.
- Deamortized, worst-case-optimal dynamic learned indexes.
- Robustness certificates that compose under joint learning of multiple components.
- Lower bounds specific to the *hybrid* (advice-augmented) model rather than the base problem.

## 9. Key References
- **[SOTA]** P. Ferragina, G. Vinciguerra. *The PGM-index: a fully-dynamic compressed learned index with provable worst-case bounds.* PVLDB, 2020. — [DOI](https://doi.org/10.14778/3389133.3389135)
- **[Foundational]** T. Kraska, A. Beutel, E. Chi, J. Dean, N. Polyzotis. *The Case for Learned Index Structures.* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3196909) · [arXiv](https://arxiv.org/abs/1712.01208)
- **[SOTA]** J. Ding et al. *ALEX: An Updatable Adaptive Learned Index.* SIGMOD, 2020. — [DOI](https://doi.org/10.1145/3318464.3389711) · [arXiv](https://arxiv.org/abs/1905.08898)
- **[Foundational]** T. Lykouris, S. Vassilvitskii. *Competitive Caching with Machine Learned Advice.* JACM, 2021 (ICML 2018). — [DOI](https://doi.org/10.1145/3447579) · [arXiv](https://arxiv.org/abs/1802.05399)
- **[Survey]** M. Mitzenmacher, S. Vassilvitskii. *Algorithms with Predictions.* CACM / Beyond the Worst-Case Analysis book chapter, 2020–2022. — [DOI](https://doi.org/10.1145/3528087) · [arXiv](https://arxiv.org/abs/2006.09123)
- **[Foundational]** M. Pătraşcu, M. Thorup. *Time-Space Trade-Offs for Predecessor Search.* STOC, 2006. — [DOI](https://doi.org/10.1145/1132516.1132551) · [arXiv](https://arxiv.org/abs/cs/0603043)

## 10. Worked Example

A learned index over $n=10^6$ sorted keys uses model $f$ to predict a key's position, then does local binary search in a window of size $2\varepsilon+1$ around the prediction.

**On-distribution.** Suppose the trained model has max error $\varepsilon=15$. Lookup cost $=\underbrace{1}_{\text{model eval}}+\underbrace{\lceil\log_2(2\cdot15+1)\rceil}_{\text{window search}}=1+5=6$ probes — versus a B-tree's $\lceil\log_2 10^6\rceil=20$ probes. A $\sim 3.3\times$ speedup.

**Adversarial / off-distribution.** A poisoned key shifts so $f$ mispredicts by $400{,}000$. Naively searching a window of $2\cdot 4\times10^5$ would be catastrophic. **Guaranteed fallback:** cap the window; if the key is not found within $\pm\varepsilon$, fall back to the classical B-tree path, costing $20$ probes. So worst-case stays $O(\log n)=20$ — never worse than the safe structure.

**Algorithms-with-predictions framing.** With prediction error $\eta=|f(k)-\mathrm{rank}(k)|$, cost $\le\min(1+\log(2\eta+1),\ \log n)$. This is $(1+\varepsilon)$-**consistent** (near-optimal as $\eta\to0$, the 6-probe case) and $O(1)$-**robust** (capped at the 20-probe B-tree bound), exactly the consistency/robustness Pareto guarantee.

---
*Part of the [DBMS Research catalog](../../README.md).*
