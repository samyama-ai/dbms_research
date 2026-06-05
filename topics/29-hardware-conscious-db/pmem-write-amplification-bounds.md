# Persistent-memory write-amplification bounds

> **Topic:** Hardware-Conscious Databases · **ID:** `29-hardware-conscious-db/pmem-write-amplification-bounds` · **Status:** open

## 1. Problem Statement

On byte-addressable persistent memory, a logical update of a few bytes costs more than those bytes: durability requires flushing whole cache lines, the media writes in larger internal units, and consistency protocols (logging, copy-on-write, shadowing) replicate data. **Write amplification (WA)** is the ratio of media bytes (or cache-line flushes) written to logical bytes updated. The question is **lower bounds**: for a durable, crash-consistent update to an *ordered* structure (sorted array, B+-tree node, ordered log), what is the minimum number of cache-line `flush`/`fence` ordering points and media-write units that *any* correct algorithm must incur?

Variants:
- **Counting/cost lower bound:** minimum flushes per durable ordered insert as a function of node size $B$ (cache lines) and position.
- **Amortized:** minimum flushes per operation over a sequence, allowing batching.
- **Decision:** given a flush budget $k$, does a crash-consistent protocol for operation set $S$ exist?

## 2. Mathematical Foundations

Model PMEM as cache lines of $L$ bytes (typically 64) with an atomic-store granularity $w$ (8 bytes). A *persist* is an ordering point: a flush of one line followed (eventually) by a fence. Crash consistency requires that every prefix of the persist order recovers a valid state. This is naturally an **adversary/cell-probe**-style argument: the adversary crashes at the worst persist boundary, and the algorithm must keep the structure recoverable, forcing extra persists or shadow copies.

For a sorted node, inserting a key at position $p$ in a packed array shifts $\Theta(B-p)$ elements across potentially $\Theta((B-p)/(L/w))$ cache lines, each needing a persist — giving a *shift-based* upper bound. The matching lower bound asks whether logging-free schemes can avoid this. Connections: the **encoding/information-theoretic** argument (a durable structure must encode enough to recover), the **RUM conjecture** trade-off (Athanassoulis et al., EDBT 2016) between Read, Update, and Memory overheads, and external-memory $B$-tree write bounds re-cast with the persist as the costly primitive (cf. the $B^\varepsilon$-tree / buffer-tree write amplification analysis).

$$\text{WA}_{\text{flush}}(p,B) \;\ge\; f(B-p)\quad\text{for packed sorted nodes;}$$
the open problem is the tight $f$ across all crash-consistent protocols, not just shifting ones.

## 3. State of the Art (SOTA)

There is no clean, widely accepted tight lower bound. What exists:
- **Upper-bound techniques (write reduction):** unsorted/append-only leaves (FAST&FAIR, FPTree) avoid shifting; *write-optimal* PMEM trees and slot-array layouts amortize. Log-structured and *fingerprint* layouts cut writes on lookup-heavy nodes.
- **Trade-off framing:** the **RUM conjecture** posits you cannot simultaneously minimize read, update, and memory amplification; PMEM adds *persist* amplification as a fourth axis (sometimes "RUMP").
- **Endurance-aware hashing:** Level Hashing, Dash minimize writes on resize as empirical WA optima, but without proven lower bounds.

So the field has good *upper-bound* constructions and a *conceptual* trade-off, but the genuine **lower bound is open**.

## 4. Upper Bound

For a single durable insert into an **unsorted** node with an out-of-band validity bitmap: O(1) flushes (write the entry, then atomically flip an 8-byte slot/bitmap word). For **sorted** nodes via shifting: O(B/(L/w)) flushes worst case; FAST&FAIR reduces the constant by tolerating a transient duplicate so only one ordered store sequence is needed per shift step. Append-only logs: O(1) flushes per record amortized. These are achievable bounds, not proven optimal.

## 5. Lower Bound

Provable so far: any durable transition crossing the $w$-byte atomic boundary needs $\ge 1$ persist (else a crash mid-transition leaves an unrecoverable state) — an information-theoretic / adversary argument. For maintaining **sortedness with in-place packing**, $\Omega(B-p)$ bytes must move and hence $\Omega((B-p)/L)$ cache lines must be re-persisted *within that representation*. The crucial open gap: there is **no proven lower bound forbidding a smarter representation** (indirection, deferred sorting, logarithmic-rebuild) from achieving $o(B)$ persists per ordered insert while preserving O(1)-ish reads. No cell-probe-style bound ties persist count to ordered-search cost the way external-memory bounds tie I/O to range queries.

## 6. The Gap

The gap is wide and **genuinely open**: upper bounds come from clever representations; the only lower bounds are the trivial $\ge 1$ persist and representation-specific shift bounds. We lack a representation-independent lower bound of the form "any crash-consistent ordered structure supporting O(log) search must pay $\Omega(g(B))$ persists per insert," analogous to external-memory or cell-probe results. Closing it requires either such a lower bound (likely via a cell-probe/encoding argument augmented with the persist-ordering adversary) or a construction breaking the shift barrier with provably few persists.

## 7. Current Research (as of June 2026)

- Adapting the analysis to **CXL.mem and asymmetric DRAM-class persistence** as Optane exits, changing the unit of "media write" *(frontier — verify)*.
- Formal cost models unifying RUM with persist amplification, and attempts at cell-probe lower bounds for durable structures *(frontier — verify)*.
- Endurance/wear-aware lower bounds for flash-like media. Groups: Harvard DASlab (Athanassoulis/Idreos lineage), MIT (external-memory/B-tree theory), UCSD NVSL.

## 8. Future Work

- A representation-independent persist lower bound for ordered durable structures.
- Tight amortized bounds allowing batching/group commit on PMEM.
- A "persistent external-memory" model with matching upper/lower bounds.
- Wear-leveling-aware WA bounds.

## 9. Key References

- **[Foundational]** Athanassoulis, Kester, Maas, Stoica, Idreos, Ailamaki, Dittrich. *Designing Access Methods: The RUM Conjecture.* EDBT, 2016.
- **[Foundational]** Pelley, Chen, Wenisch. *Memory Persistency.* ISCA, 2014.
- **[SOTA]** Hwang, Kim, Won, Kim. *Endurable Transient Inconsistency in Byte-Addressable Persistent B+-Tree (FAST&FAIR).* FAST, 2018.
- **[SOTA]** Zuo, Hua, Sun. *Write-Optimized and High-Performance Hashing Index Scheme for Persistent Memory (Level Hashing).* OSDI, 2018.
- **[Foundational]** Brodal, Fagerberg. *Lower Bounds for External Memory Dictionaries.* SODA, 2003.
- **[Survey]** Aurora, Crotty, et al. (and predecessors). *Persistent Memory: a survey of programming and indexing techniques.* (PMEM index/WA surveys), 2020-2021.

---
*Part of the [DBMS Research catalog](../../README.md).*
