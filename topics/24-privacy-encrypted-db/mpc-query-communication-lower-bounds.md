# Communication Lower Bounds for MPC Queries

> **Topic:** Privacy & Encrypted Databases · **ID:** `24-privacy-encrypted-db/mpc-query-communication-lower-bounds` · **Status:** open

## 1. Problem Statement
Establish **tight communication and round lower bounds** for *securely* evaluating relational-algebra and aggregation queries under MPC. Given parties holding private relations and an ideal functionality $\mathcal{F}_Q$ for a query $Q$ (selection, projection, join, group-by, aggregation), prove lower bounds on the **total bits exchanged** and the **number of rounds** by *any* secure protocol realizing $\mathcal{F}_Q$ — separating the cost intrinsic to the *function* (plaintext communication complexity) from the *security overhead* imposed by privacy.

Variants:
- **Decision:** does a secure protocol with $o(f(n))$ communication / $o(r(n))$ rounds for $Q$ exist?
- **Optimization (lower-bound):** the largest provable $\Omega(\cdot)$ on bits and rounds, ideally matching a known protocol (tightness).
- **Counting:** lower bounds for COUNT/SUM/median aggregates and for set-cardinality (PSI-CA).

## 2. Mathematical Foundations
The backbone is **communication complexity** (Yao'79; Kushilevitz–Nisan). Plaintext two-party deterministic communication $D(f)$, randomized $R(f)$, and **information complexity** $\mathrm{IC}(f)$ lower-bound *any* protocol, secure or not. Canonical hard functions embedded in queries:
- **Set-disjointness** $\mathrm{DISJ}_n$: $R(\mathrm{DISJ})=\Omega(n)$ (Kalyanasundaram–Schnitger; Razborov; Bar-Yossef et al. via information complexity) — embeds in join/intersection.
- **Inner-product / GIP**: $\Omega(n)$ for parity-style aggregation.
- **Equality, Index, Gap-Hamming**: round/space trade-offs (Index → streaming/one-way bounds).

Round lower bounds come from **round-elimination** and **communication–round trade-offs** (e.g., pointer-jumping $\Omega(k)$ rounds). For **secure** protocols specifically, results separate function cost from privacy cost: Kushilevitz's characterization of **privately computable functions** and Bar-Yehuda–Chor–Kushilevitz–Orlitsky's *"Privacy, additional information, and communication"* (IEEE IT, 1993) lower-bound the communication needed to compute $f$ *privately*, sometimes strictly above $D(f)$. Information-theoretic MPC bounds (Franklin–Yung; Damgård–Nielsen) bound communication vs. corruption threshold $t/n$.

## 3. State of the Art (SOTA)
- **Function-level (apply to secure protocols):** $\Omega(n)$ randomized for disjointness/intersection (hence joins, PSI) — tight against near-linear PSI. Multiparty (number-on-forehead) disjointness lower bounds (Sherstov; Beame–Huynh) give bounds for $k$-party set operations.
- **Privacy-specific:** BCKO'93 and Kushilevitz'92 characterize which functions are privately computable and the *extra* communication privacy can force; Data–Prabhakaran–Prabhakaran (CRYPTO'14) give information-theoretic communication lower bounds for secure 2- and 3-party computation. **Amortized**/correlated-randomness models (Couteau, FOCS/IT) show preprocessing can beat online bounds.
- No general *tight* characterization for full relational algebra + aggregation exists — the bounds are query/function-specific.

## 4. Upper Bound
Matching protocols (the targets the lower bounds aim at): **PSI/semi-join** $\tilde O(n)$ communication, constant rounds — matches the $\Omega(n)$ disjointness bound up to logs/security parameter. **Secure join (materializing)** $\tilde O(n+Z)$ via oblivious sort-merge (see companion page). **Aggregation (SUM/COUNT)** via secret-sharing is $O(n)$ communication, $O(1)$ rounds in the honest-majority setting — essentially optimal. These upper bounds (in the real/ideal MPC model) are what make some lower bounds *tight* and expose where they are not.

## 5. Lower Bound
- **Communication:** $\Omega(n)$ bits for any secure intersection/equi-join (via $\mathrm{DISJ}$ reduction, information complexity). For hiding output size, an additional $\Omega(\mathrm{AGM}(Q))$ envelope is forced information-theoretically.
- **Privacy overhead:** BCKO'93 — some functions require strictly more than $D(f)$ communication to compute *privately*; secure protocols inherit this gap. Data–Prabhakaran–Prabhakaran give tight info-theoretic 2/3-party bounds for specific functionalities.
- **Rounds:** round–communication trade-offs (round elimination) imply that low-communication secure sort/merge pipelines need $\Omega(\log n)$ rounds; general constant-round MPC (BMR) exists but at higher communication.
- **Multiparty:** NOF lower bounds bound $k$-party set queries but degrade with $k$ — a known weakness.

## 6. The Gap
There is **no tight, query-class-wide theory**: known lower bounds are inherited from a handful of hard functions (disjointness, inner product) and *do not tightly capture the privacy overhead* for general joins, multi-way/cyclic queries, group-by, or aggregation under varying corruption thresholds. Open: (i) does materializing a join securely cost strictly more than the plaintext $\Theta(n+Z)$ communication, and by how much? (ii) tight **round** lower bounds for secure relational pipelines; (iii) bounds that account for preprocessing/correlated randomness (where current online bounds can be beaten); (iv) tight $k$-party bounds not degrading with $k$.

## 7. Current Research (as of June 2026)
Directions: (a) **information-complexity** techniques sharpened for secure-computation communication, separating function cost from privacy tax *(frontier — verify)*; (b) lower bounds in the **preprocessing/silent-OT/FSS** model, where the online-vs-offline split changes the picture *(frontier — verify)*; (c) lower bounds for **DP-relaxed** secure queries (revealing noised output sizes) — quantifying the communication saved by leaking $\epsilon$; (d) connecting fine-grained plaintext join lower bounds (3SUM/APSP-conditional, AGM-tightness) to their secure counterparts. Groups: IISc/TIFR (Prabhakaran, Data), Aarhus (Nielsen, Orlandi), CNRS/ENS (Couteau), Technion/Bar-Ilan, Toronto/IAS (Sherstov-style CC).

## 8. Future Work
- A general theorem bounding the *privacy overhead* (secure minus plaintext communication) for a relational-algebra query by structural parameters (treewidth, AGM exponent).
- Tight round lower bounds for secure sort/join pipelines and matching constant-round low-communication protocols.
- Lower bounds robust to preprocessing and to corruption-threshold variation.
- Fine-grained (conditional) lower bounds importing 3SUM/SETH-hardness of plaintext joins into the MPC setting.

## 9. Key References
- **[Foundational]** A. Yao. *Some Complexity Questions Related to Distributive Computing.* STOC, 1979.
- **[Foundational]** E. Kushilevitz, N. Nisan. *Communication Complexity.* Cambridge University Press, 1997.
- **[Foundational]** R. Bar-Yehuda, B. Chor, E. Kushilevitz, A. Orlitsky. *Privacy, Additional Information, and Communication.* IEEE Trans. Information Theory, 1993.
- **[Foundational]** Z. Bar-Yossef, T. S. Jayram, R. Kumar, D. Sivakumar. *An Information Statistics Approach to Data Stream and Communication Complexity.* JCSS / FOCS, 2002/2004.
- **[SOTA]** D. Data, M. M. Prabhakaran, V. M. Prabhakaran. *On the Communication Complexity of Secure Computation.* CRYPTO, 2014.
- **[Foundational]** E. Kushilevitz. *Privacy and Communication Complexity.* SIAM J. Discrete Math, 1992.
- **[Survey]** A. Sherstov. *Communication Complexity Theory: Thirty-Five Years of Set Disjointness* (survey), MFCS, 2014.

---
*Part of the [DBMS Research catalog](../../README.md).*
