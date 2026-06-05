# Blocking with Recall Guarantees

> **Topic:** Data Cleaning & Quality · **ID:** `16-data-cleaning-quality/blocking-recall-guarantees` · **Status:** partially-solved

## 1. Problem Statement

Entity resolution (ER) over $n$ records cannot afford the $\binom{n}{2}$ pairwise matcher calls. **Blocking** produces a candidate set $C \subseteq \binom{R}{2}$ such that the expensive matcher is only run on $C$. Let $M \subseteq \binom{R}{2}$ be the true matching pairs (unknown). Define:
- **Pair completeness / recall** $\mathrm{PC} = |C \cap M| / |M|$,
- **Reduction ratio** $\mathrm{RR} = 1 - |C| / \binom{n}{2}$.

**Problem.** Design a blocking scheme that guarantees $\mathrm{PC} \ge 1-\delta$ (provably, not just empirically) while keeping $|C| = o(n^2)$, ideally $\tilde O(n)$.
- **Decision:** does scheme $\mathcal{B}$ admit recall $\ge 1-\delta$ under a stated similarity/metric assumption?
- **Optimization:** minimize $|C|$ subject to a recall guarantee.
- The crux is the *guarantee*: empirical recall on a labeled sample is easy; a **provable** bound over the unlabeled population is the open hard part.

## 2. Mathematical Foundations

Assume matching pairs are *near* under a similarity/metric $\sigma$: $M \subseteq \{(x,y): \sigma(x,y) \ge \tau\}$. Then blocking is the **near-neighbor / similarity-join** problem, and recall guarantees inherit from **Locality-Sensitive Hashing (LSH)**: a family is $(\tau, c\tau, p_1, p_2)$-sensitive if near pairs collide w.p. $\ge p_1$ and far pairs w.p. $\le p_2$. With $L$ bands of $k$ hashes, a $\tau$-near pair is recalled w.p. $1-(1-p_1^k)^L \ge 1-\delta$, giving a **distribution-free recall guarantee** with cost $L\cdot k$ hashes and expected candidate set $|C| = O(n + n^2 p_2^k L)$. The LSH exponent $\rho = \log p_1/\log p_2 < 1$ yields sublinear query / subquadratic total work: $\tilde O(n^{1+\rho})$.

The guarantee is **only as valid as the near-pair assumption** ($M$ confined to the $\tau$-ball). Where matching is non-metric, recall must instead be controlled by **probabilistic sampling**: a sampled, labeled subset of size $m = O(\delta^{-2}\log(1/\beta))$ bounds population recall within $\delta$ w.p. $1-\beta$ (binomial concentration), but this is a statistical, not adversarial, guarantee. VC-dimension of the blocking-key class controls uniform convergence of empirical-to-true recall.

## 3. State of the Art (SOTA)

- **Sorted Neighborhood** (Hernández, Stolfo, *SIGMOD 1995*) and **canopy clustering** (McCallum, Nigam, Ungar, *KDD 2000*) — classic blocking; recall is heuristic.
- **LSH-based blocking** (e.g., MinHash for Jaccard, *Broder 1997*) — the theory-SOTA for provable recall under metric/similarity assumptions.
- **Meta-blocking** (Papadakis et al., *TKDE 2014*) — graph-based pruning of redundant comparisons from schema-agnostic blocks; systems-SOTA for token blocking quality.
- **DeepBlocker** (Thirumuruganathan et al., *VLDB 2021*) and **Sudowoodo / Blocker via dense embeddings + ANN** (2022–2023) — learned blocking using embeddings + HNSW/IVF, strong empirical recall but guarantees inherited only from ANN.
- **pyJedAI / JedAI** toolkits consolidate blocking + meta-blocking pipelines.

## 4. Upper Bound

Under a $(\tau,c\tau,p_1,p_2)$-LSH family, total candidate-generation time is $\tilde O(n^{1+\rho})$ with $\rho<1$ and recall $\ge 1-\delta$ achievable by tuning $(k,L)$; space $\tilde O(n^{1+\rho})$. For Jaccard/MinHash, $\rho \approx \log(1/p)$ behavior gives strongly subquadratic cost. With the sampling-based statistical guarantee, any blocker can certify population recall $\ge 1-\delta$ using $O(\delta^{-2}\log(1/\beta))$ labeled pairs — additive cost independent of $n$.

## 5. Lower Bound

- **ANN hardness:** for high-dimensional near-neighbor (Hamming/Euclidean), the LSH exponent $\rho \ge 1/(2c-1) - o(1)$ is **optimal** for hashing-based methods (O'Donnell–Wu–Zhou lower bound), and exact near-neighbor inherits **OVH/SETH** conditional hardness — no strongly subquadratic exact similarity join for general high-dimensional data unless SETH fails.
- **Distribution-free impossibility:** without *any* metric/near assumption on $M$, no sub-quadratic blocker can guarantee recall — an adversary can place a matching pair in any block boundary; guarantees are impossible in the fully adversarial model (a covering/information lower bound).
- **Communication:** in distributed blocking, achieving recall $1$ with low candidate sets has communication lower bounds via set-disjointness reductions.

## 6. The Gap

Under a clean metric assumption the gap is essentially **closed** (LSH upper bound meets the $\rho$ lower bound). The genuinely open part is **non-metric / learned-similarity** matching: embedding-ANN blockers give excellent empirical recall but no population guarantee, while the only provable route (labeled sampling) certifies recall *post hoc* rather than by construction and assumes the sample distribution matches deployment. Bridging learned blocking to provable recall — i.e., bounding the matcher-induced similarity by a metric admitting LSH, or learning an LSH family with certified $p_1,p_2$ — is the unresolved core.

## 7. Current Research (as of June 2026)

- Learning LSH/embedding families with **certified collision probabilities** for matching pairs *(frontier — verify)*.
- Calibrated, distribution-shift-robust recall certificates for embedding-ANN blockers (conformal-prediction-style guarantees) *(frontier — verify)*.
- LLM-assisted blocking-key generation with recall auditing.
- Active groups: Papadakis/Palpanas (Athens/Paris, JedAI), Christen (ANU), Doan/Govind/Konda (Wisconsin, Magellan), Tang/Ouzzani (QCRI), Thirumuruganathan.

## 8. Future Work

- Provable recall for learned, non-metric matchers (conformal or PAC certificates under bounded shift).
- Joint optimization of blocking + matching to hit a target end-to-end recall with minimal cost.
- Incremental/streaming blocking certificates as new records arrive.
- Privacy-preserving blocking with recall guarantees (secure ER).

## 9. Key References

- **[Foundational]** Hernández, Stolfo. *The Merge/Purge Problem for Large Databases (Sorted Neighborhood).* SIGMOD, 1995. — [DOI](https://doi.org/10.1145/223784.223807)
- **[Foundational]** McCallum, Nigam, Ungar. *Efficient Clustering of High-Dimensional Data Sets with Application to Reference Matching (Canopies).* KDD, 2000. — [DOI](https://doi.org/10.1145/347090.347123)
- **[Foundational]** Indyk, Motwani. *Approximate Nearest Neighbors: Towards Removing the Curse of Dimensionality (LSH).* STOC, 1998. — [DOI](https://doi.org/10.1145/276698.276876)
- **[SOTA]** Papadakis, Koutrika, Palpanas, Nejdl. *Meta-Blocking: Taking Entity Resolution to the Next Level.* IEEE TKDE, 2014. — [DOI](https://doi.org/10.1109/TKDE.2013.54)
- **[SOTA]** Thirumuruganathan et al. *DeepBlocker: Deep Learning for Blocking in Entity Matching.* PVLDB, 2021. — [DOI](https://doi.org/10.14778/3476249.3476294)
- **[Survey]** Christen. *Data Matching: Concepts and Techniques for Record Linkage, Entity Resolution, and Duplicate Detection.* Springer, 2012. — [DOI](https://doi.org/10.1007/978-3-642-31164-2)

## 10. Worked Example

Take MinHash LSH for Jaccard similarity. Suppose true matching pairs have similarity $s \ge \tau = 0.8$, so a single MinHash agrees with probability $p_1 = 0.8$. We want recall $\ge 1-\delta = 0.95$.

Use the AND-OR construction: $L$ bands of $k$ hashes each. A pair is a candidate iff some band matches all $k$ hashes. Recall probability is
$$1-(1-p_1^{\,k})^{L}.$$

Try $k = 3$, $L = 10$: $p_1^k = 0.8^3 = 0.512$, so recall $= 1-(1-0.512)^{10} = 1-0.488^{10} \approx 1 - 0.00072 = 0.9993 \ge 0.95$. Good.

Now check false-positive control: a far pair at $s = 0.3$ has $p_2 = 0.3$, collision prob $1-(1-0.3^3)^{10} = 1-(0.973)^{10} \approx 0.238$. With $n=10^5$ records, the $\binom{n}{2}\approx 5\times 10^9$ pairs shrink to roughly $0.238 \times$ that for genuinely-far pairs — still large, so one tunes $k$ up. Raising $k$ shrinks both recall and candidates; the LSH exponent $\rho = \log p_1/\log p_2 = \log 0.8/\log 0.3 \approx 0.185$ gives total cost $\tilde O(n^{1.185})$, far below $n^2$.

---
*Part of the [DBMS Research catalog](../../README.md).*
