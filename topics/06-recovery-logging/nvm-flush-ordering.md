# NVM logging without flush ordering

> **Topic:** Recovery, Logging & Durability · **ID:** `06-recovery-logging/nvm-flush-ordering` · **Status:** open

## 1. Problem Statement

On byte-addressable persistent memory (PMEM/NVM, and emerging CXL-attached persistent tiers), a store reaches the CPU cache, not durability. To make a write durable in a controlled order, software must issue cache-line flushes (`clwb`/`clflushopt`) and ordering fences (`sfence`), and the WAL invariant "log record durable before the data it protects" must be enforced with these instructions. These flush/fence operations are *expensive* and lie on the persistence critical path; a naive durable update may cost several flush+fence pairs.

**Problem:** design durability/logging protocols that **minimize or eliminate** cache-line flush and fence *ordering* on the critical path, while still guaranteeing crash-recoverability under realistic persistence reordering. Concretely: how few fences per durable transaction are required, and can ordering be replaced by *self-verifying* / *order-free* techniques (checksums, monotonic markers, idempotent replay) so that recovery tolerates arbitrary persist order?

Variants: (a) eliminate *intra-record* ordering (torn-write detection without fences); (b) eliminate *inter-record* ordering (log entries persisted in any order); (c) eliminate the *log-before-data* fence via undo/redo-free or epoch-based schemes; (d) optimization: minimize fences subject to a target durability latency.

## 2. Mathematical Foundations

Persistence is governed by a **persistency model** (analogous to a memory-consistency model): Px86 (Intel), ARMv8 persistency, and the abstract **epoch persistency** of Pelley et al. A program's stores form a partial order; the persistency model defines which **persist orderings** the hardware guarantees and which require explicit fences. Let $\le_{po}$ be program order, $\le_{pm}$ the persist order; without fences, $\le_{pm}$ may reorder concurrent stores arbitrarily within an *epoch*; a fence imposes $\le_{pm}$ between epochs.

Crash recovery must hold for *every* legal $\le_{pm}$. The order-free design goal is to make the log record **self-describing and validatable**: append a checksum/CRC and a monotonically increasing sequence marker so recovery accepts a record iff its checksum verifies *and* it forms an unbroken prefix. Then the only required guarantee is that a record is *atomically valid-or-absent*, achievable with a single trailing flush rather than ordered fences. Idempotent **redo** (apply iff `pageLSN < LSN`) means out-of-order persisted updates converge to the same state — recovery is a fold over a partially-ordered multiset that is order-insensitive.

Formally, an order-free protocol is correct iff its recovery function $R$ is *invariant under all persist-order linearizations consistent with the persistency model*: $\forall \sigma_1,\sigma_2 \in \text{Lin}(\le_{pm}):\ R(P_{\sigma_1}) = R(P_{\sigma_2})$ and equals the committed prefix. This is a confluence property.

## 3. State of the Art (SOTA)

- **Epoch persistency / BPFS** (Condit et al., SOSP 2009; Pelley, Chen, Wenisch, ISCA 2014) — coarse-grained ordering via epochs instead of per-write fences; the foundational relaxation.
- **Log-free / single-flush data structures** — **BzTree** (Arulraj, Levandoski, et al., VLDB 2018) uses a persistent multi-word CAS (PMwCAS) to make updates durable with bounded flushes; **link-and-persist** and **FAST&FAIR** (Hwang et al., FAST 2018) tolerate inconsistency via search-layer recovery, avoiding logging entirely.
- **Checksum/marker-based logging** — many NVM WALs (e.g., in **NOVA**, Xu & Swanson, FAST 2016) make log entries self-validating so persist order among them does not matter; recovery scans and validates.
- **Formal persistency reasoning** — Px86/PArmv8 models (Raad, Vafeiadis et al.; POPL 2020) and **Persistency-aware separation logics** (Pierogi, Spirea) give the semantics order-free proofs build on.

## 4. Upper Bound

Best achieved: **a constant number of flushes and as few as one fence per durable operation** for order-free structures (BzTree-style PMwCAS; link-and-persist). Self-validating logs achieve **zero inter-record ordering** — log records persist in any order, recovery validates by checksum + sequence prefix — so only a single trailing flush per record is on the path. Epoch persistency amortizes fences across many writes within an epoch, $O(1/\text{epoch size})$ fences per write. Lower-level: hardware eADR (extended ADR) removes explicit flushes entirely (the cache is in the persistence domain), reducing the problem to *ordering* only — making order-free designs even cheaper.

## 5. Lower Bound

Information-theoretic / adversarial, not computational. **Atomicity floor:** to detect a torn (partial) persist of a record, you must persist *redundant* validating information (a checksum/marker) — $\Omega(1)$ extra bits per atomic unit; you cannot get free torn-write detection. **Ordering floor:** if commit $c_2$ truly depends on $c_1$ across a persistence boundary and recovery must observe the prefix property, at least one fence (or an equivalent epoch boundary) is required between them — an adversary persisting un-fenced stores in reverse yields an unrecoverable state. So fences can be *amortized* and *batched* to $O(1/k)$, but the *number of distinct persistence epochs* needed equals the depth of cross-epoch dependencies, which is $\ge 1$ and can be forced larger by dependency chains. No protocol achieves *zero* ordering when dependencies cross commit boundaries.

## 6. The Gap

Genuinely open. We have order-free constructions per data structure and self-validating logs, but no general theory giving, for an arbitrary workload + persistency model, the *minimum* number of fences/epochs and matching protocol. The gap: between practical "few flushes" designs and a tight lower bound on persistence-ordering operations parameterized by the dependency DAG and the specific persistency model (Px86 vs ARMv8 vs epoch). Hardware shifts (eADR, CXL) keep moving the target. Closing it needs a unified cost model over persistency models and a matching adversary lower bound.

## 7. Current Research (as of June 2026)

Active: persistency-aware program logics and verified order-free structures (Vafeiadis/Raad — MPI-SWS; Spirea, Pierogi) *(frontier — verify)*; CXL-attached memory and its (different) persistence semantics; exploiting **eADR** so flushes vanish and only ordering remains, redesigning logs accordingly; fence-minimization compilers that insert the provably-minimal fence set for a persistency model *(frontier — verify)*. Groups: Wenisch/Chen (Michigan, epoch persistency lineage), Swanson (UCSD, NOVA), Vafeiadis/Raad (persistency semantics), Arulraj/Pavlo (NVM systems).

## 8. Future Work

- A tight, persistency-model-parameterized lower bound on fences/epochs per transaction.
- Provably fence-minimal compilation for a given persistency model.
- Order-free logging under partial-write and media-failure models (not just reordering).
- Re-architecting WAL for eADR/CXL where the durability domain includes the cache.

## 9. Key References

- **[Foundational]** Jeremy Condit, Edmund B. Nightingale, Christopher Frost, et al. *Better I/O Through Byte-Addressable, Persistent Memory (BPFS).* SOSP, 2009. — [DOI](https://dl.acm.org/doi/10.1145/1629575.1629589)
- **[Foundational]** Steven Pelley, Peter M. Chen, Thomas F. Wenisch. *Memory Persistency.* ISCA, 2014. — [DOI](https://doi.org/10.1109/ISCA.2014.6853222)
- **[SOTA]** Joy Arulraj, Justin Levandoski, Umar Farooq Minhas, Per-Åke Larson. *BzTree: A High-Performance Latch-Free Range Index for Non-Volatile Memory.* VLDB, 2018. — [DOI](https://dl.acm.org/doi/10.1145/3164135.3164147)
- **[SOTA]** Deukyeon Hwang, Wook-Hee Kim, Youjip Won, Beomseok Nam. *Endurable Transient Inconsistency in Byte-Addressable Persistent B+-Tree (FAST&FAIR).* FAST, 2018. — [USENIX](https://www.usenix.org/conference/fast18/presentation/hwang)
- **[SOTA]** Azalea Raad, John Wickerson, Gil Neiger, Viktor Vafeiadis. *Persistency Semantics of the Intel-x86 Architecture (Px86).* POPL, 2020. — [DOI](https://dl.acm.org/doi/10.1145/3371079)

## 10. Worked Example

Append one WAL record to NVM: payload $48$ B plus a trailing $4$ B CRC and a $4$ B monotonic sequence number $s$. The cache lines holding it may persist in any order $\le_{pm}$ within an epoch.

**Naive ordered scheme:** flush payload, `sfence`, flush header/CRC, `sfence` — $2$ flushes + $2$ fences per record to guarantee the CRC is durable only after the payload.

**Order-free scheme:** issue `clwb` on all lines, then a *single* trailing `sfence`. Recovery scans records and accepts record $i$ iff (a) $\text{CRC}(payload_i)$ verifies and (b) $s_i = s_{i-1}+1$ forms an unbroken prefix. If the CRC line persisted but the payload did not, the check fails and the record is treated as absent — *atomically valid-or-absent* with no inter-record ordering. So fences drop from $2$ to effectively $1/\text{epoch}$.

The lower bound still bites: the $4$ B CRC is the $\Omega(1)$ redundant-bits *atomicity floor* — you cannot detect a torn write for free. And if record $j$'s commit truly depends on record $i$'s across an epoch, at least one fence between them is unavoidable: an adversary persisting $j$ before $i$ yields an unrecoverable prefix.

---
*Part of the [DBMS Research catalog](../../README.md).*
