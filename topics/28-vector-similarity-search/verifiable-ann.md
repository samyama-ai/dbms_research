# Authenticated/verifiable ANN results

> **Topic:** Vector Databases & Similarity Search · **ID:** `28-vector-similarity-search/verifiable-ann` · **Status:** open

## 1. Problem Statement

A client outsources a vector dataset $P \subseteq \mathbb{R}^d$ (and an ANN index) to an untrusted server, then issues query $q$ and receives a claimed approximate top-$k$ answer $S$. The server must return a **succinct proof** $\pi$ that convinces the client (or any verifier holding a short digest of $P$) that $S$ is a *correct* answer under a stated correctness predicate, while the server cannot make the client accept a wrong $S$ except with negligible probability. Correctness predicates of interest: **exact top-$k$** (the $k$ truly nearest); **$(1+\varepsilon)$-approximate top-$k$** (each returned point within $(1+\varepsilon)$ of the true $i$-th distance); and **completeness** (no qualifying point was omitted) and **soundness** (no spurious point inserted). Variants: **authenticated data structures (ADS)** with a trusted-digest model; **SNARK-based** proofs in the no-trusted-setup-needed model; and the **interactive** verification variant. Goal: proof size and verification time **sublinear in $n$**, ideally $\mathrm{polylog}(n)$ or independent of $n$.

## 2. Mathematical Foundations

The setting is **verifiable computation** and **authenticated data structures**. A digest is a **Merkle/vector commitment** $\mathrm{com}(P)$; correctness reduces to proving a NP statement: "there exist $k$ points in the committed set whose distances to $q$ are the $k$ smallest, and the gap to the $(k{+}1)$-th certifies the approximation." Two regimes: (1) **ADS with completeness proofs** — geometric certificates (e.g. covering balls / separating hyperplanes proving no closer point exists) Merkle-authenticated; (2) **succinct arguments** — encode the index traversal + distance comparisons as an arithmetic circuit and produce a **SNARK** (KZG/PLONK/STARK), giving proof size $O(1)$ or $\mathrm{polylog}$ and verification $\mathrm{polylog}(n)$, at high prover cost. The hard part is the **completeness** half: certifying *absence* of a closer point requires either scanning (defeating sublinearity) or a geometric witness (a partition of space proving the unsearched region is empty of closer points), which is the ANN analogue of authenticated range/skyline queries.

## 3. State of the Art (SOTA)

- **Authenticated queries (classical):** Merkle-tree ADS for range, kNN, and skyline in low dimension (Yang, Papadias, Papadopoulos, Kalnis — "authenticated kNN", 2009 era) using Voronoi/partition certificates; these blow up exponentially in $d$.
- **Verifiable ML / inference:** zkSNARK proofs of neural-network inference (e.g. zkCNN, 2021; later zkLLM-style work) show feasibility of proving large computations, transferable to proving a distance-comparison circuit.
- **Vector-search specific:** essentially **no production system** offers verifiable ANN; commercial vector DBs are trusted. Academic prototypes for verifiable similarity search exist only for exact, low-dimensional, or top-1 cases *(frontier — verify)*.

## 4. Upper Bound

For **exact** authenticated kNN in low/fixed dimension, Voronoi-partition ADS gives proof size and verification $O(k \cdot 2^{O(d)} \log n)$ — sublinear in $n$ but exponential in $d$. For **approximate** top-$k$ via SNARK over a graph/IVF traversal: proof size $O(1)$–$\mathrm{polylog}(n)$ and verification $\mathrm{polylog}(n)$ in the SNARK model, but prover time is $\tilde O(C)$ where $C$ is the circuit size of the (quantized) distance computations along the traversal — practically heavy. No scheme simultaneously achieves $\mathrm{poly}(d)$, sublinear proof, *and* practical prover cost.

## 5. Lower Bound

The completeness requirement inherits ANN's **curse of dimensionality**: any *certificate-based* proof of "no closer point exists" in high dimension that avoids touching $\Omega(n)$ data faces the same barriers as exact high-dimensional NN (no $\mathrm{poly}(n,d)$-space, sublinear-query exact structure under SETH-style hardness, Rubinstein 2018) — the proof cannot be cheaper than verifying the search, and exact search is conditionally hard. Cryptographically, SNARK proof size is lower-bounded by soundness requirements but is independent of $n$; the binding constraint is therefore **prover cost** (circuit size $\ge$ work to certify the answer) and, for completeness, the **geometric witness size**, which can be $\Omega(n)$ in the worst high-dimensional case.

## 6. The Gap

**Genuinely open.** Soundness (proving returned points are genuinely close) is achievable via Merkle-authenticated distance recomputation. **Completeness** (proving nothing closer was skipped) is the open core: in high dimension there is no known sublinear-size, $\mathrm{poly}(d)$ geometric certificate, and SNARK approaches push the cost into an enormous prover circuit. The gap between (a) cheap soundness-only proofs and (b) full sound-and-complete approximate top-$k$ proofs with practical prover cost is wide and unaddressed.

## 7. Current Research (as of June 2026)

- zkSNARK proofs of ANN traversal (proving a fixed beam-search path was executed faithfully) — gives *path-faithfulness* but not *global optimality* of the answer *(frontier — verify)*.
- Probabilistic / approximate completeness: accept proofs guaranteeing recall $\ge 1-\delta$ via sampled audits rather than exact certificates.
- TEE-assisted verifiable vector search (attested enclaves) as a weaker but deployable trust model.
- Groups: applied-crypto teams bridging zkML and databases; classical ADS lineage (Papadopoulos, Papadias).

## 8. Future Work

- Sublinear-size completeness certificates for approximate top-$k$ in high dimension (or a hardness proof ruling them out).
- Recall-bounded probabilistic verification with rigorous soundness/recall guarantees.
- SNARK-friendly index designs minimizing prover circuit size.
- Updatable/streaming authenticated ANN under insertions and deletions.

## 9. Key References

- **[Foundational]** Tamassia, R. *Authenticated Data Structures.* ESA, 2003.
- **[Foundational]** Yang, Y., Papadias, D., Papadopoulos, S., Kalnis, P. *Authenticated Join Processing / Spatial Queries in Outsourced Databases.* SIGMOD, 2009.
- **[SOTA]** Liu, T., Xie, X., Zhang, Y. *zkCNN: Zero Knowledge Proofs for Convolutional Neural Network Predictions.* CCS, 2021.
- **[Lower bound]** Rubinstein, A. *Hardness of Approximate Nearest Neighbor Search.* STOC, 2018.
- **[Survey]** Setty, S., et al. *Survey/Foundations of Succinct Arguments (SNARKs/STARKs).* (e.g. Spartan, CCS 2020; and STARK transparency work).

---
*Part of the [DBMS Research catalog](../../README.md).*
