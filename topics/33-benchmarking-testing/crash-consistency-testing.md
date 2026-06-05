# Crash-Consistency Testing of Storage Engines

> **Topic:** Benchmarking, Testing & Verification · **ID:** `33-benchmarking-testing/crash-consistency-testing` · **Status:** empirically-open

## 1. Problem Statement

A storage engine promises **durability** and **atomicity**: an acknowledged commit survives a crash, and partially-completed operations recover to a consistent state. Crash-consistency testing asks: *does the engine actually keep these promises across all the states a power failure can leave on disk?*

Formally, fix a workload $W$ and a point during its execution. A crash at that point exposes some **persistent reordering and partial-write** of the engine's I/O to durable media. The tester must:
- **Decision (per state):** for a chosen crash point and a chosen legal reordering of not-yet-persisted writes, recover the engine and check whether the recovered state satisfies the consistency invariant $\Phi$ (e.g., a committed transaction is fully present or fully absent).
- **Search / coverage:** explore the (astronomically large) space of (crash point × persistence permutation) pairs to *find a state that violates* $\Phi$ — a durability or recovery bug.
- **Optimization:** maximize bug-finding per unit of expensive crash-and-recover trials.

The space is enormous: the storage stack may reorder writes, lose un-flushed pages, tear a sector mid-write, or reorder across `fsync` if barriers are misused. Exhaustive enumeration is infeasible; the engineering challenge is principled pruning.

## 2. Mathematical Foundations

Model the disk as a set of blocks; the engine emits an I/O trace $\sigma = o_1 o_2 \dots o_m$ of writes interleaved with **flush/barrier** operations. The **persistence model** $\mathcal{P}$ defines, for a crash after issuing prefix of $\sigma$, the set of **reachable on-disk states** $\mathrm{Reach}_{\mathcal P}(\sigma)$:

- A *flush* ($\mathsf{fsync}$/`FUA`) is a barrier: all writes before it are durable, none after may "jump" it.
- Between barriers, any subset of writes may have persisted, in any order (and a write may be **torn** at sub-block granularity).

$$\mathrm{Reach}_{\mathcal P}(\sigma) = \{\, \text{disk states } d : d \text{ respects barrier ordering of } \sigma \,\}.$$

The correctness obligation is:
$$\forall\, d \in \mathrm{Reach}_{\mathcal P}(\sigma).\quad \mathrm{Recover}(d) \models \Phi_W,$$
where $\Phi_W$ encodes prefix-consistency: the recovered logical state equals the effect of some prefix of the acknowledged-commit sequence. $|\mathrm{Reach}_{\mathcal P}(\sigma)|$ is exponential in the number of writes between barriers, so the tester samples or symbolically reasons over it. ALICE-style frameworks formalize this via *persistence properties* (atomicity, ordering) that the engine assumes but the file system may not provide.

## 3. State of the Art (SOTA)

**Systems-SOTA.**
- **ALICE** (Pillai et al., OSDI 2014) — discovers application-level crash vulnerabilities by abstracting file-system behavior into persistence properties and enumerating legal reorderings.
- **CrashMonkey & ACE** (Mohan et al., OSDI 2018) — *bounded black-box* exploration: ACE systematically enumerates workloads up to a bound, CrashMonkey replays crash states; found dozens of bugs in Linux file systems.
- **Hydra / B³** and **dm-log-writes**-based harnesses — record-and-replay of the block trace with controlled reordering.
- **Jepsen** with **fault injection** (process kill, `kill -9`, container pause) covers crash behavior at the distributed layer.
- Engine-specific: **RocksDB/WiredTiger** ship internal "crash test" loops; PostgreSQL's `pg_isready`/checkpoint torture tests.

**Theory-SOTA.** Model-checking approaches (e.g., **FiSC/eXplode**, Yang et al., OSDI 2006) treat the kernel + engine as a state machine and do stateful exploration; formal verified engines (**FSCQ**, SOSP 2015) *prove* crash consistency under a specified disk model rather than test it.

## 4. Upper Bound

- **Exhaustive** bounded exploration: enumerate all $\mathrm{Reach}_{\mathcal P}(\sigma)$ for workloads with $\le b$ persistence operations — exponential in $b$ but complete for that bound (ACE).
- **Sampling:** uniform or coverage-guided sampling gives no completeness but bounded cost; greedy/coverage maximization is a submodular-coverage problem, admitting a $(1-1/e)$ approximation if a tractable coverage oracle is defined.
- Verified engines (FSCQ) replace testing with proof: $O(1)$ residual risk modulo the assumed disk model and TCB.

## 5. Lower Bound

- The state space $|\mathrm{Reach}_{\mathcal P}(\sigma)|$ is **exponential** in writes-between-barriers; exhaustive coverage is intractable beyond small bounds — an information-theoretic/combinatorial barrier, not merely NP-hardness.
- Bug-finding is **undecidable in general** (it reduces to nontrivial properties of arbitrary recovery code, à la Rice's theorem); testing can only refute, never certify, absent a proof.
- The fault model is itself uncertain: real devices violate the assumed barrier semantics (lying `fsync`, FTL reordering), so even a complete search under model $\mathcal P$ misses bugs outside $\mathcal P$ — a *specification-gap* lower bound.

## 6. The Gap

There is no theoretical "closing" here: completeness is impossible at scale, so the field is **empirically open**. The gap is between (a) what current bounded/black-box explorers cover and (b) the true device-level fault space. Progress = better persistence models validated against real hardware, smarter coverage metrics that prioritize bug-dense regions, and pushing verified engines to cover realistic storage stacks. A closed solution would require either a *trusted, accurate* disk fault model plus full verification, or a coverage criterion proven to dominate the relevant bug classes.

## 7. Current Research (as of June 2026)

- Coverage-guided fuzzing of recovery code (libFuzzer/AFL++ harnesses over the block layer) combined with persistence-aware mutators *(frontier — verify)*.
- Extending crash testing to **NVMe/CXL persistent-memory** semantics, where the failure-atomicity unit and ordering differ from block devices.
- Symbolic / SMT reasoning over barrier traces to prune equivalent crash states (successors to eXplode).
- Validating `fsync` honesty on real SSDs and cloud block stores (power-cut rigs); Vijay Chidambaram's group (UT Austin) and the Jepsen project remain active.

## 8. Future Work

- A standard, *validated* persistence-model abstraction layer reusable across engines.
- Provable coverage metrics: a criterion such that "covered" implies absence of a defined bug class.
- Continuous crash-consistency in CI at full-workload scale, not just bounded micro-workloads.
- Bridging tested engines and verified engines: certify the hot path, test the rest.

## 9. Key References

- **[Foundational]** T. S. Pillai et al. *All File Systems Are Not Created Equal: On the Complexity of Crafting Crash-Consistent Applications (ALICE).* OSDI, 2014.
- **[SOTA]** J. Mohan, A. Martinez, S. Ponnapalli, P. Raju, V. Chidambaram. *Finding Crash-Consistency Bugs with Bounded Black-Box Crash Testing (ACE/CrashMonkey).* OSDI, 2018.
- **[Foundational]** H. Chen, D. Ziegler, T. Chajed, A. Chlipala, M. F. Kaashoek, N. Zeldovich. *Using Crash Hoare Logic for Certifying the FSCQ File System.* SOSP, 2015.
- **[Foundational]** J. Yang, P. Twohey, D. Engler, M. Musuvathi. *Using Model Checking to Find Serious File System Errors (FiSC/eXplode).* OSDI, 2004/2006.
- **[SOTA]** K. Kingsbury. *Jepsen* analyses (ongoing). jepsen.io.

---
*Part of the [DBMS Research catalog](../../README.md).*
