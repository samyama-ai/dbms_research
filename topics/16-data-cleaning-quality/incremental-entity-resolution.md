# Incremental Entity Resolution

> **Topic:** Data Cleaning & Quality · **ID:** `16-data-cleaning-quality/incremental-entity-resolution` · **Status:** open

## 1. Problem Statement

A batch ER computation produces a partition (clustering) $\mathcal{C}$ of records into entities. In practice the input *changes*: records are inserted/deleted/updated, blocking keys change, the matcher is retrained, or matching **rules/constraints** are edited. **Incremental ER** maintains $\mathcal{C}$ under these updates **without recomputing from scratch**, ideally with work proportional to the *change* and bounded *drift* from the from-scratch result.

- **Data-update variant:** given $\Delta$ records (inserts/deletes/updates), produce $\mathcal{C}'$ matching (or provably close to) the batch result on $R\cup\Delta$.
- **Rule/model-update variant:** the matcher or constraints change; update $\mathcal{C}$ accordingly — strictly harder, since a single rule edit can flip many old decisions.
- **Decision:** does an update change the cluster of record $x$?
- **Optimization:** minimize maintenance work / latency subject to a staleness/accuracy bound.

It is marked **open**: no method maintains correlation-clustering-quality ER under arbitrary updates with sublinear amortized cost *and* bounded divergence from batch, especially under rule changes.

## 2. Mathematical Foundations

ER consolidation is **correlation clustering** (NP-hard, APX-hard; see *Transitive Closure in Matching*). Incremental ER is therefore a **dynamic graph clustering / dynamic correlation clustering** problem: maintain an (approximate) optimum of an NP-hard objective under edge/vertex insertions and deletions.

- **Insertion-only / order-independence:** Whang et al. formalize *incremental ER* and show that for certain merge functions ER is **confluent / order-independent** (the result is independent of processing order), enabling sound incremental merges; in general ER is order-*dependent*, so increments can diverge from batch.
- **Dynamic-graph lower bounds:** maintaining connected components under edge deletions has **OMv-conditional** polynomial update lower bounds; dynamic clustering inherits these. The **Online Matrix–Vector (OMv) conjecture** implies no $O(n^{1-\epsilon})$ worst-case update for many incremental graph problems.
- **Amortization:** good incremental schemes target $\tilde O(|\Delta| \cdot \text{polylog})$ amortized work, bounding the *recourse* (number of records changing cluster per update) — a key competitive measure analogous to online/competitive analysis.
- Rule changes correspond to *batch edge re-weighting*; bounding the induced cluster change is a **sensitivity/stability** question for correlation clustering, largely uncharacterized.

## 3. State of the Art (SOTA)

- **Incremental ER framework** (Whang, Garcia-Molina, *VLDB 2010 / VLDBJ 2014*) — foundational model of evolving ER, rule evolution, and conditions for incremental correctness.
- **Gradual / online deduplication** and **R-Swoosh / F-Swoosh incremental variants** (Benjelloun et al., *Swoosh*, VLDBJ 2009) — generic merge/match with properties (ICAR) enabling efficient (and incremental) resolution.
- **Streaming/online correlation clustering** with bounded recourse (Cohen-Addad, Lattanzi, et al., 2021–2024) — theory-SOTA for dynamic clustering maintenance *(frontier — verify)*.
- **Incremental/continuous ER systems** in industry (Senzing, Zingg-streaming, AWS Entity Resolution incremental mode) — systems-SOTA, mostly insertion-focused.
- **Embedding/ANN-based incremental blocking** with HNSW dynamic inserts feeding incremental clustering.

## 4. Upper Bound

- Insertion-only, order-independent merge functions: incremental maintenance in time proportional to affected blocks, $\tilde O(|\Delta|\cdot b)$ for block size $b$ (Whang/Swoosh).
- Dynamic correlation clustering: recent results maintain $O(1)$-approximate clustering with **polylog amortized update time and recourse** under edge updates *(frontier — verify)*; for the disagreement objective, constant-approximation with $\text{poly}\log n$ recourse per update.
- Distinct-entity-count maintenance: HyperLogLog merges in $O(1)$.

## 5. Lower Bound

- **OMv-conditional:** maintaining exact connected components / clustering under edge deletions admits no $O(n^{1-\epsilon})$ worst-case update unless the OMv conjecture fails — a fine-grained dynamic lower bound.
- **APX-hardness** of the underlying static objective transfers: you cannot incrementally maintain something you cannot compute, so optimal incremental ER is NP-hard per step.
- **Recourse lower bounds:** for online correlation clustering, $\Omega(\log n)$ amortized recourse is necessary in adversarial-arrival models (online lower bound).
- **Order-dependence impossibility:** when ER is not confluent, *no* incremental scheme can match the batch result for all update orders (a stability/impossibility result).

## 6. The Gap

**Genuinely open.** Insertion-only, confluent ER is well-handled (near-tight), but the realistic setting — deletions, *updates*, and especially **rule/model changes** — has no method that is simultaneously (a) sublinear/low-recourse per update, (b) provably close to the batch result, and (c) handles non-confluent matchers. The dynamic-correlation-clustering theory (polylog recourse) lives under idealized $\pm1$ edge models and adversarial-edge assumptions that do not match ER's *attribute*-driven, rule-driven updates. Bridging dynamic-clustering theory to rule-evolving, learned-matcher ER is the open core; even the right *quality metric* for incremental drift is unsettled.

## 7. Current Research (as of June 2026)

- Fully-dynamic correlation clustering with deletions + bounded recourse, and its DP variants (Cohen-Addad, Lattanzi, Łącki) *(frontier — verify)*.
- Incremental ER under **matcher retraining / LLM-matcher updates** — quantifying and bounding cluster drift when the model changes *(frontier — verify)*.
- Provenance-aware incremental ER: re-deriving only clusters whose supporting rules changed.
- Continuous ER over streams with staleness SLAs.
- Active groups: Whang (KAIST), Garcia-Molina lineage (Stanford), Cohen-Addad/Lattanzi (Google), Rahm (Leipzig), Stoyanovich (NYU).

## 8. Future Work

- A unified competitive-analysis theory of incremental ER (recourse vs. approximation vs. update time) for *attribute/rule* updates, not just edge updates.
- Bounded-drift guarantees under matcher/rule evolution.
- Hybrid batch+incremental schedulers that trigger partial recomputation with certificates.
- Privacy-preserving and provenance-tracked incremental ER.

## 9. Key References

- **[Foundational]** Whang, Garcia-Molina. *Incremental Entity Resolution on Rules and Data.* VLDB Journal, 2014 (VLDB 2010).
- **[Foundational]** Benjelloun, Garcia-Molina, Menestrina, Su, Whang, Widom. *Swoosh: A Generic Approach to Entity Resolution.* VLDB Journal, 2009.
- **[SOTA]** Cohen-Addad, Lattanzi, Maggiori, Parotsidis. *Online and Consistent Correlation Clustering.* ICML, 2022.
- **[Foundational]** Henzinger, Krinninger, Nanongkai, Saranurak. *Unifying and Strengthening Hardness for Dynamic Problems via the Online Matrix–Vector Multiplication Conjecture.* STOC, 2015.
- **[SOTA]** Gruenheid, Dong, Srivastava. *Incremental Record Linkage.* PVLDB, 2014.
- **[Survey]** Christophides, Efthymiou, Palpanas, Papadakis, Stefanidis. *An Overview of End-to-End Entity Resolution for Big Data.* ACM Computing Surveys, 2021.

---
*Part of the [DBMS Research catalog](../../README.md).*
