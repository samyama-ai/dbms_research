# Multi-vector and late-interaction search

> **Topic:** Vector Databases & Similarity Search · **ID:** `28-vector-similarity-search/multi-vector-late-interaction` · **Status:** empirically-open

## 1. Problem Statement

In late-interaction retrieval (e.g., ColBERT), each document $D$ is represented not by one vector but by a *bag* of token embeddings $\{d_1,\dots,d_{m}\}$, and each query $Q$ by $\{q_1,\dots,q_{n}\}$. The relevance score is the **MaxSim** (Chamfer-style) similarity

$$S(Q,D) = \sum_{i=1}^{n} \max_{j \le m} \langle q_i, d_j\rangle.$$

The task is to return the top-$k$ documents by $S$ **without materializing all $n\times m$ interactions** for every document, over a corpus of $N$ documents with potentially billions of token vectors.

- **Optimization variant.** Build an index that answers top-$k$ MaxSim queries with high recall while bounding per-query distance computations and memory.
- **Decision/pruning variant.** Given partial per-query-token candidate lists, decide which documents can be safely pruned (their score upper bound is below the current $k$-th score).
- **Counting/aggregation challenge.** Unlike single-vector ANN, the score is a *set-to-set* aggregate, so standard top-$k$ ANN over individual token vectors only produces *candidates*, not final scores.

## 2. Mathematical Foundations

MaxSim is an asymmetric **Chamfer similarity** between point sets; it is not a metric and does not embed into a single inner product, so single-vector ANN is only a relaxation. The standard pipeline is **filter–then–rerank**: (1) for each query token $q_i$, ANN-retrieve candidate document tokens; (2) gather the union of their parent documents; (3) compute exact MaxSim on this candidate set. Correctness of pruning rests on an **upper-bound score**: if only some query tokens have found candidates for document $D$, bound the missing tokens' contributions by a per-token max (or by the global max inner product), giving a monotone, admissible bound enabling **threshold-algorithm**-style early termination (Fagin's TA/NRA family). The aggregation is a top-$k$ over a monotone scoring function of sorted lists, where TA is instance-optimal.

Cost is dominated by token-vector count $M=\sum_m \approx \bar m N$; compression matters. **Token pruning/pooling** reduces $m$ per document; **residual/product quantization** compresses each $d_j$. Theoretical handle: Chamfer/MaxSim relates to optimal-transport and the geometry of point-set similarity; sketching MaxSim has communication-complexity lower bounds.

## 3. State of the Art (SOTA)

- **Systems-SOTA.** *ColBERT* (Khattab–Zaharia, SIGIR 2020) and *ColBERTv2* (Santhanam et al., NAACL 2022) with residual compression and centroid-based candidate generation. *PLAID* (Santhanam et al., CIKM 2022) adds aggressive centroid-interaction pruning, cutting latency by ~7×. *EMVB* (Nardini et al., 2024) and *XTR* (Lee et al., NeurIPS 2023) — XTR retrains so that retrieved tokens directly approximate the final score, removing the gather/rerank stage. *MUVERA* (Dhulipala et al., 2024) builds *fixed-dimensional encodings (FDE)* that turn multi-vector MaxSim into single-vector MIPS with provable approximation, then re-ranks.
- **Theory-SOTA.** MUVERA gives the first $\epsilon$-approximation of Chamfer/MaxSim via single-vector reduction with dimension bounds; near-linear-time Chamfer approximation (Bakshi–Indyk–... line).

## 4. Upper Bound

MUVERA's FDE reduces top-$k$ MaxSim to MIPS over $O(\text{poly}(1/\epsilon))$-dimensional vectors with a $(1\pm\epsilon)$ guarantee on the Chamfer score, enabling any single-vector ANN as a black box plus a cheap exact re-rank — yielding sub-linear query time with bounded approximation. PLAID achieves order-of-magnitude latency reduction empirically via centroid pruning (no formal recall guarantee). Fagin's TA gives instance-optimal aggregation over the per-token sorted candidate lists when an admissible upper bound is available. Near-linear-time $(1+\epsilon)$ Chamfer-distance approximation algorithms bound the exact-scoring step.

## 5. Lower Bound

Exact MaxSim/Chamfer top-$k$ inherits high-dimensional NN hardness: under SETH, computing all-pairs Chamfer (or even a single closest set under Chamfer) in truly sub-quadratic time is conditionally hard, mirroring orthogonal-vectors / closest-pair lower bounds (Williams; Rubinstein). Communication-complexity bounds on sketching set similarity imply any single-vector encoding of a point set must lose information — so the FDE dimension cannot be $O(1)$ for arbitrary $\epsilon$. No data structure can answer exact set-to-set MaxSim top-$k$ in time independent of $\bar m$ for adversarial inputs.

## 6. The Gap

The reduction-to-MIPS approach (MUVERA) gives the first principled bridge, but the gap between its approximation guarantees and the *empirical* recall/latency of pruning systems (PLAID, EMVB) is uncharacterized; pruning heuristics lack guarantees, and the FDE approach lacks tight constants. It is **empirically open**: practitioners get excellent results from engineering (compression, centroid pruning, retraining as in XTR) but there is no unified theory of the recall–compute frontier for late interaction.

## 7. Current Research (as of June 2026)

- Single-vector reductions of MaxSim (MUVERA / FDE) and their tightening *(frontier — verify)*.
- Retrieval-aware training (XTR) that aligns retrieved tokens with final scoring to skip gather/rerank.
- Token pooling/pruning and learned per-document budget allocation to shrink $M$.
- Quantization tailored to MaxSim (residual + centroid interaction, EMVB bit-vector pre-filtering).
- Groups: Stanford (ColBERT/PLAID, Zaharia/Potts), Google DeepMind (XTR, MUVERA), academic IR (Pisa/Tonellotto, Nardini).

## 8. Future Work

- Provable recall guarantees for centroid-pruning pipelines.
- Optimal compression of token bags under a MaxSim distortion budget (rate–distortion for set similarity).
- Joint index supporting both single-vector and multi-vector queries with a shared cost model (links to ANN cost-model problem).
- Streaming/updatable multi-vector indexes.

## 9. Key References

- **[Foundational]** Omar Khattab, Matei Zaharia. *ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction over BERT.* SIGIR, 2020.
- **[SOTA]** Keshav Santhanam, Omar Khattab, Christopher Potts, Matei Zaharia. *PLAID: An Efficient Engine for Late Interaction Retrieval.* CIKM, 2022.
- **[SOTA]** Laxman Dhulipala, Majid Hadian, Rajesh Jayaram, Jason Lee, Vahab Mirrokni. *MUVERA: Multi-Vector Retrieval via Fixed Dimensional Encodings.* arXiv:2405.19504, 2024.
- **[SOTA]** Jinhyuk Lee et al. *Rethinking the Role of Token Retrieval in Multi-Vector Retrieval (XTR).* NeurIPS, 2023.
- **[Foundational]** Ronald Fagin, Amnon Lotem, Moni Naor. *Optimal Aggregation Algorithms for Middleware.* JCSS / PODS, 2003.
- **[Foundational]** Ryan Williams. *A New Algorithm for Optimal 2-Constraint Satisfaction and Its Implications.* Theoretical Computer Science, 2005.

---
*Part of the [DBMS Research catalog](../../README.md).*
