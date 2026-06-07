---
id: 12-newsql-distributed-sql/readonly-transaction-latency-bounds
title: "Read-only transaction latency lower bounds"
topic: 12-newsql-distributed-sql
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Read-only transaction latency lower bounds

> **Topic:** NewSQL & Distributed SQL · **ID:** `12-newsql-distributed-sql/readonly-transaction-latency-bounds` · **Status:** open
> **Verification note:** The SNOW paper's authors are Lu, Hodsdon, Ngo, Mu, and Lloyd (OSDI 2016); the names "Kiwan, Cidon, Mahajan" in sections 2/7/9 are incorrect and the reference has been corrected.

## 1. Problem Statement

A read-only transaction (ROT) reads a set of keys spread across shards/replicas and must
return a **consistent snapshot**. The most desirable ROT has three properties
simultaneously: **strong consistency** (the snapshot is strictly serializable / externally
consistent with the surrounding read-write transactions), **single-round (one-shot)**
(one round of non-blocking messages to the involved replicas, no second confirmation
round), and **wait-free / non-blocking** (a ROT never waits on concurrent writers or on
other clients). The open problem: **for which system models are all three jointly
achievable, and what is the tight latency lower bound when they are not?**

Variants: (i) **Feasibility (decision)** — does a protocol exist providing
strict-serializability + one-round + wait-free ROTs under a given replication/consistency
model? (ii) **Latency lower bound (optimization)** — minimize ROT message rounds / response
time as a function of the consistency level. (iii) **Tradeoff frontier** — characterize the
Pareto surface between consistency strength and the achievable (rounds, blocking) pair.

## 2. Mathematical Foundations

Model an asynchronous (or partially synchronous) message-passing system with $n$ replicas,
clients issuing transactions, and a correctness criterion fixed by the **consistency
hierarchy**: eventual ⊂ causal ⊂ snapshot/process-order ⊂ serializable ⊂ strict
serializable (linearizable transactions). A ROT protocol is a distributed algorithm; its
cost is measured in **communication rounds** (message delays) and whether any step's
termination depends on another operation (blocking).

The key formal tool is the **SNOW theorem** (Lu, Hodsdon, Ngo, Mu, Lloyd; OSDI
2016): the four properties **S**trict serializability, **N**on-blocking reads, **O**ne-
response (one round / one version per read), and **W**rite transactions that conflict — at
most **three of the four** can hold simultaneously; no protocol achieves all four. This is
an impossibility result in the asynchronous message-passing model, giving a hard wall.
Adjacent foundations: linearizability (Herlihy–Wing), the CAP theorem
(Gilbert–Lynch formalization of Brewer), and FLP impossibility (consensus is unsolvable in
asynchrony with one crash), which together bound what "consistent + non-blocking" can mean.

## 3. State of the Art (SOTA)

**Theory SOTA.** SNOW (OSDI 2016) is the canonical impossibility, with a matching
construction showing each set of three properties is achievable. It establishes that
**strict-serializable + non-blocking + one-round** ROTs are impossible *whenever* concurrent
conflicting writes exist.

**Systems SOTA.** Spanner (OSDI 2012) offers consistent snapshot reads using TrueTime and
a chosen read timestamp, but general ROTs may wait for the safe time / pay a round to pick
a timestamp. RIFL/Eris and Rococo target latency but not all four SNOW properties.
**SNOW-optimal** designs (e.g., the COPS/Eiger lineage for causal consistency, and the
OSDI'16 paper's own constructions) hit three properties: for instance non-blocking +
one-round + write-conflicts at the cost of dropping strict serializability (settling for a
weaker but still useful snapshot). MongoDB/CockroachDB/YugabyteDB offer
non-blocking *follower reads* at bounded staleness, trading recency for the SNOW corner.

## 4. Upper Bound

Achievable corners (three-of-four) have **one-round, wait-free** ROTs under
weaker-than-strict consistency: e.g., causal+ consistency with non-blocking single-version
reads (Eiger). With strict serializability, the best **non-blocking** ROTs require more than
one effective round (e.g., choosing/learning a safe read timestamp, then reading) — bounding
ROT latency at roughly two message delays plus clock-uncertainty wait in TrueTime-style
systems. With bounded clock error $\epsilon$, externally consistent reads incur an expected
extra wait on the order of $\epsilon$. These are constructive upper bounds, each *omitting*
exactly one SNOW property.

## 5. Lower Bound

The **SNOW theorem** is the lower bound: in the asynchronous message-passing model, **no**
ROT protocol simultaneously provides strict serializability, non-blocking reads, one-round/
one-version responses, and supports conflicting write transactions. Hence the targeted
"wait-free, single-round, strongly consistent" ROT is **provably impossible** in the
presence of conflicting writes. Complementary impossibilities: CAP (no strong consistency +
availability under partition) and FLP (no deterministic non-blocking consensus in
asynchrony) reinforce that the strong-consistency corner cannot be both one-round and
non-blocking in general. The lower bound holds in the standard distributed model with
asynchronous communication and at least one possible conflicting writer.

## 6. The Gap

For the *exact* SNOW formulation, the problem is **closed**: the impossibility plus
matching three-property constructions are tight. What remains genuinely **open** is the
*landscape around* it: (1) precise latency lower bounds (in concrete message-delay/clock-
uncertainty units, not just "≥ 2 rounds") for the strongest ROTs that *do* exist; (2)
characterizing which **workload restrictions** (e.g., absence of concurrent conflicting
writes, bounded contention, partition-local reads) let one recover all four properties; (3)
whether weakening "strict serializability" minimally (to e.g. process-ordered
serializability) admits one-round non-blocking ROTs with provable tightness; (4) the
analogous theorem under partial synchrony / bounded clocks, where TrueTime changes the
model.

## 7. Current Research (as of June 2026)

Active threads: refining SNOW-style impossibilities for **partially synchronous** and
clock-bounded models *(frontier — verify)*; "SNOW-optimal" protocol engineering that
attains three properties with minimal latency at scale; and exploiting **contention-
adaptive** fast paths that achieve four-property behavior *when no conflicting write is
concurrent* and degrade gracefully otherwise *(frontier — verify)*. Researchers around the
original SNOW authors (Lu, Mu, Lloyd) and the broader distributed-transactions
community (e.g., NYU, MIT, Cornell groups) remain active; HLC-based follower-read freshness
bounds intersect this problem.

## 8. Future Work

- Tight, unit-ful latency lower bounds (message delays + clock uncertainty) for strongest
  achievable ROTs per consistency level.
- Workload-conditional impossibility: exact characterization of conflict patterns that
  restore the fourth SNOW property.
- A SNOW analogue for the partially synchronous / TrueTime / HLC model.
- Energy/round tradeoff and its interaction with follower-read staleness budgets.

## 9. Key References

- **[Foundational]** Lu, Hodsdon, Ngo, Mu, Lloyd. *The SNOW Theorem and Latency-Optimal Read-Only Transactions.* OSDI, 2016. — [USENIX](https://www.usenix.org/conference/osdi16/technical-sessions/presentation/lu)
- **[Foundational]** Gilbert, Lynch. *Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services (CAP).* SIGACT News, 2002. — [DOI](https://doi.org/10.1145/564585.564601)
- **[Foundational]** Fischer, Lynch, Paterson. *Impossibility of Distributed Consensus with One Faulty Process (FLP).* JACM, 1985. — [DOI](https://doi.org/10.1145/3149.214121)
- **[SOTA]** Corbett et al. *Spanner: Google's Globally-Distributed Database.* OSDI, 2012. — [USENIX](https://www.usenix.org/conference/osdi12/technical-sessions/presentation/corbett)
- **[SOTA]** Lloyd, Freedman, Kaminsky, Andersen. *Stronger Semantics for Low-Latency Geo-Replicated Storage (Eiger).* NSDI, 2013. — [USENIX](https://www.usenix.org/conference/nsdi13/technical-sessions/presentation/lloyd)
- **[Foundational]** Herlihy, Wing. *Linearizability: A Correctness Condition for Concurrent Objects.* ACM TOPLAS, 1990. — [DOI](https://doi.org/10.1145/78969.78972)

## 10. Worked Example

Two shards hold $x$ (shard 1) and $y$ (shard 2), initially $x=y=0$. A read-write transaction $W$ does $x{:=}1,\,y{:=}1$ atomically (strictly serializable). A read-only transaction $R$ reads $\{x,y\}$ and wants all four SNOW properties.

$R$ fires one parallel round: a single message to each shard, no second confirmation (**O**ne-response), and each shard replies immediately without blocking on $W$ (**N**on-blocking). Suppose $W$'s write to $x$ lands before $R$'s read on shard 1 but $W$'s write to $y$ lands *after* $R$'s read on shard 2. Then $R$ observes $x=1,\,y=0$.

No serial order explains this: $R$ before $W$ requires $x=0$; $R$ after $W$ requires $y=1$. So $R$ is **not strictly serializable** (the fractured read). To repair it, a shard must either delay its reply until it knows $W$'s fate (drops **N**) or $R$ must run a second round to agree on a snapshot (drops **O**). This is exactly the SNOW wall: with a conflicting writer $W$ present, **S+N+O is unachievable** — at most three of the four hold.

---
*Part of the [DBMS Research catalog](../../README.md).*
