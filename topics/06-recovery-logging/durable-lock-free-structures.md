# Durable lock-free data structures

> **Topic:** Recovery, Logging & Durability · **ID:** `06-recovery-logging/durable-lock-free-structures` · **Status:** partially-solved

## 1. Problem Statement

Build concurrent data structures (queues, stacks, hash tables, B-trees, skip lists) on byte-addressable persistent memory (PM) that are simultaneously:

- **Lock-free** — system-wide progress is guaranteed; at least one thread completes an operation in a bounded number of steps regardless of delays or failures of others.
- **Durably linearizable** — after a full-system crash, the recovered state is a consistent linearization of exactly the operations that completed (or were appropriately persisted) before the crash, with no torn or "lost-but-acknowledged" updates.

The challenge is doing this at **low persistence cost**: minimizing the number of cache-line flushes (`clwb`/`clflushopt`) and store fences (`sfence`) on the critical path, since each is far more expensive than a volatile memory access.

Variants: (a) *decision* — does a given construction satisfy durable linearizability under a model M? (b) *optimization* — minimize flushes/fences per operation; (c) *progress-refinement* — achieve wait-freedom or bounded recovery time, not merely lock-freedom.

## 2. Mathematical Foundations

The substrate is **linearizability** (Herlihy & Wing, 1990): a concurrent history is correct iff it is equivalent to a legal sequential history respecting real-time order. Durability extends this through correctness conditions formalized by Izraelevitz, Mendes & Scott (2016):

- **Durable linearizability:** the history obtained by appending operations that persisted before the crash is linearizable.
- **Buffered durable linearizability:** a weaker condition allowing a bounded suffix of completed-but-unpersisted operations to be lost, recovered up to an explicit *sync* point.

Formally, persistent state evolves under a **persistency model** $\mathcal{M}$ (e.g., Px86, epoch persistency) defining a partial *persist order* $\le_p$ over stores. A construction is durably linearizable iff for every crash cut, the set $S$ of persisted writes forms a *consistent cut* of the linearization order: $\le_p$ must respect the happens-before edges induced by linearization points. The minimal-flush problem is then: find the smallest set of fence placements that enforces $\le_p \supseteq$ (required commit-dependency edges). Lower bounds invoke an adversary that reorders un-fenced stores within an epoch.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** General *transforms* turning any linearizable lock-free object into a durably linearizable one — Izraelevitz et al.'s construction adds $O(1)$ flushes per shared-memory access (often too many in practice). The **Mirror** (Friedman et al., PLDI 2021) and **NVTraverse** (Friedman et al., 2020) constructions reduce flushes by exploiting traversal structure.
- **Systems-SOTA:** Hand-tuned structures — **link-and-persist** for lock-free lists; the **log-free concurrent hash index (Dash)** (Lu et al., VLDB 2020); **BzTree** (Arulraj et al., VLDB 2018) using persistent multi-word CAS (PMwCAS); persistent Michael-Scott queues; **RECIPE** (Lee et al., SOSP 2019), which gives a principled recipe converting concurrent indexes to crash-consistent ones.

## 4. Upper Bound

For general transforms, the best automatic constructions add a **constant number of flushes per memory operation** that mutates shared state, with **$O(1)$ fences per linearized update** (model: Px86 / explicit epoch persistency). Hand-tuned structures achieve as few as **one flush + one fence per update operation** by detaching read traversals (which need no persistence) from the mutating tail (NVTraverse-style: only nodes "in the data structure" are persisted). PMwCAS achieves multi-word atomic durable update with a constant number of persistence barriers amortized.

## 5. Lower Bound

Persistence cost lower bounds are per-model and partial:

- Any durably linearizable update whose effect must outlive a crash requires **at least one persist barrier on its critical path** between making the update visible and acknowledging it (an adversary reordering un-fenced stores otherwise produces an inconsistent recoverable cut).
- For **detectable** operations (recovery can tell whether an operation took effect), an information-theoretic argument shows extra persistent state per operation is needed; detectability strictly increases cost (Friedman et al.).
- No tight universal lower bound on flush *count* as a function of structure shape exists; bounds are stated per construction.

## 6. The Gap

Partially solved: we have working low-cost structures and general transforms, but the transforms are not flush-optimal and the optimal hand-tuned bounds are not matched by any automatic method. The gap is between $O(1)$-per-*access* (transforms) and $O(1)$-per-*operation* (best manual). Closing it needs a flush-minimizing compiler/transform with a matching lower bound parameterized by the object's dependency structure, under a realistic persistency model rather than idealized stable stores.

## 7. Current Research (as of June 2026)

Active directions: detectable recoverable objects and their inherent cost (Attiya, Ben-Baruch, Hendler); flush-minimizing transforms and verified persistency (the Scott/Rochester group, Technion); formal persistency semantics (Px86, ARMv8) feeding mechanized proofs of crash consistency *(frontier — verify)*. There is growing interest in CXL-attached memory shifting the persistency model and reviving these questions for disaggregated PM *(frontier — verify)*.

## 8. Future Work

- A provably flush-optimal automatic transform with matching lower bounds.
- Wait-free (not just lock-free) durable structures with bounded recovery.
- Durable linearizability under weak persistency (epoch/buffered) with formal recovery-time guarantees.
- Adapting these designs to CXL/disaggregated byte-addressable memory where the failure domain differs from local PM.

## 9. Key References

- **[Foundational]** Maurice Herlihy, Jeannette Wing. *Linearizability: A Correctness Condition for Concurrent Objects.* ACM TOPLAS, 1990. — [DOI](https://doi.org/10.1145/78969.78972)
- **[Foundational]** Joseph Izraelevitz, Hammurabi Mendes, Michael L. Scott. *Linearizability of Persistent Memory Objects under a Full-System-Crash Failure Model.* DISC, 2016. — [DOI](https://doi.org/10.1007/978-3-662-53426-7_23)
- **[SOTA]** Michal Friedman, Naama Ben-David, Yuanhao Wei, Guy Blelloch, Erez Petrank. *NVTraverse: In NVRAM Data Structures, the Destination Is More Important than the Journey.* PLDI, 2020. — [arXiv](https://arxiv.org/abs/2004.02841)
- **[SOTA]** Se Kwon Lee, Jayashree Mohan, Sanidhya Kashyap, Taesoo Kim, Vijay Chidambaram. *RECIPE: Converting Concurrent DRAM Indexes to Persistent-Memory Indexes.* SOSP, 2019. — [arXiv](https://arxiv.org/abs/1909.13670)
- **[SOTA]** Joy Arulraj, Justin Levandoski, Umar Farooq Minhas, Per-Åke Larson. *BzTree: A High-Performance Latch-free Range Index for Non-Volatile Memory.* VLDB, 2018. — [DOI](https://doi.org/10.1145/3164135.3164147)

## 10. Worked Example

Consider a lock-free Michael-Scott queue on persistent memory, enqueueing node $x$. The volatile linearization point is the CAS that swings `tail.next` from `NULL` to `&x`. A naive durable version flushes *every* shared write it touches during the traversal to find the tail.

**Naive (Izraelevitz transform):** suppose finding the tail walks 3 nodes (`n1 → n2 → n3`) and re-reads `tail` once. The transform inserts a `clwb`+`sfence` after each shared read/write to keep persist order $\le_p$ consistent: roughly 4 flushes + 4 fences for one `enqueue`.

**NVTraverse insight ("destination > journey"):** the traversal reads `n1,n2,n3` but does *not* mutate them, so on a crash an un-persisted traversal is simply re-done — those reads need no persistence. Only the *destination* writes must be durable: persist the new node $x$'s contents, then `sfence`, then CAS `tail.next`, then persist that one pointer + `sfence`.

Cost drops from $\approx 4$ flushes / $4$ fences to **1 flush + 1 fence for the node payload and 1 flush + 1 fence for the link** — matching the lower bound of $\ge 1$ persist barrier on the critical path, illustrating the $O(1)$-per-*access* vs. $O(1)$-per-*operation* gap.

---
*Part of the [DBMS Research catalog](../../README.md).*
