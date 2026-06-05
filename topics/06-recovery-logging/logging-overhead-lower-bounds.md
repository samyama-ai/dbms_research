# Lower bounds on logging overhead

> **Topic:** Recovery, Logging & Durability · **ID:** `06-recovery-logging/logging-overhead-lower-bounds` · **Status:** open

## 1. Problem Statement

Every crash-recoverable durability protocol pays a cost to make committed work survive failures: it must force some information to a stable, persistence-ordered medium before acknowledging a commit. The question is *how much* it must pay. We want tight lower bounds on:

- **Persistent-write volume** — the number of bytes (or distinct cache lines / pages / log records) that must reach stable storage per committed transaction.
- **Ordering operations** — the number of fence / barrier / `flush` operations on the persistence critical path.
- **I/O round trips** — the number of synchronous stable-storage waits a commit must serialize on.

Variants: (a) *decision* — given a workload and durability semantics, can durability be achieved within budget $B$? (b) *optimization* — minimize amortized persistent-write overhead per commit; (c) *counting / information-theoretic* — minimum bits of persistent state recording a window of $n$ committed transactions so that recovery reconstructs the committed prefix.

The bound must hold against an adversarial crash that can occur at any instruction and (on persistent memory) reorder un-fenced stores.

## 2. Mathematical Foundations

Model the system as a state machine whose volatile state $V$ is lost on crash and whose persistent state $P$ survives. A *durability protocol* is a schedule of persist operations $\pi_1,\dots,\pi_k$ such that for any crash point $t$, a recovery function $R(P_t)$ recovers exactly the set of transactions that were *acknowledged-committed* before $t$.

The **counting lower bound** is information-theoretic: if a window admits $N$ distinguishable committed-prefix outcomes that recovery must tell apart, then $P$ must encode at least $\log_2 N$ bits — a pigeonhole / Kraft argument. For $n$ independently committable transactions over a domain producing $2^{\Omega(n)}$ recoverable states, $\Omega(n)$ bits of persistent writes are unavoidable.

The **ordering lower bound** uses an adversary argument on persistence order. If commit $c_2$ depends on $c_1$ (read-from or write-after-write), then any reordering that persists $c_2$'s effect before $c_1$'s leaves a recoverable state violating prefix-consistency; a fence is required on the path, giving a lower bound parameterized by the dependency DAG's antichain structure.

For amortized I/O, the relevant frame is the **external-memory / DAM model** with block size $B$: writing $W$ log records costs $\Omega(W/B)$ I/Os, and group commit cannot beat this when commit arrival is adversarially spread. Latency lower bounds invoke the synchronous-wait structure (one stable-storage round trip per durability point unless commits are batched).

## 3. State of the Art (SOTA)

There is no single tight theory; SOTA is a patchwork. The information-theoretic $\Omega(n)$-bits intuition is folklore from Gray & Reuter. Systems-SOTA effectively *defines* the achievable upper envelope: physiological logging (ARIES) pays one log record per update plus a forced flush per commit; command/logical logging shrinks write volume at recovery-time cost; **group commit** (DeWitt et al., 1984) amortizes the fence; **early lock release** and **controlled lock violation** (Graefe et al., 2013) remove the commit wait from the critical path without weakening durability. On NVM, **persist-ordering lower-bound reasoning** appears in work on epoch persistency and the BzTree / log-free structures, but bounds are stated per-construction, not universally.

## 4. Upper Bound

Best constructive upper bounds: amortized **$O(1)$ fences per committed transaction** under group commit, and as low as **one persistent-write per transaction** for log records when updates are coalesced. With distributed/replicated durability, a single round of stable writes suffices (one I/O round trip per commit, batchable to $O(1/k)$ amortized for batch size $k$). On persistent memory, log-free / single-flush designs (e.g., link-and-persist, BzTree's persistent multi-word CAS) achieve **a constant number of flushes per operation**, independent of structure size.

## 5. Lower Bound

- **Information-theoretic:** $\Omega(n)$ bits of persistent writes to recover a committed prefix of $n$ distinguishable transactions (pigeonhole on recoverable states).
- **Ordering:** at least one persist-ordering fence per *commit dependency edge that crosses a persistence boundary*; an adversary that reorders un-fenced stores forces this.
- **I/O round trips:** $\Omega(1)$ synchronous stable-storage wait per durability point that is not batched; no protocol can acknowledge a commit before its effects are stably ordered (a FLP-flavored "no premature ack" impossibility).

These are individually tight in their isolated models but do not compose into one tight, workload-parameterized statement.

## 6. The Gap

The gap is genuinely open. We have a clean info-theoretic *volume* bound and clean *per-dependency* fence bounds, but no theory tying write-volume, fence-count, and latency together as a Pareto frontier parameterized by workload (dependency structure, conflict rate) and storage model (block device vs. byte-addressable NVM with epoch persistency). Closing it requires a single model in which group commit, logical logging, and NVM fence-elision are all special cases, plus matching adversary lower bounds in that model.

## 7. Current Research (as of June 2026)

Active threads: fine-grained "persist cost" accounting for NVM data structures and formal **persistency models** (Px86, ARMv8 persistency) feeding lower-bound arguments *(frontier — verify)*; work from the durable-linearizability community (Izraelevitz, Mendes, Scott) on the cost of recoverable objects; CMU and MIT-adjacent groups on log-structured and constant-flush NVM indexes. A recurring 2025–2026 claim is matching upper/lower bounds for *fence count* in epoch-based persistency *(frontier — verify)*.

## 8. Future Work

- A workload-parameterized Pareto lower bound jointly over {bytes, fences, round trips}.
- Bounds under realistic NVM persistency (partial cache-line atomicity, out-of-order persist) rather than idealized stable storage.
- Connecting durability lower bounds to consensus/replication lower bounds (the "one round trip" floor).
- Tight bounds for logical/command logging where recovery does compute, trading persist volume for replay time.

## 9. Key References

- **[Foundational]** Jim Gray, Andreas Reuter. *Transaction Processing: Concepts and Techniques.* Morgan Kaufmann, 1993. — [WorldCat](https://search.worldcat.org/title/transaction-processing-concepts-and-techniques/oclc/26303792)
- **[Foundational]** C. Mohan et al. *ARIES: A Transaction Recovery Method Supporting Fine-Granularity Locking and Partial Rollbacks Using Write-Ahead Logging.* ACM TODS, 1992. — [DOI](https://dl.acm.org/doi/10.1145/128765.128770)
- **[SOTA]** Goetz Graefe, Mark Lillibridge, Harumi Kuno, et al. *Controlled Lock Violation.* SIGMOD, 2013. — [DOI](https://dl.acm.org/doi/10.1145/2463676.2465325)
- **[SOTA]** Joseph Izraelevitz, Hammurabi Mendes, Michael L. Scott. *Linearizability of Persistent Memory Objects under a Full-System-Crash Failure Model.* DISC, 2016. — [DOI](https://doi.org/10.1007/978-3-662-53426-7_23)
- **[Survey]** Alexander van Renen, Viktor Leis, et al. *Persistent Memory I/O Primitives / managing NVM.* (survey-style treatments of persist cost), 2019. — [arXiv](https://arxiv.org/abs/1904.01614)

## 10. Worked Example

Consider committing $n = 4$ independent transactions, each setting one of four distinct keys to one of two values. The number of distinguishable committed-prefix outcomes recovery must tell apart is $2^4 = 16$, so $P$ must store at least $\log_2 16 = 4$ bits — the counting lower bound $\Omega(n)$ in miniature. No encoding, however clever, recovers all 16 states from fewer than 4 bits.

Now the fence bound. Suppose $c_2$ read-from $c_1$ and $c_4$ depends on $c_3$, but the two pairs are independent. The dependency DAG has two cross-boundary edges, so at least $2$ persist-ordering fences are required: a fence between $c_1\!\to\!c_2$ and between $c_3\!\to\!c_4$. With group commit batching all four into one flush, the *I/O round trips* drop to $1$ (amortized $1/4$ per commit), yet the $2$ ordering fences remain — they track dependency depth, not batch size. So bytes $=4$, fences $=2$, round trips $=1$: three separate floors, hit by three separate arguments, with no single tight law tying them together.

---
*Part of the [DBMS Research catalog](../../README.md).*
