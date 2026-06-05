# Crash-consistent persistent-memory indexes

> **Topic:** Hardware-Conscious Databases · **ID:** `29-hardware-conscious-db/pmem-crash-consistent-index` · **Status:** partially-solved

## 1. Problem Statement

Byte-addressable persistent memory (PMEM/NVM, e.g. Intel Optane DCPMM, and successors) sits on the memory bus: loads/stores reach it directly, but durability requires explicit cache-line flushes (`CLWB`/`CLFLUSHOPT`) plus store fences (`SFENCE`), and only 8-byte aligned stores are guaranteed atomic. The problem: design tree or hash indexes that are (a) **crash-consistent** — every crash leaves a state recoverable to a consistent index without unbounded scan, (b) **concurrent and ideally lock-free**, and (c) **flush/fence-frugal**, since each ordered persist is expensive and writes wear and amplify on the media.

Variants:
- **Decision:** is a given update protocol crash-consistent under the persistency model (does every crash-reachable state recover)?
- **Optimization:** minimize the number of `CLWB`+`SFENCE` ordering points per insert/update while preserving correctness and concurrency.

## 2. Mathematical Foundations

Reasoning rests on a **persistency model**: an ordering relation over persists distinct from the memory-consistency order. *Epoch persistency* and *strict persistency* (Pelley, Chen, Wenisch, ISCA 2014) formalize when a store is durable relative to others. A structure is crash-consistent if, for every prefix of the persist order, the recovered state satisfies the index invariant — analogous to **linearizability extended with a durability point** (*durable linearizability* / *buffered durable linearizability*, Izraelevitz, Mendes, Scott, DISC 2016).

Atomicity primitive: only an 8-byte aligned word flips atomically. Larger transitions need a **redo/undo log** or a **failure-atomic CAS** built from it. The flush-frequency cost is the count of `flush;fence` ordering points; the lower-bound questions connect to the persistent-memory analogue of cell-probe complexity and to RAWL-style write amplification (see companion problem).

## 3. State of the Art (SOTA)

Systems-SOTA is mature for *some* points in the design space:
- **B+-tree family:** *NV-Tree* (Yang et al., FAST 2015) keeps leaves consistent while leaving internal nodes volatile/rebuildable; *FAST&FAIR* (Hwang et al., FAST 2018) achieves failure-atomicity using only ordered stores (no logging) by tolerating transiently duplicated keys; *BzTree* (Arulraj et al., VLDB 2018) is lock-free via persistent multi-word CAS (PMwCAS).
- **Hash family:** *CCEH* (Nam et al., FAST 2019) gives cache-line-conscious extendible hashing with low-overhead resizing; *Dash* (Lu et al., VLDB 2020) and *Level Hashing* (Zuo et al., OSDI 2018) reduce writes on rehash.
- **Hybrid DRAM+PMEM:** *uTree*, *FPTree* (Oukid et al., SIGMOD 2016) — selective persistence: inner nodes in DRAM, leaves in PMEM.

## 4. Upper Bound

Achievable: insert/update with **O(1) ordering points** in the common (no split) case. FAST&FAIR performs node updates with a *single* failure-atomic store sequence and **no logging** for in-node operations, paying extra flushes only on structural modification (splits). BzTree gives lock-free updates with a bounded number of persists per PMwCAS. Recovery is O(structure-size) at worst but O(1)-bounded "in-flight" operations to roll forward/back. Space overhead is O(n) with small constants.

## 5. Lower Bound

Any durable update that crosses an 8-byte atomicity boundary provably needs at least one ordering point (`flush;fence`) to be crash-consistent — you cannot make a >8-byte transition atomic for free. For ordered structures, a node split or rebalance touches multiple cache lines and thus requires $\Omega(1)$ but provably $>1$ flushes in the worst case (formalized in the companion write-amplification problem). There is no constant-round lower bound separating the best logging-free schemes from optimal; the precise per-operation flush lower bound for *sorted* PMEM nodes remains the sharp open question.

## 6. The Gap

For *unsorted* / hash and for *single-key* updates, theory and practice nearly meet: logging-free O(1)-flush protocols exist and are proven crash-consistent. The residual gap is concentrated on **structural modifications under concurrency**: combining lock-freedom, minimal flushes on split/merge, and durable linearizability simultaneously is done by separate systems but no single design provably optimizes all three, and there is no matching lower bound for sorted-node splits. Hence **partially-solved**. Real hardware shifts (Optane's discontinuation, CXL persistent tiers) also reopen the cost model.

## 7. Current Research (as of June 2026)

- Re-targeting PMEM index techniques to **CXL-attached memory and battery-backed DRAM**, since Optane's EOL changed the durability primitive's cost profile *(frontier — verify)*.
- Formal verification of crash consistency (model-checking persist orders) — work from the persistency-semantics community (Vafeiadis et al.) *(frontier — verify)*.
- Learned/adaptive node layouts minimizing flush counts. Active groups: UCSD (Swanson, NVSL), KAIST (Nam/Won), Virginia Tech, TU Dresden.

## 8. Future Work

- A tight per-operation flush lower bound for sorted PMEM nodes, with a matching protocol.
- Lock-free + minimal-flush + durable-linearizable index in one design with a proof.
- Verified crash-consistency toolchains usable by systems builders.
- Portability across persistency models (x86 epoch vs. ARM DC CVAP).

## 9. Key References

- **[Foundational]** Pelley, Chen, Wenisch. *Memory Persistency.* ISCA, 2014. — [DOI](https://doi.org/10.1145/2678373.2665712) — [DBLP](https://dblp.org/rec/conf/isca/PelleyCW14.html)
- **[Foundational]** Izraelevitz, Mendes, Scott. *Linearizability of Persistent Memory Objects under a Full-System-Crash Failure Model.* DISC, 2016. — [DOI](https://doi.org/10.1007/978-3-662-53426-7_23) — [DBLP](https://dblp.org/rec/conf/wdag/IzraelevitzMS16.html)
- **[SOTA]** Hwang, Kim, Won, Nam. *Endurable Transient Inconsistency in Byte-Addressable Persistent B+-Tree (FAST&FAIR).* FAST, 2018. — [USENIX](https://www.usenix.org/conference/fast18/presentation/hwang) — [DBLP](https://dblp.org/rec/conf/fast/HwangKWN18.html)
- **[SOTA]** Arulraj, Levandoski, Minhas, Larson. *BzTree: A High-Performance Latch-free Range Index for Non-Volatile Memory.* VLDB, 2018. — [DOI](https://doi.org/10.1145/3164135.3164147) — [DBLP](https://dblp.org/rec/journals/pvldb/ArulrajLML18.html)
- **[SOTA]** Lu, Hao, Wang, Lo. *Dash: Scalable Hashing on Persistent Memory.* VLDB, 2020. — [DOI](https://doi.org/10.14778/3389133.3389134) — [arXiv](https://arxiv.org/abs/2003.07302)
- **[Foundational]** Oukid, Lasperas, Nica, Willhalm, Lehner. *FPTree: A Hybrid SCM-DRAM Persistent and Concurrent B-Tree.* SIGMOD, 2016. — [DOI](https://doi.org/10.1145/2882903.2915251) — [DBLP](https://dblp.org/rec/conf/sigmod/OukidLNWL16.html)

## 10. Worked Example

Consider a sorted PMEM B+-tree leaf holding 8-byte keys in a packed array, one cache line ($L=64$ B) = 8 slots. Current contents: $[10, 20, 30, \_, \_, \_, \_, \_]$. We insert key $25$, which belongs at index 2.

**Naive logged insert.** Write an undo-log record, fence, shift $30 \to$ slot 3, write $25$ into slot 2, fence, then clear the log: $\ge 3$ ordering points.

**FAST insert (logging-free).** Shift right one slot at a time using *failure-atomic 8-byte stores*, tolerating a transient duplicate:
1. Copy slot 2's value ($30$) into slot 3 → array $[10,20,30,30,\dots]$. A crash here is recoverable: a reader sees a duplicate $30$, which FAIR's recovery deduplicates — the tree invariant (sorted, no lost key) still holds.
2. Overwrite slot 2 with $25$ → $[10,20,25,30,\dots]$.

Because all writes land in **one 64-byte cache line**, a single `CLWB`+`SFENCE` persists the whole result: **1 ordering point**, no log. This is the $O(1)$-flush common case of section 4.

**When the bound bites:** inserting at index 0 of a *full* line forces shifting all 8 slots; if the node spans 2 lines, the shift crosses a line boundary and now needs $\ge 2$ flushes — the $\Omega((B-p)/(L/w))$ shift cost of section 5 (here $w=8$, $L/w=8$). A node *split* (structural modification) is where minimal-flush + lock-freedom + durable linearizability remain jointly open.

---
*Part of the [DBMS Research catalog](../../README.md).*
