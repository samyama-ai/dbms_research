# Generalization to Unseen Queries

> **Topic:** Learned Database Components · **ID:** `27-learned-db-components/optimizer-unseen-query-generalization` · **Status:** open

## 1. Problem Statement

Learned optimizers and cost models are trained on a finite workload sample, but production queries differ — new join graph shapes, predicate constants/columns absent from training, even new tables/schemas. The generalization problem: **characterize and guarantee how well a learned optimizer performs on queries drawn from outside its training distribution.**

Three nested generalization regimes:

- **In-distribution generalization (estimation):** new query, same distribution $\mathcal D$ — bound expected excess plan cost on a fresh draw $q\sim\mathcal D$.
- **Compositional / shape generalization:** new join-graph topology or predicate combinations not seen, but built from seen primitives (chain→star, 3-way→8-way).
- **Schema transfer (the hardest):** new tables/columns/databases entirely — the model must featurize unseen schema elements transferably (no per-column lookup table).

The decision variant: given a query $q$ and confidence $\delta$, decide whether the learned optimizer's plan is trustworthy or should fall back to the classical optimizer.

## 2. Mathematical Foundations

Let $f_\theta:\mathcal Q\to\text{Plans}$ be the learned policy with risk $R_{\mathcal D}(f)=\mathbb E_{q\sim\mathcal D}[\text{excess-cost}(f,q)]$. Standard learning theory bounds the **generalization gap** $R_{\mathcal D}-\hat R_{\text{train}}$ by complexity terms: VC dimension, Rademacher complexity $\mathfrak R_n(\mathcal F)$, or PAC-Bayes — all assuming **train and test share $\mathcal D$**. Unseen-query generalization breaks that assumption, so:

- **Covariate shift / OOD:** test queries draw from $\mathcal D'\ne\mathcal D$; risk transfers only up to discrepancy $d(\mathcal D,\mathcal D')$ (Ben-David et al. 2010). Compositional shapes induce *systematic*, not random, shift.
- **Compositional generalization:** formalized via systematicity — does $f$ correctly handle predicate/operator combinations whose components were seen but not their conjunction? Studied via the lens of relational-algebra structure; a model that is **equivariant** to the join-graph automorphism group (permutation of relations) generalizes across isomorphic shapes (graph-neural-net inductive bias).
- **Schema transfer:** requires features invariant to schema identity — encode columns by *statistics* (NDV, histograms, datatype) not by name, so an unseen column maps into the same feature space. This connects directly to **plan-featurization-expressiveness**: generalization is upper-bounded by what the encoding can represent transferably.

A clean sub-result: if the cost-relevant target function factorizes over the join graph and the model is graph-permutation-equivariant, generalization to larger isomorphic shapes is provable; without that inductive bias, no shape extrapolation is guaranteed.

## 3. State of the Art (SOTA)

- **Systems-SOTA:** *Bao*'s hint-set design generalizes robustly because actions are sound plans, so OOD queries degrade gracefully to optimizer defaults (Marcus et al., SIGMOD 2021). *Zero-shot cost models* (Hilprecht & Binnig, VLDB 2022) demonstrate schema transfer via transferable features. *Balsa* (Yang et al., SIGMOD 2022) studies generalization to held-out query templates and reports degradation off-distribution. GNN-based plan encoders aim for shape generalization *(frontier — verify)*.
- **Theory-SOTA:** generic OOD/domain-adaptation bounds; no DB-specific compositional-generalization theorem.

## 4. Upper Bound

- **In-distribution:** uniform-convergence bound $R_{\mathcal D}(f)\le \hat R+\tilde O(\sqrt{\mathfrak R_n(\mathcal F)/n})$ in the **PAC/statistical-learning model** — standard, holds only no-shift.
- **Shifted:** $R_{\mathcal D'}(f)\le \hat R_{\mathcal D}+d_{\mathcal H\Delta\mathcal H}(\mathcal D,\mathcal D')+\lambda^\*$ (Ben-David). For permutation-equivariant models on isomorphic shapes, the shape-extrapolation term can be zero by construction.

## 5. Lower Bound

- **No-free-lunch / OOD impossibility:** for arbitrary unseen distributions there is no learner with bounded excess risk — an adversary places test mass on the worst region (information-theoretic). Schema transfer to a database with genuinely novel correlation structure is unbounded without samples.
- **Compositional hardness:** representing all conjunctions of $k$ seen predicates requires either exponential capacity or a compositional inductive bias; without the bias, a model can fit training conjunctions while erring on unseen ones (separation results from compositional-generalization theory).
- **Estimation barrier inherited:** since cost depends on cardinality, unseen-predicate generalization inherits CE's $\Omega(n)$-space / sampling lower bounds for unseen joint mass (see topic 26).

## 6. The Gap

Open. In-distribution generalization is well understood; **systematic** shift (shape, predicate, schema) is not. The gap is between (a) generic OOD bounds that are vacuous when discrepancy is large and (b) the empirical observation that the *right inductive bias* (graph equivariance, statistic-based schema features) generalizes far better than the bounds predict. Closing it requires DB-specific compositional-generalization theory: identify the encoding + architecture class for which shape/schema extrapolation is provable, and the queries for which it is provably impossible.

## 7. Current Research (as of June 2026)

- Transferable, schema-agnostic featurization (data statistics instead of identifiers) for zero-shot transfer to unseen DBs (Binnig group, TU Darmstadt) *(frontier — verify)*.
- Graph-neural plan/query encoders for shape generalization with permutation-equivariant inductive bias *(frontier — verify)*.
- OOD detection + abstention: route low-confidence queries to the classical optimizer (ties to **learned-component-robustness** fallback).
- Benchmarks stress-testing held-out templates, larger join counts, and shifted constants (CEB/JOB-extended, learned-optimizer benchmark efforts).

## 8. Future Work

- A compositional-generalization theorem for join-graph-structured policies (when does seen-primitive → unseen-combination extrapolation hold?).
- Calibrated OOD/confidence scores that gate fallback with bounded false-trust rate.
- Schema-transfer guarantees tied to measurable feature invariances.
- Joint study with **plan-featurization-expressiveness**: generalization ceiling = encoding's transferable-expressiveness ceiling.

## 9. Key References

- **[Foundational]** Ben-David, Blitzer, Crammer, Kulesza, Pereira, Vaughan. *A Theory of Learning from Different Domains.* Machine Learning, 2010. — [DOI](https://doi.org/10.1007/s10994-009-5152-4)
- **[SOTA]** Hilprecht, Binnig. *Zero-Shot Cost Models for Out-of-the-Box Learned Cost Prediction.* VLDB, 2022. — [arXiv](https://arxiv.org/abs/2201.00561)
- **[SOTA]** Yang, Chiang, Luan, et al. *Balsa: Learning a Query Optimizer Without Expert Demonstrations.* SIGMOD, 2022. — [arXiv](https://arxiv.org/abs/2201.01441)
- **[SOTA]** Marcus, Negi, Mao, Tatbul, Alizadeh, Kraska. *Bao: Making Learned Query Optimization Practical.* SIGMOD, 2021. — [DOI](https://doi.org/10.1145/3448016.3452838)
- **[Survey]** Lan, Bao, Peng. *A Survey on Advancing the DBMS Query Optimizer: Cardinality Estimation, Cost Model, and Plan Enumeration.* Data Science and Engineering, 2021. — [DOI](https://doi.org/10.1007/s41019-020-00149-7)

## 10. Worked Example

Train a learned optimizer only on **chain** joins $A\!\bowtie\!B\!\bowtie\!C$ (a path graph). Test query: a **star** join $A\!\bowtie\!B,\,A\!\bowtie\!C,\,A\!\bowtie\!D$ (hub $A$). Both use the seen primitive "two-way hash join", but the star's topology was never seen — *systematic*, not random, shift.

- **Flat/per-edge encoder.** Features = bag of pairwise join predicates. The chain and star can share identical pairwise features yet have very different optimal plans (the star wants $A$ built once and probed 3×). The encoder conflates them: degradation off-distribution, as Balsa reports on held-out templates.
- **Permutation-equivariant GNN.** Encode the join graph; message passing makes node $A$'s embedding reflect its degree-3 hub role. If true cost factorizes over the graph and the model is equivariant to relabeling $\{B,C,D\}$, the section-4 shape-extrapolation term is **0**: the learned policy provably transfers to any star isomorphic to the trained-on motif size.

Contrast the lower bound: a genuinely new *4-clique* topology (cyclic, no acyclic seen analog) carries no equivariance guarantee — the no-free-lunch barrier of section 5 bites, and abstention to the classical optimizer is the safe move.

---
*Part of the [DBMS Research catalog](../../README.md).*
