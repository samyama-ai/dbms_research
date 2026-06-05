# Cardinality estimation for subgraph patterns

> **Topic:** Graph Databases & Graph Query Processing · **ID:** `21-graph-databases/subgraph-cardinality-estimation` · **Status:** open

## 1. Problem Statement

Given a (labeled) data graph $G$ and a pattern $Q$, estimate the number of embeddings (homomorphisms or subgraph isomorphisms) $|\mathrm{Emb}(Q, G)|$ **without** fully enumerating them. This *counting-estimation* problem is the cost model underpinning every graph query optimizer: it drives matching-order selection, WCOJ vs. binary-join choices, and CRPQ join ordering.

The challenge is accuracy under **heavy degree correlation** (hubs, power-law degree, assortativity) and **label skew** (rare vs. frequent edge/vertex labels), where independence and uniformity assumptions — standard in relational optimizers — fail catastrophically, producing errors of many orders of magnitude. Variants: **exact counting** (#-hard), **approximate counting** with multiplicative $(1\pm\epsilon)$ guarantees, and **practical estimation** with empirical accuracy but no proven bounds. The open problem is estimators that are *both* practical (sub-linear, low-variance on real graphs) *and* carry rigorous error bounds.

## 2. Mathematical Foundations

Homomorphism counts $\hom(Q,G)$ are central: subgraph-isomorphism counts decompose into homomorphism counts via Möbius inversion over the partition lattice (Lovász). For sampling estimators, an unbiased estimator $\hat{X}$ with relative variance $\mathrm{Var}[\hat X]/\mathbb{E}[\hat X]^2$ governs the sample size needed for $(\epsilon,\delta)$ guarantees (Chernoff/median-of-means). The **AGM bound** gives a deterministic *upper* envelope $|\mathrm{Emb}| \le \prod_e |R_e|^{x_e}$; *degree-aware* refinements (e.g. MOLP / DBPLP, "degree bounds beyond AGM" by Abo Khamis et al.) tighten this using per-attribute degree constraints, yielding polymatroid bounds expressible as an information-theoretic LP over **entropic** functions $h(\cdot)$:

$$\log|\mathrm{out}| \le \max_{h \in \Gamma_n^*} h(\text{all vars}) \ \text{s.t. degree/cardinality constraints}.$$

Random-walk and color-coding estimators rely on mixing time and on the $k$-tree-width of $Q$ respectively (Alon–Yuster–Zwick color coding gives FPT exact counting).

## 3. State of the Art (SOTA)

- **Sampling/theory-SOTA:** WanderJoin (Li–Wu–Yu, SIGMOD 2016) random-walk join sampling with unbiased estimates; *Alley* (Kim et al., SIGMOD 2021) combining sampling + synopsis; GenericJoin-style online sampling.
- **Summary/synopsis:** *Characteristic Sets* (Neumann–Moerkotte, ICDE 2011) for star/SPARQL queries; *SumRDF*, *Color/correlated sketches*.
- **Learned:** *NeuroCard*, *LSS / Learned Subgraph Sketch*, *G-CARE* benchmark (Park et al., SIGMOD 2020) showing *all* methods have huge errors on cyclic/correlated patterns; *NeurSC*, *LearnSC* GNN-based estimators (2022–2023).
- **Bound-based:** degree-aware polymatroid bounds (MOLP/PANDA lineage) for guaranteed *upper* bounds rather than point estimates.

## 4. Upper Bound

Color coding (Alon–Yuster–Zwick) counts/approximates $k$-vertex patterns of treewidth $w$ exactly in $2^{O(k)} \cdot n^{w+1}$, FPT in $k$. Randomized $(\epsilon,\delta)$ approximation of $\hom(Q,G)$ is achievable in time $\mathrm{poly}(1/\epsilon, \log(1/\delta))$ times an instance factor for bounded-treewidth $Q$. Degree-aware LP bounds (Abo Khamis–Ngo et al.) give deterministic upper bounds computable in $\mathrm{poly}$ in the number of degree constraints, provably tighter than AGM. WanderJoin gives unbiased estimates with variance bounded by the AGM bound divided by walk count.

## 5. Lower Bound

Exact counting of subgraph isomorphisms is **#P-hard** in general and **#W[1]-hard** parameterized by $|Q|$ (Flum–Grohe); counting $k$-cliques in $n^{o(k)}$ refutes ETH. Curticapean–Marx establish a complete classification: counting homomorphisms is hard exactly when the pattern class has unbounded treewidth. For *approximate* counting, certain patterns are NP-hard to approximate within any factor unless RP = NP. Information-theoretically, any estimator achieving bounded relative error on adversarial correlated/skewed instances needs sample size that can grow with the AGM bound itself — hence no sub-linear estimator can give worst-case multiplicative guarantees for cyclic, correlated patterns.

## 6. The Gap

Genuinely **open**. Practical estimators (sampling, learned) have low *average* error but unbounded *worst-case* error on correlated/skewed graphs (documented by the G-CARE benchmark). Estimators with proven bounds (color coding, polymatroid LP) are either too slow or give only loose one-sided bounds, not tight point estimates. No method delivers *practical* accuracy *with* rigorous two-sided error bounds under degree correlation and label skew. Closing it needs estimators whose variance is provably controlled by realistic structural parameters (degeneracy, degree-correlation moments) rather than worst-case AGM.

## 7. Current Research (as of June 2026)

- *(frontier — verify)* GNN/transformer estimators conditioned on degree and label histograms, with conformal-prediction-style error intervals, are an active 2024–2026 thread (groups at SNU, HKUST, TU Munich, Waterloo).
- *(frontier — verify)* hybrid "sampling-calibrated bounds" that combine polymatroid upper bounds with sampling lower bounds to *bracket* the true count.
- Degree-aware and "beyond worst-case" bound theory (Abo Khamis, Ngo, Suciu) continues to tighten deterministic guarantees.

## 8. Future Work

- Two-sided, bounded-error estimators parameterized by realistic skew/correlation measures.
- Estimators that are *consistent* under query-optimizer composition (errors don't compound across joins).
- Streaming / dynamic-graph cardinality estimation with maintenance guarantees.
- Tight connections between learned models and the information-theoretic LP bounds.

## 9. Key References

- **[Foundational]** Alon, Yuster, Zwick. *Color-Coding.* JACM 1995.
- **[Foundational]** Curticapean, Marx (and Dell). *Homomorphisms Are a Good Basis for Counting Small Subgraphs.* STOC 2017.
- **[SOTA]** Li, Wu, Yu. *Wander Join: Online Aggregation via Random Walks.* SIGMOD 2016.
- **[SOTA]** Abo Khamis, Ngo, Suciu. *What Do Shannon-type Inequalities, Submodular Width, and Disjunctive Datalog Have to Do with One Another? (degree/entropic bounds).* PODS 2017.
- **[Survey/Benchmark]** Park, Ko, Kankanamge, Salihoglu, et al. *G-CARE: A Framework for Performance Benchmarking of Cardinality Estimation Techniques for Subgraph Matching.* SIGMOD 2020.
- **[SOTA]** Kim, Choi, Han, et al. *Learned Cardinality Estimation: An In-depth Study / Alley.* SIGMOD 2021.

---
*Part of the [DBMS Research catalog](../../README.md).*
