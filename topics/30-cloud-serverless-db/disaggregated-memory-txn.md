# Disaggregated-memory transaction protocols

> **Topic:** Cloud & Serverless Databases · **ID:** `30-cloud-serverless-db/disaggregated-memory-txn` · **Status:** empirically-open

## 1. Problem Statement

In **memory disaggregation**, working memory is not local DRAM but a pool of *remote* memory nodes reached over RDMA (one-sided READ/WRITE/CAS) or CXL. Compute nodes are largely *stateless* and **failure-independent** from memory nodes: either side can crash without the other. The problem: design **concurrency control + logging/recovery** for transactions whose data, indexes, locks, and even latches live in remote, byte-addressable memory that the compute node manipulates with one-sided verbs and a weak set of remote atomics.

Core difficulties: a one-sided RDMA op gives no remote CPU to run a critical section, so traditional latching/2PL must be reimplemented from remote CAS; a compute crash can leave remote locks held and partial writes; a memory crash loses uncommitted (and possibly committed-but-unflushed) state. Variants:
- **Decision:** does a CC protocol over a verb set $V$ (e.g., {READ, WRITE, CAS, FAA}) achieve serializability with $O(1)$ round-trips per conflict-free transaction?
- **Optimization:** minimize RDMA round-trips / network-atomics per transaction and recovery time, subject to strict serializability and independent-failure durability.

## 2. Mathematical Foundations

The interface is an **asynchronous shared-memory** model with a restricted primitive set. Its power is bounded by the **consensus number** hierarchy (Herlihy): atomic registers (READ/WRITE) have consensus number 1 and cannot solve wait-free consensus, so coordination *must* rest on CAS/FAA (consensus number $\infty$). Hence remote-atomic availability dictates which CC/recovery protocols are even possible.

Correctness is the standard **serializability/CSR** condition (acyclic conflict graph) but enforced via remote primitives; recovery correctness is **write-ahead logging** with the durability ordering of ARIES (Mohan et al.), reframed so the *log* lives in failure-independent remote memory. Failure independence is modeled as a **crash–recovery** system with separate fault domains; safe handoff of orphaned locks after a compute crash is a *fault-tolerant reconfiguration* problem subject to **FLP** (no wait-free consensus under pure asynchrony + crash) — so protocols assume failure detectors / leases / partial synchrony. Memory-pool replication for durability invokes quorum theory (Lamport's $f+1$-of-$2f+1$).

## 3. State of the Art (SOTA)

**Systems-SOTA.** *FaRM* (Dragojević et al., NSDI 2014; SOSP 2015) pioneered RDMA-based transactions with optimistic CC + 2PC over one-sided reads and a fast lock-free commit, plus replicated durable memory. *FaSST* (Kalia, Kaminsky, Andersen; OSDI 2016) argued two-sided datagram RPC beats one-sided verbs for transactions at scale. *DrTM / DrTM+R / DrTM+H* (Wei et al., SOSP 2015, EuroSys 2016, OSDI 2018) combine HTM with RDMA and tune the one-sided/two-sided mix. The disaggregated-memory wave: *FaRM-style* designs adapted to compute/memory separation, *Clover/pDPM* (Tsai, Shan, Zhang; ATC 2020) for passive disaggregated persistent memory, *Sherman* (Wang et al., SIGMOD 2022) — an RDMA B-tree index for disaggregated memory with on-chip-lock and write-combining optimizations, *FORD* (Zhang et al., FAST 2022) — fast one-sided RDMA transactions for disaggregated memory, and *Motor*/*dLSM*-style follow-ups. **CXL**-based memory pooling (Pond, ASPLOS 2023) is the emerging hardware substrate.

**Theory-SOTA.** The wait-free/lock-free hierarchy (Herlihy) and disaggregated-memory data-structure lower bounds (Aguilera et al., HotOS/PODC line) frame what one-sided primitives can do.

## 4. Upper Bound

Conflict-free transactions can commit in a *constant* number of RDMA round-trips: FaRM-style optimistic execution reads versions with one-sided READs and commits with a small fixed number of phases; FORD and FaSST report transactions at single-digit microsecond latency and millions of txns/s. For indexing, Sherman achieves near-RPC throughput for a tree using one-sided ops plus a hybrid lock. Thus the **upper bound is $O(1)$ network round-trips per uncontended transaction** in the one-sided/two-sided RDMA model, with recovery time bounded by replicated-log replay. These are systems upper bounds; the matching analytical model is the asynchronous shared-memory machine with bounded message size.

## 5. Lower Bound

Lower bounds are primitive- and round-driven. **(a)** With only atomic READ/WRITE (consensus number 1, Herlihy) some coordination tasks are *impossible* wait-free; safe orphaned-lock recovery after a compute crash needs consensus-number-$\infty$ primitives or external failure detectors — pure asynchrony + crash is blocked by **FLP**. **(b)** One-sided-only protocols pay extra round-trips: certain operations provably need $\Omega(\log n)$ or multiple round-trips because the memory side cannot execute a critical section (data-structure lower bounds for "passive" memory, Aguilera et al.). **(c)** CAP applies to replicated durable memory: linearizable + available across a memory-pool partition is impossible. **(d)** Cell-probe-style bounds lower-bound remote-access counts for ordered dictionaries. No single tight bound spans the full txn protocol; pieces are known.

## 6. The Gap

Genuinely **open**. Empirically, RDMA/disaggregated transactions hit microsecond latencies, but there is no tight theory pinning the *minimal* number of network round-trips and remote atomics for serializable commit + failure-independent recovery as a function of the available verb set and the contention level. The interplay of one-sided vs two-sided, the cost of orphaned-lock cleanup, and durable replication under independent failures lacks a unifying optimality result. CXL's cache-coherent loads/stores may change the primitive set and reopen the design space. Closing the gap needs (i) a formal cost model over $(V,\text{round-trips},\text{atomics})$ and (ii) matching protocol lower bounds for that model.

## 7. Current Research (as of June 2026)

Active: protocols *native* to compute/memory separation that tolerate compute-node crashes without losing remote locks (lease + helper-based cleanup); **CXL 3.0** shared/pooled memory with hardware coherence enabling load/store transactions rather than verbs *(frontier — verify)*; one-sided indexes and learned remote indexes (Sherman successors); and hybrid CXL+RDMA tiered memory engines. Groups/people: Aguilera and collaborators (VMware Research → broad disaggregation theory/systems), Chen/Chen (SJTU — DrTM line), Kaminsky/Andersen (CMU — FaSST/eRPC), and the FAST/OSDI/SIGMOD disaggregated-memory community. Frontier claim: *CXL coherent memory pooling makes one-sided-verb concurrency control partly obsolete, shifting CC back toward shared-memory algorithms over a slower coherence fabric* *(frontier — verify)*.

## 8. Future Work

- A tight round-trip/atomics lower bound for serializable commit on a given verb set, with matching protocols.
- Recovery protocols with provable bounds when *both* fault domains can fail, including orphaned-resource reclamation.
- CC algorithms for CXL coherent pools and the RDMA↔CXL boundary.
- Co-design with disaggregated logging/recovery and elastic repartitioning (see elastic-oltp-repartition).

## 9. Key References

- **[Foundational]** M. Herlihy. *Wait-Free Synchronization.* ACM TOPLAS, 1991. — [DOI](https://doi.org/10.1145/114005.102808)
- **[Foundational]** C. Mohan et al. *ARIES: A Transaction Recovery Method Supporting Fine-Granularity Locking and Partial Rollbacks Using Write-Ahead Logging.* ACM TODS, 1992. — [DOI](https://doi.org/10.1145/128765.128770)
- **[SOTA]** A. Dragojević, D. Narayanan, M. Castro, O. Hodson. *FaRM: Fast Remote Memory.* NSDI, 2014. — [DBLP](https://dblp.org/rec/conf/nsdi/DragojevicNCH14.html)
- **[SOTA]** A. Kalia, M. Kaminsky, D. Andersen. *FaSST: Fast, Scalable and Simple Distributed Transactions with Two-Sided RDMA Datagram RPCs.* OSDI, 2016. — [DBLP](https://dblp.org/rec/conf/osdi/KaliaKA16.html)
- **[SOTA]** Q. Wang et al. *Sherman: A Write-Optimized Distributed B+Tree Index on Disaggregated Memory.* SIGMOD, 2022. — [DOI](https://doi.org/10.1145/3514221.3517824) · [arXiv](https://arxiv.org/abs/2112.07320)
- **[SOTA]** M. Zhang et al. *FORD: Fast One-sided RDMA-based Distributed Transactions for Disaggregated Persistent Memory.* FAST, 2022. — [USENIX](https://www.usenix.org/conference/fast22/presentation/zhang-ming)
- **[Survey]** M. K. Aguilera et al. *Designing Far Memory Data Structures: Think Outside the Box.* HotOS, 2019. — [DOI](https://doi.org/10.1145/3317550.3321433)

## 10. Worked Example

A compute node runs a transfer transaction $T$: read balances $A, B$ in remote memory, check $A \ge 100$, then debit $A$ by 100 and credit $B$. The verb set is $V=\{\text{READ}, \text{WRITE}, \text{CAS}\}$.

*Optimistic FaRM-style commit, conflict-free path.* Each record carries a version stamp.
1. **READ** $A$ and $B$ (with versions $v_A, v_B$) — 1 round trip (batched).
2. Compute locally: $A'=A-100$, $B'=B+100$.
3. **Lock + validate**: issue **CAS** on each record's lock word, checking the version is still $v_A, v_B$ — 1 round trip.
4. **WRITE** new values and release — 1 round trip (can overlap with replication of the log).

Total: a *constant* 3 round trips, independent of data size — the $O(1)$ upper bound of section 4.

*Why a register isn't enough.* Step 3 needs CAS, not plain WRITE. By Herlihy's hierarchy, atomic READ/WRITE registers have consensus number 1 and cannot atomically test-and-set a lock; two compute nodes both doing READ-then-WRITE could both pass the version check and double-spend. CAS (consensus number $\infty$) is what makes the lock atomic.

*Failure wrinkle.* If the compute node crashes between steps 3 and 4, record $A$'s lock word is set with no owner alive — an orphaned lock. Pure asynchrony + crash cannot safely reclaim it (FLP); a lease on the lock word (auto-expiring after $\tau$) or an external failure detector is required, illustrating section 5(a).

---
*Part of the [DBMS Research catalog](../../README.md).*
