# Holistic Many-to-Many Schema Matching

> **Topic:** Data Integration & Schema Mapping · **ID:** `15-data-integration/holistic-schema-matching` · **Status:** empirically-open

## 1. Problem Statement

Classical schema matching is **pairwise**: given two schemas $S, T$, output element correspondences. **Holistic** matching takes a *corpus* of $N$ heterogeneous schemas $\{S_1, \dots, S_N\}$ (web tables, forms, open-data CSVs, enterprise schemas — often hundreds to millions) and computes a **joint** matching: a clustering of all attributes across all schemas into semantic concepts (a "mediated schema" / attribute clusters), exploiting cross-schema statistical signal rather than treating each pair independently.

- **Optimization variant:** Partition the set of all attributes $A = \bigcup_i \mathrm{attrs}(S_i)$ into clusters maximizing within-cluster semantic coherence and respecting structural constraints (attributes from the *same* schema usually shouldn't merge), e.g. a **correlation-clustering** or **constrained k-partition** objective.
- **Calibrated-confidence variant:** Output for each correspondence a *calibrated* probability, not just a score, so downstream integration can reason about uncertainty.
- **Scalability variant:** Do this at **web scale** ($N$ large, sublinear in pairwise comparisons) with bounded error.

"Solving" (here) means a system that matches a large corpus jointly with empirically high precision/recall *and* calibrated confidence, scaling sub-quadratically in $N$ — currently achieved only partially and without guarantees.

## 2. Mathematical Foundations

Model attributes as nodes; a learned similarity $w_{uv} \in [-1,1]$ (positive = likely same concept) on pairs yields a signed graph. The joint objective is **correlation clustering**: minimize disagreements $\sum_{u,v} [\,\mathbf{1}[u\sim v]\,(1-w^+_{uv}) + \mathbf{1}[u\not\sim v]\,w^+_{uv}\,]$, NP-hard with the best constant-factor approximations known. **Holistic** signals add: *co-occurrence statistics* (attributes that never co-occur in a schema are more likely synonyms — the basis of **DCM / statistical schema matching**, He–Chang), and *correlation mining* over the corpus. Calibration is a statistical-learning notion: a matcher is **calibrated** if among correspondences output with confidence $p$, a fraction $p$ are truly correct; measured by **ECE** (expected calibration error) and reliability diagrams. Embedding-based variants place attributes in $\mathbb{R}^d$ and reduce matching to **nearest-neighbor / metric clustering**, invoking the AGM-style blow-up only at the structural-mapping stage, not matching.

## 3. State of the Art (SOTA)

**Foundational holistic theory.** He, Chang (SIGMOD 2003, *Statistical Schema Matching across Web Query Interfaces*) and the **DCM framework** established corpus-level co-occurrence matching. Madhavan et al. (*Corpus-based Schema Matching*, ICDE 2005) used a schema corpus as background knowledge. **Systems SOTA.** Google's **WebTables / Octopus / InfoGather** (Cafarella, Halevy; Yakout et al., SIGMOD 2012) match millions of web tables; modern learned matchers — **EmbDI** (Cappuzzo et al., SIGMOD 2020), **DeepMatcher**-style and especially **Valentine** (Koutras et al., ICDE 2021, a benchmark/SOTA survey of matchers) and LLM/foundation-model column-type and matching systems (e.g. Starmie, RECA, table-foundation models) — are the empirical frontier *(frontier — verify)*. None provide formal calibration or recall guarantees at corpus scale.

## 4. Upper Bound

The joint clustering relaxation (correlation clustering) admits a **$2.06$-approximation** via LP rounding (Chawla–Makarychev–Schramm–Yaroslavtsev, STOC 2015) for the min-disagreement objective on complete signed graphs; pivot-based combinatorial algorithms give a **3-approximation** (Ailon–Charikar–Newman, JACM 2008) in near-linear time. With LSH/embedding blocking, candidate generation is **sub-quadratic** ($\tilde{O}(N)$ to $\tilde{O}(N^{1.x})$) in the number of attributes. So the *clustering* step has constant-factor approximation guarantees; the *matching-signal* step (producing $w_{uv}$) is heuristic/learned with no accuracy guarantee. Model: approximation algorithms (RAM), under the assumption that similarity weights are given.

## 5. Lower Bound

Correlation clustering (min-disagreement, general weights) is **APX-hard** — NP-hard to approximate within some constant (Charikar–Guruswami–Wirth, FOCS 2003); on signed complete graphs it remains NP-hard. These bound the *clustering* step. For the *matching accuracy* itself there is **no nontrivial lower bound** because there is no agreed information model of the input signal — see the companion problem **Schema Matching Quality Lower Bounds**. Calibration adds a learning-theoretic obstruction: distribution shift between training corpora and the target corpus makes worst-case calibration impossible without assumptions. Model: APX-hardness (NP) for clustering; the accuracy lower bound is open / informal.

## 6. The Gap

This problem is **empirically-open**: the *algorithmic* core (joint clustering) has tight-ish constant-factor approximations, but the end-to-end task lacks any theory connecting input signal quality to output matching accuracy, and lacks any guarantee of calibration at scale. The gap is between strong systems-level empirical results on benchmarks (Valentine) and the **absence of guarantees** — we cannot certify recall, precision, or calibration on an unseen corpus. Closing it requires (a) an information-theoretic accuracy model (open elsewhere in this topic) and (b) provably calibrated joint inference.

## 7. Current Research (as of June 2026)

Directions: (1) **foundation-model / LLM** column and schema matchers with retrieval and verification, and table-representation models pretrained on millions of tables *(frontier — verify)*; (2) **calibration** of matcher outputs (temperature scaling, conformal prediction over correspondences) to get coverage guarantees *(frontier — verify)*; (3) benchmark-driven evaluation continuing the **Valentine** line, plus open-data lake matching (Auctus, Starmie); (4) graph/co-occurrence holistic methods revisited with GNNs. Groups: Halevy/Cafarella lineage, Miller (Data Lakes, Northeastern), Koutras–Bonifati–Fundulaki, Cappuzzo–Papotti.

## 8. Future Work

An information-theoretic accuracy model that makes "guaranteed recall" meaningful; conformal/PAC-calibrated correspondence confidence at corpus scale; joint matching that *propagates* uncertainty into downstream p-mappings; truly sublinear corpus matching with bounded error; and standardized large-scale, drift-aware benchmarks beyond the current pairwise-dominated suites.

## 9. Key References

- **[Foundational]** He, Chang. *Statistical Schema Matching across Web Query Interfaces.* SIGMOD 2003.
- **[Foundational]** Madhavan, Bernstein, Doan, Halevy. *Corpus-based Schema Matching.* ICDE 2005.
- **[SOTA]** Koutras, Siachamis, Ionescu, et al. *Valentine: Evaluating Matching Techniques for Dataset Discovery.* ICDE 2021.
- **[SOTA]** Cappuzzo, Papotti, Thirumuruganathan. *Creating Embeddings of Heterogeneous Relational Datasets (EmbDI).* SIGMOD 2020.
- **[Foundational]** Ailon, Charikar, Newman. *Aggregating Inconsistent Information: Correlation Clustering.* JACM 2008.
- **[Survey]** Rahm, Bernstein. *A Survey of Approaches to Automatic Schema Matching.* VLDB Journal, 2001.

---
*Part of the [DBMS Research catalog](../../README.md).*
