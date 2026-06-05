# Adversarial robustness of ANN indexes

> **Topic:** Vector Databases & Similarity Search · **ID:** `28-vector-similarity-search/adversarial-robustness-ann` · **Status:** open

## 1. Problem Statement
Graph ANN indexes (HNSW, Vamana/DiskANN) and partition indexes (IVF, LSH) are tuned and benchmarked on benign, often i.i.d. workloads. Their good behavior — near-logarithmic query cost, high recall, cheap incremental build — is *average-case*. The problem: **characterize and defend against adversarial input.** An adversary controlling the *insert stream*, the *query stream*, or both can try to (a) degrade query recall far below its configured target, (b) inflate per-query distance computations (a latency/DoS attack), or (c) blow up build/maintenance cost (e.g., force pathological degree distributions or repeated graph repairs).

Variants:
- **Query-time adversary:** index fixed; choose queries $q_1,\dots,q_T$ maximizing total distance evaluations or worst recall.
- **Insert-time (poisoning) adversary:** choose an insertion order / a set of points that makes the *built* graph fragile or disconnected for honest queries.
- **Adaptive adversary:** observes results/timing and adapts (the classic adaptive-data-analysis setting), defeating any fixed randomized seed.
- **Defense / decision:** does there exist a build+query policy guaranteeing recall $\ge\rho$ and cost $\le B$ against the worst case (or with high probability against an oblivious adversary)?

## 2. Mathematical Foundations
Model an ANN index as a (randomized) data structure $\mathcal{D}$ supporting `insert(x)` and `query(q)→S`. Define adversarial recall $\rho_{\mathrm{adv}}=\min_{q}\Pr[\text{true }k\text{-NN}\subseteq S]$ over an adversarially chosen query set, and adversarial cost $C_{\mathrm{adv}}=\max_q \mathbb{E}[\#\text{dist-evals}]$.

Key scaffolding:
- **Adaptive adversaries vs. randomized data structures.** Hardt–Woodruff and the adaptive-data-analysis line show that data structures correct for *oblivious* inputs can be driven to failure by adversaries who adapt to released outputs; sketches/embeddings (Johnson–Lindenstrauss) are not robust to adaptively chosen queries unless re-randomized or made differentially private.
- **Greedy-search pathology.** Greedy descent fails when the graph has *local minima* w.r.t. a query — a node closer than all its neighbors but far from the true NN. An adversary maximizes the basin/depth of such minima.
- **Hardness of NN itself.** Worst-case exact NN in high $d$ is SETH-hard (subquadratic ruled out), so any robustness claim must be about *approximate* recall and *amortized* cost.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** essentially none purpose-built. Production defenses are operational: query rate limiting, capping `ef`/`n_probe`, timeouts that return partial results, and periodic rebuilds. Robustness is not a benchmarked axis on ann-benchmarks.
- **Adjacent results:** robust-streaming and adversarially-robust sketching (Ben-Eliezer–Jayaram–Woodruff–Yogev, PODS 2020) give a template — bound the number of "flips" an adaptive adversary can induce and re-randomize — but have not been instantiated for graph ANN. Robust sublinear NN under adaptive queries is largely unstudied.
- **Attack-side:** empirical demonstrations that crafted query distributions and insertion orders can sharply raise HNSW search cost / lower recall exist as security-flavored studies *(frontier — verify)*; embedding-poisoning attacks on RAG retrieval (corpus-poisoning) are an active applied-security topic.

## 4. Upper Bound
No tight robustness upper bound is published specifically for graph ANN. Transferable templates: the adversarially-robust streaming framework yields, for a structure tolerating $f$ adaptive corruptions, an overhead of $\tilde{O}(\sqrt{f})$ independent copies (sketch-switching) — suggesting a *recall-robust* ANN at $\tilde{O}(\sqrt{T})$-copy overhead for $T$ adaptive queries, but this is conjectural for graphs. Differential-privacy-style noise on returned distances can bound an adaptive adversary's information gain at a known recall cost (a privacy↔robustness transfer), again not yet realized as a deployed ANN.

## 5. Lower Bound
- **Fine-grained:** since exact bichromatic closest pair is SETH-hard for $d=\omega(\log n)$ (Rubinstein, STOC 2018), an adversary picking queries near the decision boundary forces any exact method to $\Omega(n^{2-o(1)})$ total work — robustness *must* sacrifice exactness.
- **Adaptive-adversary impossibility:** JL-based and LSH-based structures have linear-query attacks — there exist $O(d)$ adaptively chosen queries that recover enough of the random projection to construct an input on which recall collapses (Hardt–Woodruff-style). This gives an information-theoretic barrier: a *fixed-randomness* ANN cannot be robust against a fully adaptive adversary.

## 6. The Gap
Wide open. There is no formal robustness model agreed upon for ANN, no benchmark, essentially no provable defense, and only scattered attacks. The central question — *can a single index simultaneously guarantee a recall floor and a cost ceiling against an oblivious (let alone adaptive) adversary, and at what overhead?* — is unanswered. Closing it requires (i) a precise adversary model, (ii) instantiating robust-streaming / DP machinery on proximity graphs, and (iii) matching lower bounds on the price of robustness.

## 7. Current Research (as of June 2026)
Active threads: corpus-poisoning and retrieval-attack research on RAG pipelines (security/ML venues); adversarially-robust streaming and sketching theory (Woodruff, Yogev and collaborators) that the ANN community is beginning to import *(frontier — verify)*; and "graph repair under adversarial inserts" within vector-DB engineering. Differential privacy as a robustness lever for similarity search is an emerging crossover *(frontier — verify)*.

## 8. Future Work
- A standard adversarial-ANN threat model and benchmark suite.
- Provable recall-floor / cost-ceiling indexes against oblivious adversaries with quantified overhead.
- Re-randomization / sketch-switching schedules for graph indexes to blunt adaptive attacks.
- Cheap poisoning detection on insert streams (degree/clustering anomalies).

## 9. Key References
- **[Foundational]** O. Ben-Eliezer, R. Jayaram, D. P. Woodruff, E. Yogev. *A Framework for Adversarially Robust Streaming Algorithms.* PODS, 2020. — [arXiv](https://arxiv.org/abs/2003.14265) — [DOI](https://doi.org/10.1145/3375395.3387658)
- **[Foundational]** M. Hardt, D. P. Woodruff. *How Robust are Linear Sketches to Adaptive Inputs?* STOC, 2013. — [arXiv](https://arxiv.org/abs/1211.1056) — [DOI](https://doi.org/10.1145/2488608.2488624)
- **[Foundational]** A. Rubinstein. *Hardness of Approximate Nearest Neighbor Search.* STOC, 2018. — [arXiv](https://arxiv.org/abs/1803.00904) — [DOI](https://doi.org/10.1145/3188745.3188916)
- **[SOTA]** Y. Malkov, D. Yashunin. *Efficient and Robust Approximate Nearest Neighbor Search using HNSW graphs.* IEEE TPAMI, 2020 (arXiv:1603.09320). — [arXiv](https://arxiv.org/abs/1603.09320) — [DOI](https://doi.org/10.1109/TPAMI.2018.2889473)
- **[SOTA]** S. J. Subramanya, et al. *DiskANN: Fast Accurate Billion-point Nearest Neighbor Search on a Single Node.* NeurIPS, 2019. — [NeurIPS](https://proceedings.neurips.cc/paper/2019/hash/09853c7fb1d3f8ee67a61b6bf4a7f8e6-Abstract.html) — [DBLP](https://dblp.org/rec/conf/nips/SubramanyaDSKK19.html)
- **[Survey]** C. Dwork, A. Roth. *The Algorithmic Foundations of Differential Privacy.* Foundations and Trends in TCS, 2014. — [DOI](https://doi.org/10.1561/0400000042)

## 10. Worked Example

**A query-time adversary forcing a greedy-search local minimum.** Take 6 points on a line, $a{=}0, b{=}1, c{=}2, d{=}10, e{=}11, f{=}12$, and build a proximity graph where each node links only to its two nearest neighbors: $a\!-\!b\!-\!c$ and $d\!-\!e\!-\!f$, with one bridge $c\!-\!d$. Greedy 1-NN search starts at a fixed entry, say $a$.

Honest query $q{=}1.4$: true NN is $c$ (dist $0.6$). Greedy from $a$: $a(1.4)\to b(0.4)\to c(0.6)$ — neighbor $d$ is farther, stop at $c$. Correct, 3 distance evals.

Adversarial query $q{=}9.6$: true NN is $d$ (dist $0.4$). Greedy from $a$: $a(9.6)\to b(8.6)\to c(7.6)\to d(0.4)\to e$? $e$ is dist $1.4 > 0.4$, stop at $d$. Here it still succeeds but costs $4$ evals. Now delete the single bridge $c\!-\!d$ (a poisoning insert that crowds it out): greedy halts at $c$ (dist $7.6$) — recall drops to $0$. One adversarial edge removal flips recall from $1$ to $0$, illustrating why fixed-randomness graphs have no worst-case recall floor.

---
*Part of the [DBMS Research catalog](../../README.md).*
