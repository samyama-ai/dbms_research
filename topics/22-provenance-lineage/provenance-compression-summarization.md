---
id: 22-provenance-lineage/provenance-compression-summarization
title: "Provenance Compression and Summarization"
topic: 22-provenance-lineage
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
refs_unverified: 1
---

# Provenance Compression and Summarization

> **Topic:** Provenance & Lineage · **ID:** `22-provenance-lineage/provenance-compression-summarization` · **Status:** partially-solved

## 1. Problem Statement

Provenance graphs (and provenance polynomials) blow up: a single join answer can carry a witness set exponential in the query size, and workflow lineage grows linearly with execution but with enormous constants. The problem is to **compress or summarize** provenance so that it is small enough to store/transmit/query, while **preserving answerability of a stated class of provenance queries** $\mathcal{Q}_p$.

Two regimes:
- **Lossless (factorization / circuit):** an equivalent, smaller representation (d-DNNF/circuit, factorized form, deduplicated DAG) from which *every* query in $\mathcal{Q}_p$ is answered exactly. Optimization: minimum-size representation.
- **Lossy (summarization):** a smaller structure (clustering, sketch, sample, schema-level rollup) that answers $\mathcal{Q}_p$ within a tolerance $\varepsilon$ (e.g., approximate why-provenance recall, approximate model count, top-$k$ contributors). Optimization: minimum size subject to an error/answerability constraint, or minimum error subject to a size budget.

Status **partially solved**: lossless factorization theory is mature (semiring circuits, factorized DBs); lossy summarization with *provable* answerability guarantees for a characterized query class is largely open.

## 2. Mathematical Foundations

Provenance lives in the polynomial semiring $\mathbb{N}[X]$; a **factorized / circuit representation** is a $\{+,\times\}$-circuit (with variables/constants as leaves) computing the polynomial. Lossless compression = finding a small circuit; the **knowledge-compilation** lattice (OBDD ⊊ FBDD ⊊ d-DNNF ⊊ DNNF) sets which queries each form supports in PTIME (model counting needs d-DNNF/decision-DNNF).

Sizes are bounded by structure: for a CQ, the factorized provenance size is $O(|\mathrm{IN}|^{\mathsf{fhtw}})$ where $\mathsf{fhtw}$ is the **fractional hypertree width** (Olteanu–Závodný), matching the AGM-bound intuition. Where lower bounds bite, **monotone-circuit / knowledge-compilation lower bounds** (e.g., exponential OBDD/d-DNNF lower bounds for certain UCQs/queries with "hard" hypergraph structure) certify incompressibility.

Lossy summarization is naturally a **rate–distortion** problem: minimize representation bits subject to distortion $d(\text{provenance}, \widehat{\text{provenance}}) \le \varepsilon$ on $\mathcal{Q}_p$. Choosing a best summary subset is typically **submodular** (coverage of witnesses) giving $(1-1/e)$ greedy, or maps to **graph summarization / minimum description length (MDL)**.

## 3. State of the Art (SOTA)

Theory-SOTA (lossless): **factorized databases** (Olteanu–Závodný, ICDT 2012 / TODS 2015) and **provenance circuits / semiring compilation** (Deutch–Milo–Roy–Tannen "circuits for provenance," ICDT 2014) give optimal-width factorized provenance and tractable query support. **Provenance sketches** (Niu–Glavic et al., "uncertainty-annotated/provenance sketches," 2019–2021) capture a coarse, range-based summary of which fragments contribute, used to skip irrelevant data. Systems-SOTA: **GProM** factorized/compressed provenance; **ProvSQL** (Senellart et al., VLDB 2018) stores provenance as compiled circuits and supports probabilistic queries; **Pug/Why-not** summarization; graph-summarization techniques (clustering, supernodes) applied to PROV graphs. Streaming/workflow systems use **deduplicated DAGs** and reference-sharing as the practical compressor.

## 4. Upper Bound

- **Lossless CQ provenance:** factorized representation of size $O(|\mathrm{IN}|^{\mathsf{fhtw}})$, constructible in time $\tilde{O}(|\mathrm{IN}|^{\mathsf{fhtw}} + |\text{out}|)$ — RAM model (Olteanu–Závodný).
- **Compiled circuit (d-DNNF):** for queries in the safe/hierarchical class, polynomial-size circuit supporting exact model counting (probabilistic query eval) — knowledge-compilation model.
- **Lossy coverage summary:** $(1-1/e)$-approximate maximum witness coverage under a size budget via greedy on the submodular coverage objective — value-oracle model.
- **Sketch-based contribution estimates:** $\varepsilon$-additive top-$k$ contributor estimates with $O(\varepsilon^{-2}\log\frac{1}{\delta})$ space via AMS/Count-style sketches — streaming model.

## 5. Lower Bound

- **Incompressibility:** there exist UCQs whose provenance requires **$2^{\Omega(n)}$-size** OBDD/d-DNNF/monotone circuits (knowledge-compilation / monotone-circuit lower bounds), so no polynomial lossless representation supporting exact counting exists — unconditional in the compilation model.
- **Minimum factorization is hard:** computing the *smallest* circuit/factorization for a given polynomial is **NP-hard** (relates to minimum-formula / Boolean factorization).
- **Lossy with exact-answerability is hard:** minimum summary preserving exact why-provenance generalizes **minimum set cover** → NP-hard, inapproximable below $\ln n$.
- **Rate–distortion limits:** information-theoretic lower bound — no summary below $H(\text{provenance}\mid\mathcal{Q}_p)$ bits can answer $\mathcal{Q}_p$ within zero distortion.

## 6. The Gap

Lossless is essentially **closed at the structural level** (width-tight factorization; matching compilation lower bounds), with the only gap being *minimum-size* construction (NP-hard, no good approximation known). The **lossy side is genuinely open**: there is no general theory connecting a *named provenance-query class* $\mathcal{Q}_p$ to the minimum summary size that preserves $\varepsilon$-answerability — current summaries (clustering, sketches) lack guarantees that a downstream why/how/probabilistic query is answered within bounded error. Closing it needs a rate–distortion characterization per query class plus matching summary constructions.

## 7. Current Research (as of June 2026)

(1) **Provenance sketches** extended to richer query classes and to skipping work during *re-execution*, with formal capture-recall guarantees (Glavic, Niu) *(frontier — verify)*. (2) **Circuit compilation for probabilistic/where provenance** in ProvSQL-class systems, pushing safe-query factorization further (Senellart, Amarilli, Monet). (3) **MDL / graph-summarization** of PROV-style lineage with supernode rollups preserving reachability queries. (4) Learned / amortized summarizers that predict which provenance fragments a workload will query *(frontier — verify)*.

## 8. Future Work

- A rate–distortion theory parameterized by the target provenance-query class.
- Approximation algorithms for minimum factorization / minimum lossy summary with provable ratios.
- Summaries that simultaneously preserve why, how, and probabilistic queries.
- Streaming/windowed compression with bounded memory and bounded answer error.

## 9. Key References

- **[Foundational]** D. Olteanu, J. Závodný. *Factorised Representations of Query Results / Size Bounds.* ICDT 2012; ACM TODS, 2015. — [arXiv](https://arxiv.org/abs/1104.0867) · [DOI](https://doi.org/10.1145/2656335)
- **[Foundational]** D. Deutch, T. Milo, S. Roy, V. Tannen. *Circuits for Datalog Provenance.* ICDT, 2014. — [DOI](https://doi.org/10.5441/002/icdt.2014.22) · [DBLP](https://dblp.org/rec/conf/icdt/DeutchMRT14.html)
- **[SOTA]** P. Senellart, L. Jachiet, S. Maniu, Y. Ramusat. *ProvSQL: Provenance and Probability Management in PostgreSQL.* PVLDB, 2018. — [DOI](https://doi.org/10.14778/3229863.3236253) · [DBLP](https://dblp.org/rec/journals/pvldb/SenellartJMR18.html)
- **[SOTA]** X. Niu, B. Glavic et al. *Provenance Sketches / Uncertainty-Annotated Databases.* SIGMOD / PVLDB, 2019–2021. — [arXiv](https://arxiv.org/abs/2104.12815) · [DOI](https://doi.org/10.14778/3494124.3494130) *(closest confirmed: "Provenance-based Data Skipping," PVLDB 15(3), 2022)*
- **[Survey]** A. Amarilli, P. Bourhis, M. Monet, P. Senellart. *Knowledge Compilation for Probabilistic Databases.* (compilation/d-DNNF results), 2017–2020. — [DBLP search](https://dblp.org/search?q=Amarilli+Monet+Senellart+knowledge+compilation) *(grouped line; cf. Amarilli–Monet–Senellart, "Connecting Width and Structure in Knowledge Compilation," ICDT 2018, [DOI](https://doi.org/10.4230/LIPIcs.ICDT.2018.6))*
- **[Foundational]** T. M. Cover, J. A. Thomas. *Elements of Information Theory* (rate–distortion). Wiley, 2006. — [DOI](https://doi.org/10.1002/047174882X)

## 10. Worked Example

Consider the join $Q = R(A,B)\bowtie S(B,C)$ where $B$ takes one value $b$, with $R$ holding $A\in\{a_1,a_2,a_3\}$ and $S$ holding $C\in\{c_1,c_2,c_3\}$. The flat provenance of the $9$ output tuples is the sum-of-products polynomial
$$\phi = \sum_{i=1}^{3}\sum_{j=1}^{3} a_i\,b\,c_j,$$
which is $9$ monomials, $27$ variable-occurrences.

**Factorization** exploits that $B$ is shared: pull $b$ out and distribute the join,
$$\phi = b\cdot\Big(\textstyle\sum_{i} a_i\Big)\cdot\Big(\textstyle\sum_{j} c_j\Big),$$
a circuit with only $1+3+3 = 7$ leaves and $2$ products. For $n$ values on each side, flat size is $\Theta(n^2)$ but the factorized form is $\Theta(n)$ — matching the $O(|\mathrm{IN}|^{\mathsf{fhtw}})$ bound, since this acyclic query has $\mathsf{fhtw}=1$.

The compression is **lossless**: every why/how query (which sources produced output $(a_i,c_j)$? — answer $\{a_i,b,c_j\}$) is recoverable by evaluating the relevant circuit branch. The contrast with incompressible UCQs is that those have hypergraph structure forcing $2^{\Omega(n)}$-size d-DNNFs, so no such linear factorization exists.

---
*Part of the [DBMS Research catalog](../../README.md).*
