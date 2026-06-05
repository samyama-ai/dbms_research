# Randomized Consensus Round Complexity

> **Topic:** Consensus & Coordination · **ID:** `10-consensus-coordination/randomized-round-complexity` · **Status:** open

## 1. Problem Statement
Randomization circumvents FLP: in asynchronous systems, coin-flipping protocols solve Byzantine agreement with probability 1, terminating in a finite *expected* number of rounds. The central complexity question: **what is the minimum expected number of rounds (and communication) to solve asynchronous Byzantine agreement with optimal resilience against an *adaptive* adversary, and where exactly do the best known upper and lower bounds meet?**

Variants:
- **Decision/round complexity:** Determine the tight expected round complexity $R(n,f)$ for asynchronous Byzantine agreement (ABA) with $n\ge 3f+1$ against an adaptive (and against a strongly-adaptive, message-removing) adversary.
- **Communication complexity:** Minimize expected bits/messages; the round and message frontiers are coupled (e.g. via the cost of common-coin establishment).
- **Adversary model dependence:** Quantify how much the answer changes between *static*, *adaptive*, and *strongly adaptive* adversaries, and with/without trusted setup (PKI, threshold coins).

The adaptive-adversary case is the open heart: a strongly adaptive adversary that observes messages and can corrupt-and-delete in flight defeats many constant-expected-round constructions that rely on a pre-shared common coin.

## 2. Mathematical Foundations
Model: $n$ processes, asynchronous message passing, up to $f$ Byzantine, optimal resilience $n\ge 3f+1$ (Byzantine agreement requires $n>3f$, Pease–Shostak–Lamport; asynchronous BA inherits this). A **randomized** protocol must satisfy agreement and validity always, and termination with probability 1; we measure $\mathbb{E}[\text{rounds}]$ over the protocol's coins, worst-case over adversary and schedule.

The canonical engine is the **common coin** (Rabin): a shared random bit revealed to all correct processes, against which Ben-Or-style protocols converge in $O(1)$ expected rounds *if* a strong common coin exists. Building such a coin against an adaptive adversary without trusted setup is the difficulty; with a PKI + threshold signatures (Cachin–Kursawe–Shoup), a strong common coin gives $O(1)$ expected rounds and $O(n^2)$ expected messages. Lower bounds use **information-theoretic / round-elimination** arguments: against a strongly adaptive adversary, Bar-Joseph–Ben-Or proved an $\Omega\!\big(\sqrt{n/\log n}\big)$ expected-round lower bound for *full-information* randomized consensus (no cryptography), separating it sharply from the cryptographic $O(1)$.

## 3. State of the Art (SOTA)
- **Ben-Or** (PODC 1983) and **Rabin** (FOCS 1983): foundational randomized ABA; exponential vs $O(1)$ expected rounds with a common coin.
- **Cachin–Kursawe–Shoup** (PODC 2000): practical ABA with threshold-crypto common coin, $O(1)$ expected rounds, $O(n^2)$ messages — theory-and-systems SOTA for the cryptographic setting.
- **Most–Mostly / Mostefaoui–Hamouma–Raynal** (PODC 2014) and **Cobalt/Crain** ABA: signature-free binary ABA, $O(n^2)$ messages, $O(1)$ expected rounds under a fair scheduler.
- **DAG-BFT** (Narwhal–Tusk, DSN/EuroSys 2022; Bullshark; Mysticeti) embeds randomized ABA for asynchronous liveness at scale. **Adaptively secure** constructions: Abraham–Malkhi–Spiegelman and successors target adaptive adversaries with sub-quadratic or near-optimal expected rounds. *(frontier — verify 2024–2026 adaptive-adversary improvements.)*

## 4. Upper Bound
Best known: **$O(1)$ expected rounds** with a threshold-cryptographic common coin and trusted setup, at $O(n^2)$ expected communication (Cachin–Kursawe–Shoup; Mostéfaoui–Raynal for signature-free binary). Against a *non-adaptive* adversary, constant expected rounds and (with newer coins) near-$O(n)$ amortized communication are achievable. For the *strongly adaptive, full-information* (no crypto) setting, the best protocols match the $\tilde{O}(\sqrt{n})$-round regime — exponentially worse than the cryptographic case. Holds in the asynchronous Byzantine model with $n\ge 3f+1$.

## 5. Lower Bound
- **Resilience:** $n\ge 3f+1$ is necessary (Pease–Shostak–Lamport / Bracha–Toueg).
- **Rounds, full-information:** $\Omega(\sqrt{n/\log n})$ expected rounds against a strongly adaptive adversary for randomized consensus without cryptography (Bar-Joseph & Ben-Or, 1998) — and any protocol terminating in $\le t$ rounds errs with non-negligible probability below a threshold.
- **Communication:** $\Omega(f^2)$ messages for deterministic BA (Dolev–Reischuk) and $\Omega(n^2)$-type barriers persist for adaptive randomized BA without threshold setup. FLP rules out *deterministic* termination, motivating randomization in the first place.

## 6. The Gap
For the *cryptographic, static/PKI* setting the round complexity is essentially settled ($\Theta(1)$ expected). The genuinely open gap is the **adaptive (and strongly adaptive) adversary without trusted setup**: between the $\Omega(\sqrt{n/\log n})$ full-information lower bound and the $O(1)$ cryptographic upper bound lies a chasm, and it is unresolved (a) how cheaply an adaptively-secure common coin can be built, (b) whether $O(1)$ expected rounds are attainable against a *strongly* adaptive adversary at all without strong setup, and (c) the tight communication–round trade-off. Closing it needs either an adaptively-secure constant-round coin with sub-quadratic communication or a stronger round lower bound for the cryptographic adaptive model.

## 7. Current Research (as of June 2026)
- Adaptively-secure VRF/threshold common coins and "no-setup" coins via verifiable secret sharing with sub-quadratic communication. *(frontier — verify.)*
- Asynchronous DAG-BFT closing the gap between asymptotic round complexity and real throughput; balanced/player-replaceable protocols resisting adaptive corruption (à la Algorand sortition). *(frontier — verify.)*
- Groups: Technion/VMware (Abraham, Spiegelman, Malkhi), IBM/DFINITY (Cachin), IRISA (Raynal, Mostéfaoui), Aptos/Sui research, MIT/Stanford crypto-consensus groups.

## 8. Future Work
- Tight expected-round bounds for strongly adaptive ABA without trusted setup.
- Optimal round–communication trade-off curves.
- Practical adaptively-secure common coins with $\tilde{O}(n)$ communication.

## 9. Key References
- **[Foundational]** Michael Ben-Or. *Another Advantage of Free Choice: Completely Asynchronous Agreement Protocols.* PODC, 1983.
- **[Foundational]** Marshall Pease, Robert Shostak, Leslie Lamport. *Reaching Agreement in the Presence of Faults.* JACM, 1980.
- **[Foundational]** Ziv Bar-Joseph, Michael Ben-Or. *A Tight Lower Bound for Randomized Synchronous Consensus.* PODC, 1998.
- **[SOTA]** Christian Cachin, Klaus Kursawe, Victor Shoup. *Random Oracles in Constantinople: Practical Asynchronous Byzantine Agreement Using Cryptography.* PODC, 2000.
- **[SOTA]** Achour Mostéfaoui, Hamouma Moumen, Michel Raynal. *Signature-Free Asynchronous Byzantine Consensus with t < n/3 and O(n²) Messages.* PODC, 2014.
- **[SOTA]** Ittai Abraham, Dahlia Malkhi, Alexander Spiegelman et al. *Asymptotically Optimal Validated Asynchronous Byzantine Agreement.* PODC, 2019.

---
*Part of the [DBMS Research catalog](../../README.md).*
