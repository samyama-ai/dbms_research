---
id: 26-cardinality-estimation/cross-engine-statistics-transfer
title: "Cross-Engine Transfer of Statistics"
topic: 26-cardinality-estimation
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Cross-Engine Transfer of Statistics

> **Topic:** Cardinality Estimation & Statistics · **ID:** `26-cardinality-estimation/cross-engine-statistics-transfer` · **Status:** open

## 1. Problem Statement

Building statistics and learned estimators is expensive: scanning data, sampling, training models, and collecting query feedback. The problem: **reuse or transfer statistical summaries and learned CE models across schemas, datasets, and engines** so that a model trained in one context bootstraps accurate estimation in another with little or no fresh data.

Variants:

- **Cross-schema transfer (estimation):** transfer a learned estimator from schema $S_1$ to a related schema $S_2$ (different tables/columns but similar domains), e.g. via column-type/semantic alignment.
- **Cross-engine transfer (interoperability):** map statistics or models between systems with different cost models and statistic formats (Postgres ↔ Spark ↔ DuckDB ↔ a commercial optimizer).
- **Cross-data transfer (zero/few-shot):** a *pretrained* CE model that generalizes to an unseen dataset from its schema and small samples, without per-dataset training.

This matters for cold-start (new tenants/tables with no history), federated/polystore query optimization, and reducing the per-deployment cost of learned CE.

## 2. Mathematical Foundations

A statistic is a summary $T(D)$ (histogram, sketch, NDV estimate, learned density). Transfer asks for a map $\Phi$ such that $T_2 \approx \Phi(T_1)$ is accurate for $D_2$. Two regimes:

- **Invariant statistics:** some summaries are *schema-agnostic functionals* — quantiles, entropy, NDV ratios, correlation coefficients — that may transfer if domains align. Sketch *mergeability* (e.g. HyperLogLog, KMV, Count-Min are mergeable under a homomorphism) lets summaries compose across partitions/engines without recomputation, the cleanest transfer case.
- **Learned models:** transfer is a **domain-adaptation / transfer-learning** problem; the relevant bound is $\epsilon_{T}(h)\le \epsilon_S(h)+\tfrac12 d_{\mathcal H\Delta\mathcal H}(P_{S},P_{T})+\lambda$ (Ben-David et al.), so transfer succeeds only when source and target distributions/feature spaces are close after alignment $\Phi$.

Cross-engine adds a **cost-model mismatch**: even a perfectly transferred cardinality must be consumed by a different cost function $C_2$, so transferring *statistics* and transferring *plan quality* are distinct goals. Semantic alignment of columns is an **entity/schema-matching** problem (probabilistic schema mapping; representation learning over column embeddings).

## 3. State of the Art (SOTA)

- **Mergeable sketches (engine-portable):** HyperLogLog (Flajolet et al., 2007), KMV/bottom-$k$, Count-Min (Cormode–Muthukrishnan, 2005), $t$-digest — already shared across engines because they are format-stable and mergeable; the practical SOTA for portable statistics.
- **Pretrained / transferable learned CE:** *(frontier — verify)* "foundation-model"-style CE that pretrains on many datasets and adapts few-shot; column-embedding approaches that featurize predicates by learned column representations to enable cross-schema transfer.
- **Cross-engine optimization context:** learned optimizers and cost models that are partly portable (Bao/Neo lineage); transfer-learning studies for learned CE/optimizers showing partial reuse across workloads. No standardized statistics-interchange format across optimizers is in wide use.

## 4. Upper Bound

- **Mergeable summaries:** transfer/compose exactly (up to the sketch's own $(\epsilon,\delta)$ guarantee) across engines — e.g. HLL gives relative error $\approx 1.04/\sqrt m$ regardless of where merged; this is a tight, engine-independent guarantee.
- **Learned-model transfer:** bounded by the domain-adaptation inequality — error after transfer $\le$ source error $+$ alignment divergence $+$ joint risk $\lambda$; useful only when $\Phi$ makes $d_{\mathcal H\Delta\mathcal H}$ small.
- No general guarantee exists for transferring a learned *joint distribution* model to an unrelated schema.

## 5. Lower Bound

- **Information-theoretic:** if target columns carry correlations absent from any source, no transfer can recover them — target-specific information must be sampled (no-free-lunch for transfer).
- **Schema-matching hardness:** optimal semantic alignment $\Phi$ between schemas is NP-hard in general (it generalizes graph/ontology matching), so even deciding *whether* transfer is safe is intractable.
- **Cost-model non-transfer:** a transferred cardinality can yield arbitrarily bad plans under a different cost model; transferring cardinalities does **not** bound plan regret across engines (constructible counterexamples).

## 6. The Gap

**Genuinely open.** Only mergeable sketches transfer with guarantees; learned-model and cross-schema transfer have promising empirics but no theory tying alignment quality to accuracy, no standard cross-engine statistics format, and no account of cost-model mismatch. Closing it needs (a) provable alignment-to-accuracy bounds for learned CE, (b) a portable statistics interchange standard, and (c) joint transfer of cardinality *and* the relevant cost-model calibration.

## 7. Current Research (as of June 2026)

- Pretrained / few-shot "foundation" cardinality estimators with column-embedding featurization for zero-shot transfer to new schemas *(frontier — verify)*.
- Transfer-learning and meta-learning for learned CE/optimizers to cut per-deployment training (Berkeley, MIT, TUM groups; Microsoft Research).
- Portable mergeable-sketch ecosystems (Apache DataSketches) as the reliable cross-engine substrate.
- Federated/polystore optimization needing cross-engine statistic exchange *(frontier — verify)*.

## 8. Future Work

- Provable alignment-quality → transfer-accuracy bounds.
- A standardized, engine-neutral statistics/model interchange format.
- Joint cardinality + cost-model transfer with plan-regret guarantees.
- Robust column/schema embeddings that make cross-schema transfer reliable, with abstention when domains are too distant.

## 9. Key References

- **[Foundational]** Flajolet, Fusy, Gandouet, Meunier. *HyperLogLog: The Analysis of a Near-Optimal Cardinality Estimation Algorithm.* AofA, 2007. — [HAL](https://hal.science/hal-00406166)
- **[Foundational]** Cormode, Muthukrishnan. *An Improved Data Stream Summary: The Count-Min Sketch and its Applications.* J. Algorithms, 2005. — [DBLP](https://dblp.org/rec/journals/jal/CormodeM05.html)
- **[Foundational]** Ben-David, Blitzer, Crammer, Kulesza, Pereira, Vaughan. *A Theory of Learning from Different Domains.* Machine Learning, 2010. — [DOI](https://doi.org/10.1007/s10994-009-5152-4)
- **[Foundational]** Bar-Yossef, Jayram, Kumar, Sivakumar, Trevisan. *Counting Distinct Elements in a Data Stream.* RANDOM, 2002. — [DOI](https://doi.org/10.1007/3-540-45726-7_1)
- **[SOTA]** Marcus, Negi, Mao, Tatbul, Alizadeh, Kraska. *Bao: Making Learned Query Optimization Practical.* SIGMOD, 2021. — [DOI](https://doi.org/10.1145/3448016.3452838)
- **[Survey]** Cormode, Garofalakis, Haas, Jermaine. *Synopses for Massive Data: Samples, Histograms, Wavelets, Sketches.* Foundations and Trends in Databases, 2011. — [DOI](https://doi.org/10.1561/1900000004)

## 10. Worked Example

Consider transferring an NDV (distinct-count) statistic across engines via a **mergeable sketch** — the clean case from Section 3. Engine A holds partition $P_1$ of a column, engine B holds partition $P_2$, and we want the global NDV of $P_1 \cup P_2$ without re-scanning.

Use HyperLogLog with $m = 1024$ registers. HLL's relative standard error is $\approx 1.04/\sqrt{m} = 1.04/32 = 3.25\%$. Each engine builds its own sketch locally; register $j$ stores the max leading-zero count seen. Merging is register-wise max: $\text{HLL}_{\cup}[j] = \max(\text{HLL}_{P_1}[j], \text{HLL}_{P_2}[j])$. This is exact — the merged sketch is byte-identical to one built over $P_1 \cup P_2$ in a single pass, because "max of maxes" is associative and idempotent. So if true global NDV $= 1{,}000{,}000$, the estimate lands within $\approx \pm 32{,}500$ with the same $3.25\%$ guarantee regardless of where it was merged.

Contrast a **learned density model** trained on $P_1$'s schema: applied to $P_2$'s differently-distributed column it has no such guarantee — its error is bounded only by the domain-adaptation inequality $\epsilon_T \le \epsilon_S + \tfrac12 d_{\mathcal H\Delta\mathcal H}(P_1,P_2) + \lambda$, which is vacuous when the distributions diverge. This is exactly why mergeable sketches are the reliable cross-engine substrate.

---
*Part of the [DBMS Research catalog](../../README.md).*
