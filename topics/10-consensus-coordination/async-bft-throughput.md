---
id: 10-consensus-coordination/async-bft-throughput
title: "Asynchronous BFT Throughput Limits"
topic: 10-consensus-coordination
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Asynchronous BFT Throughput Limits

> **Topic:** Consensus & Coordination · **ID:** `10-consensus-coordination/async-bft-throughput` · **Status:** empirically-open

## 1. Problem Statement

Classical leader-based BFT (PBFT, HotStuff) routes all traffic through a single leader, capping throughput at the leader's egress bandwidth and stalling under leader faults or asynchrony. **Asynchronous, DAG-based BFT** (Narwhal/Bullshark/Tusk, DAG-Rider, Mysticeti) decouples *data dissemination* from *consensus ordering*: every validator continuously broadcasts batches into a causally-referenced DAG, and consensus merely *orders already-disseminated* vertices. The central question:

> How close can asynchronous DAG-BFT get to the **network-bandwidth-bound** throughput limit — i.e., the rate at which $n$ validators can collectively absorb client transactions given per-node bandwidth $B$ — as $n$ scales, under both honest and Byzantine schedules?

Variants:
- **Empirical/optimization:** maximize sustained tx/s for fixed $n$, $B$, latency target $L$, fault threshold $f$.
- **Theory:** characterize the asymptotic *throughput–latency–resilience* trade-off; is constant-factor-of-bandwidth optimal achievable with $O(1)$ expected latency?

## 2. Mathematical Foundations

Model $n = 3f+1$ validators in the **asynchronous** message-passing model with up to $f$ Byzantine faults; the adversary controls scheduling (no timing assumptions). A **DAG** is built in rounds: each round-$r$ vertex from validator $i$ carries a block of transactions and references $\ge 2f+1$ round-$(r{-}1)$ vertices, certified by quorums (reliable broadcast / consistent broadcast). The **ordering** is a deterministic function of the local DAG, so once a vertex is committed all honest parties output the same total order (agreement) without extra messages.

Key metric: **amortized communication per committed transaction**. If each transaction is sent once (dissemination) plus $O(1)$ metadata for ordering, the scheme is *bandwidth-optimal* up to constants. Throughput limit: with payload bandwidth $B$ per node and replication factor $\rho$ (each tx stored at $\ge f+1$ nodes for availability), aggregate throughput is at most
$$ T_{\max} \approx \frac{n \cdot B}{\rho \cdot s}, \qquad \rho \ge f+1, $$
for transaction size $s$. Asynchronous *agreement* itself is impossible deterministically (**FLP**); DAG-BFT escapes this with randomized common coins (DAG-Rider) or by ordering a partially-synchronous "fast path" (Bullshark).

## 3. State of the Art (SOTA)

**Systems-SOTA.** *Narwhal & Tusk* (EuroSys 2022) separated mempool from consensus and demonstrated >100k–600k tx/s. *Bullshark* (CCS 2022) added a partially-synchronous fast path with low latency and zero extra messages. *Mysticeti* (2024) cut latency to ~0.5s while keeping high throughput by allowing uncertified DAG blocks and implicit commits *(frontier — verify)*. Production: Sui (Mysticeti), Aptos (Quorum Store ≈ Narwhal), Aleph Zero (AlephBFT). *Shoal*/*Shoal++* pipeline anchors to reduce latency.

**Theory-SOTA.** *DAG-Rider* (PODC 2021) gave the first asymptotically-optimal asynchronous BFT atomic broadcast: $O(1)$ expected rounds, $O(n)$ messages per round amortized, post-quantum safe.

## 4. Upper Bound

DAG-BFT achieves **amortized $O(1)$ messages per transaction** beyond a single dissemination, i.e., it is constant-factor bandwidth-optimal: each transaction crosses the network roughly once for dissemination plus $O(n)$ small certificates amortized over a whole block. Latency: $O(1)$ expected reliable-broadcast rounds (DAG-Rider) to commit, or 2–3 message delays on the fast path (Bullshark/Mysticeti). Empirically, sustained throughput scales near-linearly with $n$ until aggregate bandwidth saturates, the regime DAG designs were built to reach.

## 5. Lower Bound

**FLP** (Fischer–Lynch–Paterson, 1985): no deterministic asynchronous protocol solves agreement with even one crash fault — hence randomization or partial synchrony is mandatory; this is why "asynchronous throughput" must invoke coins. **Dolev–Reischuk** (1985): any Byzantine agreement needs $\Omega(f^2)$ messages (a quadratic floor that DAG schemes pay in certificate formation, $O(n^2)$ per round but amortized over large blocks). Information-theoretically, durable availability under $f$ Byzantine faults requires each transaction replicated $\ge f+1$ times, so the bandwidth limit $T_{\max}$ above is a hard ceiling; no protocol can commit faster than nodes can *receive* the data they must store.

## 6. The Gap

There is no asymptotic complexity gap — DAG-BFT is provably near-optimal in messages and expected rounds. The gap is **empirical and constant-factor**: real deployments hit 30–70% of $T_{\max}$ due to certificate overhead, signature verification CPU, head-of-line blocking on slow validators, and tail-latency in reliable broadcast. Whether one can simultaneously achieve (i) >90% of bandwidth, (ii) sub-second latency, and (iii) full asynchronous safety at $n \ge 100$ remains an open *systems* question. Closing it needs either cheaper certification (threshold/aggregate signatures, erasure-coded dissemination) or a proof that some constant loss is fundamental.

## 7. Current Research (as of June 2026)

(1) **Uncertified DAGs** (Mysticeti, Cordial Miners) removing per-vertex certificates to cut latency and bandwidth *(frontier — verify)*; (2) **erasure-coded / data-availability sampling** dissemination so each node stores $O(1/n)$ of each block; (3) **leaderless pipelining** (Shoal++) to keep all anchors useful; (4) hardware-accelerated BLS aggregation. Groups/people: Spiegelman, Sonnino, Gelashvili, Kokoris-Kogias (Mysten Labs / IST Austria), Alberto Sonnino, the Aptos and Sui research teams, and academic DAG-BFT work from Technion and EPFL.

## 8. Future Work

- A tight constant-factor characterization of achievable bandwidth utilization vs. latency vs. $f$.
- Asynchronous DAG-BFT with sublinear per-node storage via coding.
- Robustness of empirical throughput under *adaptive* adversarial scheduling, not just crash/honest benchmarks.
- Formal accounting of CPU (signature) cost in the throughput model, not just network.

## 9. Key References

- **[Foundational]** M. Fischer, N. Lynch, M. Paterson. *Impossibility of Distributed Consensus with One Faulty Process.* JACM, 1985. — [DOI](https://doi.org/10.1145/3149.214121)
- **[Foundational]** D. Dolev, R. Reischuk. *Bounds on Information Exchange for Byzantine Agreement.* JACM, 1985. — [DOI](https://doi.org/10.1145/2455.214112)
- **[SOTA]** I. Keidar, E. Kokoris-Kogias, O. Naor, A. Spiegelman. *All You Need is DAG (DAG-Rider).* PODC, 2021. — [arXiv](https://arxiv.org/abs/2102.08325)
- **[SOTA]** G. Danezis, L. Kokoris-Kogias, A. Sonnino, A. Spiegelman. *Narwhal and Tusk: A DAG-based Mempool and Efficient BFT Consensus.* EuroSys, 2022. — [arXiv](https://arxiv.org/abs/2105.11827)
- **[SOTA]** A. Spiegelman, N. Giridharan, A. Sonnino, L. Kokoris-Kogias. *Bullshark: DAG BFT Protocols Made Practical.* ACM CCS, 2022. — [arXiv](https://arxiv.org/abs/2201.05677)
- **[SOTA]** K. Babel, A. Chursin, G. Danezis, A. Sonnino, et al. *Mysticeti: Reaching the Limits of Latency with Uncertified DAGs.* 2024 (preprint). — [arXiv](https://arxiv.org/abs/2310.14821)

## 10. Worked Example

Take $n = 3f+1 = 4$ validators, so $f=1$ and a quorum is $2f+1 = 3$. Plug numbers into the bandwidth ceiling $T_{\max} \approx \frac{n\,B}{\rho\,s}$.

Let per-node payload bandwidth $B = 1\text{ Gb/s} = 10^9$ b/s, transaction size $s = 512$ bytes $= 4096$ bits, and durability replication $\rho = f+1 = 2$ (each tx stored at $\ge 2$ nodes). Then

$$ T_{\max} \approx \frac{4 \cdot 10^9}{2 \cdot 4096} \approx 488{,}000 \text{ tx/s}. $$

In the DAG, each round-$r$ vertex references $\ge 2f+1 = 3$ round-$(r{-}1)$ vertices; once a vertex is committed, every honest node derives the *same* total order from its local DAG with **zero** extra ordering messages, so the only network cost is the one-time dissemination plus $O(n)$ small certificates amortized over a full block. The gap: real systems hit perhaps $0.4\,T_{\max} \approx 195{,}000$ tx/s because BLS verification CPU and reliable-broadcast tail latency, not bandwidth, become the binding constraint — the empirical, constant-factor gap this problem isolates.

---
*Part of the [DBMS Research catalog](../../README.md).*
