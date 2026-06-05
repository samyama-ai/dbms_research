# Privacy and Access-Aware Schema Decomposition

> **Topic:** Schema Design & Normalization · **ID:** `34-schema-design-normalization/privacy-aware-decomposition` · **Status:** open

## 1. Problem Statement
Given a relation/schema $R(A_1,\dots,A_n)$, a set of **sensitive associations** $\mathcal{C} = \{c_1,\dots,c_m\}$ (each $c_j \subseteq \{A_1,\dots,A_n\}$ is a set of attributes that must not appear together in the clear at any single storage site), and a workload/utility objective, **decompose** $R$ into fragments $F_1,\dots,F_k$ (vertical fragmentation, possibly with encryption) such that no fragment exposes a full sensitive association, while query utility/performance is maximized.

- **Decision variant:** Does a decomposition exist that *covers* (breaks) every constraint $c_j$ using at most $k$ fragments / sites?
- **Optimization variant:** Among valid decompositions, minimize query cost (or maximize visibility of non-sensitive co-locations) — a weighted fragmentation objective.
- **Counting variant:** How many minimal valid fragmentations exist (relevant to randomized/diverse placement)?

This generalizes BCNF-style decomposition (driven by FDs) to decomposition *driven by confidentiality constraints*, and connects to access control: fragments map to clearance levels so each role sees only permitted attribute combinations.

## 2. Mathematical Foundations
A confidentiality constraint $c$ is a subset of attributes; a fragmentation $\mathcal{F}=\{F_1,\dots,F_k\}$ **satisfies** $\mathcal{C}$ iff for every $c\in\mathcal{C}$ and every fragment $F_i$, $c \not\subseteq F_i$ (no fragment is a superset of a sensitive set). Singleton constraints $\{A\}$ force attribute $A$ to be encrypted/omitted. This is exactly a **set-cover / hitting-set** structure: each fragment must "hit" (split) every constraint, and minimizing fragments is **minimum vertical fragmentation**.

Lossless reconstruction requires a common **tuple identifier (tid)** across fragments so $R = F_1 \Join_{tid} \cdots \Join_{tid} F_k$; this re-association is itself a privacy risk if an adversary can join. Inference channels arise from FDs: if $A\to B$ holds and $A,C$ are co-located while $B,C$ are sensitive, the FD reconstructs the sensitive pair — so the model must close $\mathcal{C}$ under **dependency-aware inference** (the *chase* of constraints against FDs).

Stronger privacy targets formalize utility/privacy via $\ell$-diversity, $t$-closeness, or **$\varepsilon$-differential privacy** on released fragments; the decomposition then trades off mutual information $I(\text{fragment};\text{sensitive})$ against query utility, often a **submodular coverage** maximization under a privacy budget.

## 3. State of the Art (SOTA)
**Theory/Systems-SOTA.** The canonical line is **fragmentation for confidentiality** by **Aggarwal et al. (CIDR 2005)** — two non-communicating servers — and **Ciriani, De Capitani di Vimercati, Foresti, Jajodia, Paraboschi, Samarati** (ESORICS/TODS 2007–2010): *"Fragmentation and Encryption to Enforce Privacy in Data Storage"* and *"Combining Fragmentation and Encryption."* They give minimal-fragmentation heuristics and the "departing-from-encryption" model. **CryptDB** (Popa et al., SOSP 2011) takes the orthogonal encryption-layer route; **Cipherbase**, **Always Encrypted**, and TEE-based stores (**EnclaveDB**) are the systems-SOTA for confidential query processing. Access-control-aware design connects to **disclosure control** and **k-anonymity** (Sweeney, 2002).

**Theory-SOTA.** Minimal fragmentation is framed as a graph-coloring/set-cover optimization; approximation via greedy set cover gives the best known general guarantee.

## 4. Upper Bound
Finding *a* valid fragmentation is easy (place every attribute in its own fragment trivially satisfies all multi-attribute constraints). The hard part is **minimizing fragments / maximizing utility**: greedy set-cover-style heuristics give an **$O(\ln m)$**-approximation for minimum-fragment cover (m = #constraints). Utility maximization under a fragment-count budget, when the utility is **monotone submodular**, admits the classic **$(1-1/e)$** greedy guarantee (Nemhauser–Wolsey–Fisher). Dependency closure adds a polynomial chase step per candidate.

## 5. Lower Bound
Minimum vertical fragmentation under confidentiality constraints is **NP-hard** — it embeds **minimum hitting set / set cover** (each constraint is a set to be broken), and set cover is **NP-hard and not approximable below $(1-o(1))\ln n$** unless $\mathsf{P}=\mathsf{NP}$ (Dinur–Steurer, 2014), matching the greedy upper bound. With FD-induced inference channels the validity test interacts with FD implication; full inference-safe decomposition over FD+IND constraints inherits **undecidability** (Chandra–Vardi) in the unrestricted case. Information-theoretically, no fragmentation without encryption can hide a singleton sensitive attribute that must still be queryable — a hard impossibility forcing crypto/TEE.

## 6. The Gap
The *feasibility* question is closed (poly-time) and the minimization matches set-cover bounds. The genuine open gap is **utility-optimal, inference-safe** decomposition: we lack tight approximations once realistic query-cost utility and FD/probabilistic inference channels are both modeled, and we lack a unified theory connecting fragmentation, encryption, and differential privacy under one optimization. This is open — most systems pick one mechanism and bound only that.

## 7. Current Research (as of June 2026)
Active directions: (1) **TEE + fragmentation hybrids** and oblivious query processing that minimize what leaves the enclave *(frontier — verify)*; (2) differential-privacy-aware schema/view design, choosing decompositions that bound per-query privacy loss; (3) access-control-aware physical design for multi-tenant cloud DBs; (4) defending against *re-association/linkage* attacks across fragments using diversity. Groups: Samarati / De Capitani di Vimercati (Milan), Kantarcioglu (UT Dallas), Machanavajjhala (Duke, DP), and confidential-computing efforts (Microsoft Research, Berkeley RISE successors).

## 8. Future Work
- A single optimization framework unifying fragmentation, encryption, TEE, and DP with provable utility/privacy bounds.
- Inference-channel-safe decomposition over decidable FD/IND fragments with guarantees.
- Workload-adaptive re-fragmentation as access patterns and sensitivity labels evolve.
- Benchmarks pairing real schemas with realistic sensitive-association sets.

## 9. Key References
- **[Foundational]** Aggarwal, G., et al. *Two Can Keep a Secret: A Distributed Architecture for Secure Database Services.* CIDR, 2005.
- **[Foundational]** Ciriani, V., De Capitani di Vimercati, S., Foresti, S., Jajodia, S., Paraboschi, S., Samarati, P. *Combining Fragmentation and Encryption to Protect Privacy in Data Storage.* ACM TISSEC, 2010.
- **[SOTA]** Popa, R.A., Redfield, C., Zeldovich, N., Balakrishnan, H. *CryptDB: Protecting Confidentiality with Encrypted Query Processing.* SOSP, 2011.
- **[Foundational]** Sweeney, L. *k-Anonymity: A Model for Protecting Privacy.* IJUFKS, 2002.
- **[Foundational]** Dwork, C. *Differential Privacy.* ICALP, 2006.
- **[Foundational]** Dinur, I., Steurer, D. *Analytical Approach to Parallel Repetition (tight Set Cover hardness).* STOC, 2014.

---
*Part of the [DBMS Research catalog](../../README.md).*
