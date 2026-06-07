---
id: 24-privacy-encrypted-db/mpc-secure-joins
title: "Secure Multiparty Join Processing"
topic: 24-privacy-encrypted-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Secure Multiparty Join Processing

> **Topic:** Privacy & Encrypted Databases · **ID:** `24-privacy-encrypted-db/mpc-secure-joins` · **Status:** open

## 1. Problem Statement
Several **distrustful parties** each hold a private relation; they wish to compute a **join** (and downstream group-by/aggregation) over the union without revealing their inputs beyond the agreed output, using **secure multiparty computation (MPC)**. The problem: design MPC join protocols whose **communication and round complexity scale to real OLAP-size relations** (millions–billions of rows) across 2 or more parties, while leaking only the output (and bounded, agreed metadata such as output size — or hiding even that).

Variants:
- **Decision/feasibility:** is there an MPC equi-join protocol with $\tilde O(n)$ communication and constant/poly-log rounds for inputs of size $n$ and output $Z$?
- **Optimization:** minimize total communication bits, rounds, and online latency; reveal vs. hide output size $Z$.
- **Counting/aggregation:** compute COUNT/SUM over the join without materializing it (private-join-and-compute).

## 2. Mathematical Foundations
MPC realizes an ideal functionality $\mathcal{F}_{\bowtie}$ with security against semi-honest or malicious adversaries (Yao garbled circuits; GMW; BGW/Shamir-secret-sharing; SPDZ/MASCOT for malicious with preprocessing). Cost is dominated by **communication** and **rounds**, not local compute.

A join evaluated as a circuit costs $\Theta(|R|\cdot|S|)$ comparisons naively — the central scaling barrier. Sort-based secure joins use **oblivious sort networks** ($O(n\log^2 n)$ comparisons, Batcher) over secret-shared keys, giving $O(n\log^2 n)$ secure comparisons. **Output size** is governed by the **AGM bound** $Z\le\prod_e|R_e|^{x_e}$; hiding $Z$ forces padding to $\mathrm{AGM}(Q)$. **Private Set Intersection (PSI)** is the special case of an intersection/semi-join and has near-linear protocols (KKRT, OT-extension; OPRF-based). **Circuit-PSI** / **PSI-with-computation** extends to aggregation. Round complexity connects to communication-complexity lower bounds and to the depth of the secure sort/merge.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** **SMCQL** (Bater et al., VLDB'17) and **Conclave** (Volgushev et al., EuroSys'19) compile SQL (incl. joins) to MPC, using plaintext "selective" steps to cut cost; **Senate** (Poddar et al., USENIX'20) for malicious-secure multi-party SQL with circuit decomposition; **SAQE**, **Secrecy** (Liagouris et al., NSDI'23) — relational MPC with oblivious operators and vectorization; **Scape**/**SECRECY** group-by-join pipelines. **DJoin / Private-Join-and-Compute** (Google, CCS'19) for join-then-aggregate.
- **Theory-SOTA:** near-linear **PSI** and **circuit-PSI** (Pinkas–Schneider–Zohner lineage, KKRT'16, PSTY'19); oblivious-sort-based secure joins at $O(n\log^2 n)$ comparisons; Mohassel–Rindal-style 3-party secret-sharing joins.

## 4. Upper Bound
- **Semi-honest equi-join (sort-based):** $O((n+Z)\log^2(n+Z))$ secure comparisons / communication via oblivious bitonic sort-merge in the secret-sharing or garbled-circuit model; $O(n\log n)$ with AKS-style sort (impractical constants).
- **Two-party intersection / semi-join (PSI):** $\tilde O(n)$ communication, constant rounds (OT-extension/OPRF), the near-optimal point.
- **Join-and-aggregate (output COUNT/SUM only):** $\tilde O(n)$ with private-join-and-compute when only the aggregate, not the join tuples, is revealed.
Model: real/ideal MPC security (semi-honest; malicious adds $\sim$constant or preprocessing overhead via SPDZ/MASCOT).

## 5. Lower Bound
- **Output-size barrier:** materializing the join securely requires $\Omega(Z)$ communication; hiding $Z$ forces $\Omega(\mathrm{AGM}(Q))$ padding — information-theoretic, so secure joins cannot be output-sensitive while hiding selectivity.
- **Communication complexity:** secure evaluation inherits two-party **communication lower bounds**; e.g., set-disjointness has $\Omega(n)$ randomized communication, lower-bounding any secure join/intersection at $\Omega(n)$ bits. (See the companion "Communication Lower Bounds for MPC Queries" page.)
- **Rounds:** general MPC can be constant-round (BMR), but *low-communication* secure sort/merge pipelines have round complexity tied to network depth $\Omega(\log n)$ unless communication blows up.

## 6. The Gap
PSI/semi-joins are near-closed ($\tilde O(n)$). The **open** problem is full **materializing multi-party equi/theta-joins** at $\tilde O(n+Z)$ communication with practical constants and few rounds, especially: (i) **multi-way / cyclic** joins matching the AGM/WCOJ bound securely; (ii) malicious security without large preprocessing blowup at OLAP scale; (iii) hiding output size without quadratic padding; (iv) bandwidth, not just asymptotics — current systems are $10^2$–$10^4\times$ slower than plaintext on large inputs.

## 7. Current Research (as of June 2026)
Active: (a) vectorized, GPU/SIMD-friendly secret-sharing relational engines (Secrecy lineage) pushing billions of secure ops *(frontier — verify)*; (b) **secure worst-case-optimal / Yannakakis-style** acyclic join pipelines to avoid intermediate blowup *(frontier — verify)*; (c) function-secret-sharing (FSS) and silent-OT preprocessing to slash online communication; (d) differential-privacy-relaxed MPC joins that reveal noised output sizes for output-sensitivity; (e) hybrid TEE+MPC. Groups: Boston U/Northwestern (Bater/Bestavros/Liagouris), MIT/Berkeley (Popa lineage, Senate), Google (Private-Join-and-Compute), Aarhus (SPDZ/MASCOT), Bar-Ilan/Technion (PSI).

## 8. Future Work
- Secure acyclic-join (Yannakakis) and WCOJ pipelines with $\tilde O(n+Z)$ communication and bounded padding.
- Output-size hiding without AGM-bound blowup (DP relaxation or amortization).
- Malicious-secure OLAP joins with practical preprocessing at scale.
- Cost-model-driven secure query optimizers choosing MPC plans by communication/round budget.

## 9. Key References
- **[Foundational]** A. Yao. *Protocols for Secure Computations.* FOCS, 1982; M. Ben-Or, S. Goldwasser, A. Wigderson. *Completeness Theorems for Non-Cryptographic Fault-Tolerant Distributed Computation.* STOC, 1988. — [Yao DOI](https://doi.org/10.1109/SFCS.1982.38) — [BGW DOI](https://doi.org/10.1145/62212.62213)
- **[SOTA]** J. Bater, G. Elliott, C. Eggen, et al. *SMCQL: Secure Querying for Federated Databases.* PVLDB, 2017. — [DOI](https://doi.org/10.14778/3055330.3055334) — [arXiv](https://arxiv.org/abs/1606.06808)
- **[SOTA]** N. Volgushev, M. Schwarzkopf, et al. *Conclave: Secure Multi-Party Computation on Big Data.* EuroSys, 2019. — [DOI](https://doi.org/10.1145/3302424.3303982) — [arXiv](https://arxiv.org/abs/1902.06288)
- **[SOTA]** R. Poddar, S. Kalra, A. Yanai, et al. *Senate: A Maliciously-Secure MPC Platform for Collaborative Analytics.* USENIX Security, 2021. — [USENIX](https://www.usenix.org/conference/usenixsecurity21/presentation/poddar) — [arXiv](https://arxiv.org/abs/2010.13752)
- **[SOTA]** J. Liagouris, V. Kalavri, M. Faisal, M. Varia. *Secrecy: Secure Collaborative Analytics in Untrusted Clouds.* NSDI, 2023. — [USENIX](https://www.usenix.org/conference/nsdi23/presentation/liagouris)
- **[SOTA]** B. Pinkas, T. Schneider, O. Tkachenko, A. Yanai. *Efficient Circuit-based PSI ... (PSTY).* EUROCRYPT, 2019. — [DOI](https://doi.org/10.1007/978-3-030-17659-4_5)
- **[Foundational]** I. Damgård, V. Pastro, N. Smart, S. Zakarias. *Multiparty Computation from Somewhat Homomorphic Encryption (SPDZ).* CRYPTO, 2012. — [DOI](https://doi.org/10.1007/978-3-642-32009-5_38) — [ePrint](https://eprint.iacr.org/2011/535)

## 10. Worked Example

Two hospitals run an MPC equi-join $R(\text{pid},\text{age}) \bowtie_{\text{pid}} S(\text{pid},\text{dx})$ to count diabetic patients over 50, revealing only the COUNT.

Party A holds $R=\{(1,52),(2,47),(3,61)\}$; Party B holds $S=\{(2,\text{flu}),(3,\text{dm}),(5,\text{dm})\}$, $n=3$ each.

**Naive nested-loop circuit:** compare every $(r,s)$ pair: $|R|\cdot|S| = 3\times 3 = 9$ secure equality checks — the $\Theta(n^2)$ barrier.

**Sort-based oblivious join:** secret-share all 6 tuples tagged by relation, run one oblivious bitonic sort on key `pid` ($O(n\log^2 n)$ comparisons). The sorted shared sequence interleaves matching keys adjacently:
$$1_R,\; 2_R\,2_S,\; 3_R\,3_S,\; 5_S.$$
A single linear oblivious scan emits a shared match flag at each adjacent $R$–$S$ pair with equal key: matches at pid 2 and pid 3, so the join has $Z=2$ tuples. A second oblivious scan evaluates the predicate ($\text{age}>50 \wedge \text{dx}=\text{dm}$): only pid 3 (age 61, dm) qualifies, giving COUNT $=1$, which is then opened.

Cost: $6\log^2 6 \approx 6\cdot 6.7 \approx 40$ secure comparisons vs. 9 naive here — but for $n=10^6$ the sort's $n\log^2 n \approx 4\times10^8$ crushes $n^2=10^{12}$. Hiding $Z$ would require padding output to the $\mathrm{AGM}$ bound.

---
*Part of the [DBMS Research catalog](../../README.md).*
