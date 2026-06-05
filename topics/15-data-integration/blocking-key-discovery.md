# Blocking Key Discovery Automation

> **Topic:** Data Integration & Schema Mapping · **ID:** `15-data-integration/blocking-key-discovery` · **Status:** empirically-open

## 1. Problem Statement

Entity resolution (ER) over $n$ records is quadratic ($\binom{n}{2}$ comparisons) if done naively. **Blocking** prunes the comparison space by grouping records into blocks so that only intra-block pairs are compared. A **blocking scheme** is a set of **blocking predicates** (e.g., "same Soundex(last\_name)", "same first 3 chars of zip") combined by conjunction/disjunction (a DNF of predicates). The problem: **automatically synthesize, from data (and limited labels), a blocking scheme that jointly optimizes**:

- **Pair Completeness / Recall** $\mathrm{PC} = \frac{\text{true matches retained}}{\text{total true matches}}$, and
- **Reduction Ratio** $\mathrm{RR} = 1 - \frac{\text{candidate pairs}}{\binom{n}{2}}$ (efficiency).

Variants: **decision** (does a scheme of size $\le k$ achieve $\mathrm{PC} \ge \alpha$ and $\mathrm{RR} \ge \beta$?), **optimization** (Pareto-optimal PC/RR), **supervised vs. unsupervised** (with/without labeled match pairs), and **learned/embedding-based blocking** (DeepBlocker) versus rule/key-based.

## 2. Mathematical Foundations

A blocking predicate is a Boolean function $p_i: R \times R \to \{0,1\}$. A scheme is a **DNF** $f = \bigvee_j \bigwedge_{i \in C_j} p_i$. Learning $f$ from labeled matching/non-matching pairs is exactly **learning a DNF / disjunction of conjunctions** — connecting to **PAC learning** and to **(weighted) Set Cover**: each conjunction "covers" the true-match pairs it keeps while "paying" the non-match pairs it admits. Bilenko–Kamath–Mooney (ICDM 2006) cast optimal blocking-scheme learning as a **red-blue set cover** / approximate set cover, which is the source of its hardness.

Sample-complexity is governed by the **VC dimension** of the predicate class: with VC dimension $d$, $O\!\big(\frac{d + \log(1/\delta)}{\varepsilon}\big)$ labeled pairs suffice to estimate PC/RR within $\varepsilon$. The PC/RR trade-off is a **bi-objective** problem with no single optimum — only a **Pareto frontier**; scalarizing (e.g., maximize PC s.t. RR $\ge \beta$) yields the constrained form. Learned blocking replaces hand predicates with **nearest-neighbor in an embedding space** (then ANN such as HNSW retrieves candidates), shifting the problem to representation learning + ANN recall.

## 3. State of the Art (SOTA)

- **Algorithmic-SOTA.** **Bilenko et al.** (ICDM 2006) — learning blocking schemes via set cover (BSL/ApproxRBSetCover). **Michelson–Knoblock** (AAAI 2006) — Blocking Scheme Learner. **Kejriwal–Miranker** — *unsupervised* blocking-scheme learning using a weak training-set generator.
- **Systems-SOTA.** **DeepBlocker** (Thirumuruganathan et al., PVLDB 2021) — self-supervised, embedding-based blocking, strong PC at high RR without labels. **Sparkly** (Paganelli et al., 2023) and **DeepER/AutoBlock** lines use TF-IDF + ANN (HNSW/FAISS) and learned encoders. Toolkits: **Magellan**, **py\_entitymatching**, **JedAI** (meta-blocking, comparison cleaning).

## 4. Upper Bound

For the **set-cover formulation** of scheme learning, the greedy algorithm gives an $O(\ln m)$-approximation to the cost (number of non-matches admitted) for a fixed recall target, $m$ = number of true-match pairs to cover, in the **RAM model**. Building blocks themselves: for embedding/ANN blocking, **HNSW** (Malkov–Yashunin) gives empirically $O(\log n)$-ish query time with high recall, so candidate generation is near-linear $\tilde{O}(n)$ in practice. Meta-blocking prunes the block graph in $O(|\text{edges}|)$. No algorithm guarantees the *true* Pareto-optimal scheme in polynomial time.

## 5. Lower Bound

- **NP-hardness:** optimal blocking-scheme learning is **NP-hard** via reduction from (red-blue / partial) **Set Cover** (Bilenko et al.); the DNF-minimization underneath is also NP-hard.
- **Inapproximability:** inheriting Set Cover, the recall-constrained cost objective is **NP-hard to approximate better than $(1-o(1))\ln n$** (Dinur–Steurer), so greedy's $\ln$ factor is essentially tight for the worst case.
- **Information-theoretic:** without labels, no algorithm can certify PC because true matches are unknown — the unsupervised setting has **no worst-case recall guarantee** (an info-theoretic, not computational, barrier). This — combined with the absence of standard benchmarks where guarantees transfer — is why the status is **empirically-open**: methods are compared by measured PC/RR on benchmarks, not by proven bounds.

## 6. The Gap

The **theory gap** (set-cover hardness vs. $\ln n$ greedy) is essentially **closed** for the supervised, fixed-recall scalarization. The **open** part is empirical and definitional: (i) no method has a *distribution-free* guarantee on the **Pareto frontier**; (ii) learned/embedding blockers (DeepBlocker) win on benchmarks but offer **no recall certificate**; (iii) cross-domain generalization and the right objective (calibrated PC vs. downstream F1) are unsettled. Closing it requires either provable recall guarantees for learned blockers or a hardness result explaining their benchmark-only evaluation.

## 7. Current Research (as of June 2026)

Active: **self-supervised and LLM/embedding blocking** with ANN backends, and **blocking-aware ANN index tuning** (recall/RR via HNSW parameters). *(frontier — verify)* 2024–2025 work explores **LLM-generated blocking keys** and **schema-agnostic, in-context blocking** for heterogeneous/web data, plus **learned cost models** to choose between rule-based and embedding-based blocking per dataset. *(frontier — verify)* Benchmarks: the **DeepMatcher / Magellan** suites and newer **WDC / Alaska** product corpora. Groups: Doan/Govind/Konda (Magellan), Christophides–Papadakis (JedAI/meta-blocking), Thirumuruganathan, Papadakis–Palpanas.

## 8. Future Work

- Distribution-free or PAC-style **recall certificates** for learned/embedding blockers.
- Principled **Pareto-frontier** algorithms (not single scalarizations).
- Unified **rule + embedding** blocking with a learned router and shared cost model.
- Streaming / incremental blocking under data drift; blocking for multi-source (>2) ER.

## 9. Key References

- **[Foundational]** M. Bilenko, B. Kamath, R. Mooney. *Adaptive Blocking: Learning to Scale Up Record Linkage.* ICDM, 2006.
- **[Foundational]** M. Michelson, C. Knoblock. *Learning Blocking Schemes for Record Linkage.* AAAI, 2006.
- **[SOTA]** S. Thirumuruganathan, et al. *Deep Learning for Blocking in Entity Matching: A Design Space Exploration (DeepBlocker).* PVLDB, 2021.
- **[SOTA]** Y. Malkov, D. Yashunin. *Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs (HNSW).* IEEE TPAMI, 2020.
- **[SOTA]** G. Papadakis, D. Skoutas, E. Thanos, T. Palpanas. *Blocking and Filtering Techniques for Entity Resolution: A Survey.* ACM Computing Surveys, 2020.
- **[Survey]** P. Christen. *Data Matching: Concepts and Techniques for Record Linkage, Entity Resolution, and Duplicate Detection.* Springer, 2012.

---
*Part of the [DBMS Research catalog](../../README.md).*
