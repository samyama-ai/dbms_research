---
id: 11-nosql-kv/minimal-movement-rebalancing
title: "Provably Minimal-Movement Rebalancing"
topic: 11-nosql-kv
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Provably Minimal-Movement Rebalancing

> **Topic:** NoSQL & Key-Value Stores · **ID:** `11-nosql-kv/minimal-movement-rebalancing` · **Status:** partially-solved
> **Verification note:** Consistent Hashing with Bounded Loads (Mirrokni–Thorup–Zadimoghaddam) appeared on arXiv in 2016 and at SODA 2018, not NeurIPS 2016 as the section-2 parenthetical states.

## 1. Problem Statement

A sharded key-value store distributes $N$ keys over $n$ nodes arranged on a logical ring (or via a partition map). When a node is added or removed, some keys must migrate so that the new assignment remains **balanced** (each node owns ≈ $1/n$ of the keyspace) and **consistent** (every client computes the same key→node map). The problem: design an assignment scheme minimizing the **expected number of keys (or bytes) moved** per membership change, subject to a balance constraint, while keeping lookup $O(1)$ or $O(\log n)$ and metadata small.

Variants:
- **Decision:** does a scheme exist that moves $\le m$ keys per single node join/leave while keeping max load $\le (1+\epsilon)/n$?
- **Optimization:** minimize movement subject to a balance/load bound.
- **Counting/amortized:** expected movement over a sequence of $k$ membership changes.

The realistic regime adds **weighted/heterogeneous nodes**, **fault domains/rack-awareness**, and **bounded metadata** (no per-key directory).

## 2. Mathematical Foundations

Let the keyspace be $[0,1)$ via a hash. **Consistent hashing** (Karger et al., STOC 1997) maps both keys and nodes to the ring; a key is owned by the next node clockwise. Adding the $n$-th node disturbs in expectation a $1/n$ fraction of keys — **optimal**, since any balanced scheme must reassign at least the keys the new node will own, i.e. $\Theta(N/n)$. This is the information-theoretic floor:

$$ \mathbb{E}[\text{keys moved per join}] \ge \frac{N}{n+1}. $$

Plain consistent hashing has load imbalance $\Theta(\log n / n)$; **virtual nodes** ($v$ tokens per node) reduce variance to $O(1/\sqrt{v})$ relative. **Rendezvous (HRW) hashing** (Thaler & Ravishankar 1998) achieves the same optimal movement with $O(n)$ lookup but tiny metadata. **Jump consistent hash** (Lamping & Veach 2014) gives optimal expected movement and balanced buckets with $O(\ln n)$ lookup and *zero* stored state, but only supports removal of the *last* bucket. **Consistent hashing with bounded loads** (Mirrokni, Thorup, Zadimoghaddam, NeurIPS 2016 / SODA) guarantees max load $\le \lceil (1+\epsilon)\,\text{avg}\rceil$ while moving $O(1/\epsilon^2)$ keys per change in expectation. **Maglev hashing** (Eisenbud et al., NSDI 2016) builds a lookup table trading minimal disruption for near-perfect balance.

## 3. State of the Art (SOTA)

**Theory-SOTA:** consistent hashing with bounded loads gives tight movement bounds *with* an enforced balance guarantee; AnchorHash (Mendelson et al., 2020) and DxHash provide $O(1)$-ish memory, optimal disruption, and fast lookup for the full add/remove case. **Systems-SOTA:** Dynamo/Cassandra (virtual nodes), Amazon ElastiCache, and Maglev/Google load balancers; jump hash in production sharders. These collectively *solve* the unweighted, single-change case optimally — hence **partially-solved**.

## 4. Upper Bound

Minimal-movement is achieved: schemes move $O(N/n)$ keys per single join/leave, matching the lower bound up to constants. Jump consistent hash attains *exactly* optimal expected movement with $O(\ln n)$ time and $O(1)$ space. Consistent hashing with bounded loads attains optimal movement *and* $(1+\epsilon)$ load with $O(1/\epsilon^2)$ amortized extra moves. AnchorHash: $O(1)$ amortized lookup, minimal disruption, $O(n)$ memory.

## 5. Lower Bound

The $\Omega(N/n)$ per-change movement bound is information-theoretic and tight: the newly arrived node must receive its share. For *simultaneous balance + minimal movement under weights*, no scheme matches the unweighted optimum — weighted consistent hashing incurs provable overhead, and maintaining $(1+\epsilon)$ balance forces $\Omega(1/\epsilon)$-type movement (Mirrokni et al.). For arbitrary multi-change adversarial sequences with fault-domain constraints, tight lower bounds are open.

## 6. The Gap

For the canonical unweighted single-event case the gap is **closed** (matching $\Theta(N/n)$). Genuinely open: (1) **weighted/heterogeneous** rebalancing with simultaneously optimal movement *and* balance; (2) **constrained** placement (replication factor + rack/fault-domain + minimal movement) where the trade-off lower bounds are not tight; (3) amortized optimality over adversarial churn sequences.

## 7. Current Research (as of June 2026)

Active work on weighted consistent hashing with tight bounds and on *constrained* rebalancing for erasure-coded / geo-replicated stores. AnchorHash/DxHash-style $O(1)$-memory hashers are being extended to weighted and fault-domain-aware settings *(frontier — verify)*. Interest in rebalancing for disaggregated and serverless storage where "nodes" churn rapidly, and in coupling rebalancing with data-movement *cost* models (network/egress \$) rather than key counts. Groups: Mirrokni/Thorup (Google Research), and systems teams at AWS/Meta for production sharders.

## 8. Future Work

- A scheme that is provably movement-optimal *and* balance-optimal under arbitrary node weights.
- Tight lower bounds for rebalancing under replication + fault-domain constraints.
- Cost-aware rebalancing minimizing $ (network bytes, cross-AZ egress) rather than key count.
- Online competitive analysis over adversarial membership-change sequences.

## 9. Key References

- **[Foundational]** David Karger, Eric Lehman, Tom Leighton, Matthew Levine, Daniel Lewin, Rina Panigrahy. *Consistent Hashing and Random Trees.* STOC 1997. — [DOI](https://doi.org/10.1145/258533.258660)
- **[Foundational]** John Lamping, Eric Veach. *A Fast, Minimal Memory, Consistent Hash Algorithm.* arXiv:1406.2294, 2014. — [arXiv](https://arxiv.org/abs/1406.2294)
- **[SOTA]** Vahab Mirrokni, Mikkel Thorup, Morteza Zadimoghaddam. *Consistent Hashing with Bounded Loads.* SODA 2018 (arXiv:1608.01350). — [arXiv](https://arxiv.org/abs/1608.01350)
- **[SOTA]** Daniel E. Eisenbud et al. *Maglev: A Fast and Reliable Software Network Load Balancer.* NSDI 2016. — [USENIX](https://www.usenix.org/conference/nsdi16/technical-sessions/presentation/eisenbud)
- **[SOTA]** Gal Mendelson, Shay Vargaftik, Katherine Barabash, et al. *AnchorHash: A Scalable Consistent Hash.* IEEE/ACM Transactions on Networking, 2021. — [DOI](https://doi.org/10.1109/TNET.2020.3039547)
- **[Foundational]** David Thaler, Chinya Ravishankar. *Using Name-Based Mappings to Increase Hit Rates (HRW / Rendezvous Hashing).* IEEE/ACM ToN, 1998. — [DOI](https://doi.org/10.1109/90.663936)

## 10. Worked Example

Suppose $N = 12{,}000$ keys are hashed uniformly onto the ring over $n = 3$ nodes $A,B,C$, each owning $\approx 4{,}000$ keys.

**Add a 4th node $D$.** The information-theoretic floor says $D$ must receive $\mathbb{E}[\text{moved}] \ge N/(n+1) = 12000/4 = 3000$ keys. Plain consistent hashing achieves exactly this in expectation: $D$ claims one arc of the ring and steals only the keys falling in that arc — *no other reassignments occur*. Contrast a naive $\text{node}=h(k)\bmod n$ scheme: changing $n=3\to4$ remaps keys whenever $h(k)\bmod 3 \neq h(k)\bmod 4$, moving roughly $\tfrac{3}{4}N = 9000$ keys — a $3\times$ waste.

**Balance check.** With plain hashing, loads vary by $\Theta(\log n / n)$, so a node might hold $5{,}500$ vs the $3{,}000$ ideal. Adding $v=100$ virtual tokens per node shrinks the relative spread to $O(1/\sqrt{v}) = 10\%$, giving $\approx 3{,}000 \pm 300$ per node while preserving the optimal $\sim 3000$-key movement.

---
*Part of the [DBMS Research catalog](../../README.md).*
