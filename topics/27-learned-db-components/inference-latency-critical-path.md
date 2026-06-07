---
id: 27-learned-db-components/inference-latency-critical-path
title: "Inference Latency Inside the Critical Path"
topic: 27-learned-db-components
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Inference Latency Inside the Critical Path

> **Topic:** Learned Database Components · **ID:** `27-learned-db-components/inference-latency-critical-path` · **Status:** open
> **Verification note:** Segment-count figures below corrected from $O(n/\varepsilon^2)$ to $O(n/\varepsilon)$, matching the PGM-index bound of at most $n/(2\varepsilon)$ segments.

## 1. Problem Statement

A learned component delivers value only if its prediction $f_\theta(x)$ is *consumed* on the query execution path: a learned index predicts a position before a lookup; a learned cardinality estimator feeds the optimizer; a learned scheduler picks the next operator. The **critical-path latency problem** asks: can model inference be made cheap enough — per tuple, per operator, or per query — that the inference time $C_{\text{inf}}$ does not exceed the benefit $\Delta_q$ it enables?

Concretely, for a point lookup over $n$ keys, a B-tree costs $O(\log n)$ comparisons of a few nanoseconds each; a learned index must predict a position plus pay a (typically small) error-correction search. If $f_\theta$ is a deep network, the matrix multiplies can dwarf $O(\log n)$ pointer-chases, erasing the win.

- **Decision variant:** Given a latency budget $B$ per invocation, does there exist $\theta$ achieving target accuracy with $C_{\text{inf}}(\theta) \le B$?
- **Optimization variant:** Minimize end-to-end query latency $C_{\text{inf}} + (\text{cost after prediction})$ over model architecture.
- **Placement variant:** Decide *where* on the path (per-tuple vs. per-batch vs. per-query) to invoke the model to amortize fixed inference overhead.

## 2. Mathematical Foundations

Let a lookup pay prediction cost $C_{\text{inf}}$ plus error-correction proportional to the prediction error. For a piecewise-linear learned index with $\varepsilon$-bounded local error, lookup is $O(C_{\text{inf}} + \log \varepsilon)$ and the **PGM-index** attains worst-case $O(\log n)$ with space $O(n/\varepsilon)$ segments — a clean accuracy/latency/space frontier:

$$
\text{lookup time} = \underbrace{C_{\text{inf}}}_{\text{predict segment}} + \underbrace{O(\log \varepsilon)}_{\text{local search}}, \qquad \text{segments} = O\!\big(n/\varepsilon\big).
$$

Inference cost of a model with $L$ layers and width $w$ is $\Theta(L w^2)$ FLOPs; on the per-tuple path this must beat $\Theta(\log n)$ branch-predicted comparisons. The trade-off is governed by the **bias–capacity** tension: smaller $w$ lowers $C_{\text{inf}}$ but raises $\varepsilon$, which raises local-search cost. Batching of $b$ tuples amortizes fixed launch/dispatch overhead $O(\kappa)$ to $O(\kappa/b)$ per tuple (Amdahl-style), the central reason learned estimators are invoked per-query, not per-tuple.

## 3. State of the Art (SOTA)

- **Systems-SOTA:** **RMI** (Kraska et al., SIGMOD 2018) uses a tiny 2-stage model precisely to keep inference to a few multiply-adds. **PGM** and **RadixSpline** (Kipf et al., aiDM 2020) use a single linear model + radix table, making inference essentially branch-free. For optimizers, **Bao** (SIGMOD 2021) keeps inference to a small tree-CNN over a few plan candidates so it fits the planning budget; **NeuroCard/DeepDB** (PVLDB 2020) push cardinality inference to sub-millisecond via SPNs/autoregressive factorization.
- **Theory-SOTA:** algorithms-with-predictions gives latency-robust designs where the model is consulted once and a classical structure bounds the worst case.

## 4. Upper Bound

**PGM-index** achieves $O(\log n)$ worst-case lookup with $O(n/\varepsilon)$ space and constant-time model evaluation (RAM/word model), matching B-tree query asymptotics while typically winning constants on real key distributions. RadixSpline gives $O(1)$ expected model evaluation plus bounded local search. For optimizer-side inference, sub-millisecond per-query estimators (DeepDB, NeuroCard) keep $C_{\text{inf}}$ below typical planning time for OLAP queries.

## 5. Lower Bound

Any comparison-based ordered lookup needs $\Omega(\log n)$ in the worst case (comparison model); in the **cell-probe model**, predecessor search on $n$ keys in $u$-universe requires $\Omega(\log n / \log\log n)$ probes (Pătrașcu–Thorup, 2006), so a learned index cannot asymptotically beat balanced trees on adversarial key sets — it can only improve constants/locality on *structured* data. Per-tuple model inference faces a hard floor: evaluating a width-$w$ depth-$L$ network is $\Omega(Lw)$ work, which for any nontrivial network exceeds a single comparison; thus on truly random-access per-tuple paths, learned inference cannot be free.

## 6. The Gap

For lookups the asymptotic gap is **closed** (PGM matches the cell-probe-respecting $O(\log n)$); the open question is the *constant-factor and cache-behavior* regime — when do model evaluations win on real hardware? For optimizer/estimator inference the gap is genuinely **open**: there is no tight model relating estimator accuracy to achievable inference latency under a fixed planning budget. Closing it needs hardware-aware cost models (SIMD/branch-prediction/cache) and per-query placement theory.

## 7. Current Research (as of June 2026)

Directions: branch-free and SIMD-vectorized learned indexes; quantized/distilled tiny estimators; GPU-resident inference for batched cardinality; "consult-once" optimizer hints (Bao-style) to bound per-query overhead. Foundation-model cardinality estimators raise the *opposite* concern — large models with prohibitive critical-path cost, pushing research toward distillation and caching of inferences *(frontier — verify)*. Groups: Kraska/Marcus, Kemper/Neumann (TUM), Idreos (Harvard, hardware-conscious learned structures), Ferragina–Vinciguerra (Pisa).

## 8. Future Work

- Tight hardware-aware lower bounds for per-tuple learned inference (cache misses, branch misprediction).
- Compilation/JIT of learned predictors into the execution engine to remove dispatch overhead.
- Adaptive placement: learn whether to invoke per-tuple/per-batch/per-query online.
- Distillation pipelines that trade accuracy for a guaranteed latency budget $B$.

## 9. Key References

- **[Foundational]** Kraska, Beutel, Chi, Dean, Polyzotis. *The Case for Learned Index Structures.* SIGMOD 2018. — [arXiv](https://arxiv.org/abs/1712.01208) — [DOI](https://doi.org/10.1145/3183713.3196909)
- **[SOTA]** Ferragina, Vinciguerra. *The PGM-index.* PVLDB 2020. — [DOI](https://doi.org/10.14778/3389133.3389135) — [DBLP](https://dblp.org/rec/journals/pvldb/FerraginaV20.html)
- **[SOTA]** Kipf, Marcus, van Renen, et al. *RadixSpline: A Single-Pass Learned Index.* aiDM @ SIGMOD 2020. — [arXiv](https://arxiv.org/abs/2004.14541) — [DOI](https://doi.org/10.1145/3401071.3401659)
- **[SOTA]** Hilprecht, Schmidt, Kulessa, et al. *DeepDB: Learn from Data, not from Queries!* PVLDB 2020. — [arXiv](https://arxiv.org/abs/1909.00607) — [DOI](https://doi.org/10.14778/3384345.3384349)
- **[Foundational]** Pătrașcu, Thorup. *Time-Space Trade-Offs for Predecessor Search.* STOC 2006. — [arXiv](https://arxiv.org/abs/cs/0603043) — [DBLP](https://dblp.org/rec/conf/stoc/PatrascuT06.html)
- **[SOTA]** Marcus, Negi, Mao, et al. *Bao: Making Learned Query Optimization Practical.* SIGMOD 2021. — [DOI](https://doi.org/10.1145/3448016.3452838)

## 10. Worked Example

Consider a sorted array of $n = 10^6$ keys and a point lookup. A B-tree pays $\log_2 n \approx 20$ comparisons; assume each branch-predicted comparison costs $\approx 2$ ns, so $\approx 40$ ns total.

Now a learned index. A linear segment predicts position $\hat p$, then we do a local binary search within an $\varepsilon$-window to correct the error.

- **Tiny model (RadixSpline-style).** Inference is one multiply-add plus a radix-table lookup, say $C_{\text{inf}} \approx 5$ ns. With $\varepsilon = 32$, local search costs $\log_2 32 = 5$ comparisons $\approx 10$ ns. Total $\approx 15$ ns — a $2.7\times$ win.
- **Deep model.** A width-$w=64$, depth-$L=3$ MLP costs $\Theta(Lw^2) = 3 \cdot 64^2 \approx 12{,}288$ FLOPs. Even at 0.1 ns/FLOP that is $\approx 1200$ ns $\gg 40$ ns — the inference alone erases the win.

The lesson: on the per-tuple critical path the bias–capacity trade-off must keep $C_{\text{inf}} + O(\log\varepsilon)$ below the $\Theta(\log n)$ baseline. Batching $b = 1000$ tuples amortizes a fixed dispatch cost $\kappa = 5000$ ns to $\kappa/b = 5$ ns/tuple — which is why estimators are invoked per-query, not per-tuple.

---
*Part of the [DBMS Research catalog](../../README.md).*
