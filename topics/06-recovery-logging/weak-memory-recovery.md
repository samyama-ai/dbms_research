# Recovery correctness under weak memory

> **Topic:** Recovery, Logging & Durability · **ID:** `06-recovery-logging/weak-memory-recovery` · **Status:** open

## 1. Problem Statement
Classical recovery proofs (write-ahead logging, ARIES) assume a *sequentially consistent* store and a clean separation between "volatile" and "stable" memory: a write either reaches durable media or it does not, and the order in which durable writes land matches program order. Modern hardware violates both assumptions. With persistent memory (Intel Optane-class DIMMs, CXL-attached memory) and aggressive store buffers, a store becomes *visible* to other cores at a different time than it becomes *persistent*, and persistence order may be reordered relative to program order unless explicit barriers (`CLWB` + `SFENCE`, `eADR`, epoch fences) are issued. The problem is to **specify durability/recovery protocols and prove their crash-consistency against realistic weak persistency and weak memory-consistency models**, rather than against an idealized sequentially consistent durable store.

Variants:
- **Verification (decision):** given a protocol $P$, a persistency model $\mathcal{M}$, and a crash-consistency specification $\phi$, decide whether every execution of $P$ under $\mathcal{M}$ that crashes and recovers satisfies $\phi$.
- **Synthesis:** insert a *minimum* set of persist barriers/flushes so that $P$ becomes crash-consistent under $\mathcal{M}$ (an optimization variant — minimize the fence/flush count on the commit path).
- **Counting/robustness:** characterize which programs are *persistency-robust* (behave under $\mathcal{M}$ as under a sequentially consistent durable store).

## 2. Mathematical Foundations
The semantic substrate is **axiomatic (declarative) memory models**: an execution is a set of events with relations *program order* ($\mathit{po}$), *reads-from* ($\mathit{rf}$), *coherence* ($\mathit{co}$), and a derived *happens-before*; consistency = acyclicity of certain composed relations. Persistency extends this with a **non-volatile-order (NVO)** relation and a *persist* event per durable store; the recovery observer sees a downward-closed prefix of NVO. Px86 (Raad, Wickerson, Neis, Vafeiadis, POPL 2020) and the **PArm/PTSO** family give the canonical operational + declarative semantics; **Persistency models** were introduced by Pelley, Chen & Wenisch (ISCA 2014) as *strict*, *epoch*, and *buffered epoch* persistency.

Crash consistency is then a hyperproperty over the lattice of reachable *persistent states*. A protocol is correct iff for every prefix $S$ of NVO reachable at a crash, the recovery function $R(S)$ yields a state in the protocol's linearization. Proof techniques import **separation logic** extended with persistence (e.g. POG/Pierogi-style logics, **Persistent Owicki-Gries**) and **stateless model checking under weak persistency** (extending DPOR). Decidability mirrors that of weak-memory reachability: undecidable in general for unbounded executions under relaxed models, PSPACE/NP-hard for bounded instances.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Px86 (POPL 2020) and its Arm counterpart give sound, mechanized persistency semantics; **persistent separation logics** (e.g. Vindum & Birkedal-style, and Raad et al.'s logics) prove individual data structures correct. **PerSeVerE / Persistency-aware stateless model checking** (Kokologiannakis, Raad, Vafeiadis, OOPSLA 2021) automatically verifies bounded persistent programs.
- **Systems-SOTA:** crash-consistency testing tools — **Yat**, **PMTest**, **XFDetector**, **Jaaru** (model-checking-based), and **Agamotto** — find missing-flush/ordering bugs in real PMEM code (RocksDB-pmem, PMDK, Redis-pmem). These are bug-finders, not full proofs.

## 4. Upper Bound
For *bounded* programs under Px86/epoch persistency, persistency-aware DPOR (PerSeVerE, Jaaru) gives a **sound and complete** decision procedure; cost is exponential in the number of concurrent persist events but optimal up to the inherent state-space (no redundant exploration of equivalent persist interleavings). Logic-based proofs (persistent separation logic) give *unbounded* correctness but require manual/semi-automated effort. Minimal-fence synthesis is solved exactly only for small kernels via constraint solving.

## 5. Lower Bound
Reachability under relaxed memory is **undecidable** for unbounded executions under TSO-with-persistency and stronger relaxations (reduction from lossy/Post correspondence-style constructions in the weak-memory literature). Even single-crash bounded verification is **NP-hard** (encodes acyclicity-of-relations / SAT). Minimal persist-barrier insertion is NP-hard by reduction from minimum fence insertion (Bouajjani, Derevenetc, Meyer-style results). These are complexity lower bounds; there is no matching *impossibility* of correct protocols — correct protocols exist, they are just expensive to verify.

## 6. The Gap
The gap is between (a) push-button verification that is *sound and complete but only bounded* and (b) *unbounded* proofs that need human-guided separation logic. No tool today gives unbounded, automatic, model-parametric ("verify against any of {strict, epoch, buffered, eADR}") crash-consistency proofs for full-scale storage engines. Closing it needs either decidable fragments capturing real WAL/redo protocols, or compositional proof rules that reduce engine-scale verification to per-record obligations. The problem is genuinely **open**: even the *right specification* of durability under buffered persistency is contested.

## 7. Current Research (as of June 2026)
- Extending persistency semantics and verification from x86 to **CXL memory pooling and disaggregated persistence**, where the persistence domain spans a fabric *(frontier — verify)*.
- **eADR / "whole-system persistence"** hardware shifts the model: flushes become no-ops but fences/ordering still matter; re-proving protocols under eADR is active (Vafeiadis/MPI-SWS, Wenisch/Michigan lineage) *(frontier — verify)*.
- Persistency-aware model checking scaling to KV-store-sized code via symmetry/commutativity reductions (Kokologiannakis, Raad) *(frontier — verify)*.
- Formal connection between **durable linearizability** (Izraelevitz, Mendes, Scott, DISC 2016) and engine-level recovery specs.

## 8. Future Work
- Decidable fragments of persistent WAL protocols; a "persistency-robustness" checker analogous to TSO-robustness.
- Compositional crash-consistency logics that compose across the buffer pool / log / checkpoint subsystems.
- Verified reference implementations of ARIES-style recovery under epoch and buffered-epoch persistency.
- Synthesis of minimum-cost persist barriers with end-to-end correctness certificates.

## 9. Key References
- **[Foundational]** Pelley, S., Chen, P. M. & Wenisch, T. F. *Memory Persistency.* ISCA, 2014.
- **[Foundational]** Izraelevitz, J., Mendes, H. & Scott, M. L. *Linearizability of Persistent Memory Objects under a Full-System-Crash Failure Model (durable linearizability).* DISC, 2016.
- **[SOTA]** Raad, A., Wickerson, J., Neiger, G. & Vafeiadis, V. *Persistency Semantics of the Intel-x86 Architecture (Px86).* POPL, 2020.
- **[SOTA]** Kokologiannakis, M., Raad, A. & Vafeiadis, V. *Model Checking for Weakly Consistent Persistent Memory (PerSeVerE).* OOPSLA, 2021.
- **[SOTA]** Gorjiara, H., Xu, G. H. & Demsky, B. *Jaaru: Efficiently Model Checking Persistent Memory Programs.* ASPLOS, 2021.
- **[Survey]** Alglave, J., Maranget, L. & Tautschnig, M. *Herding Cats: Modelling, Simulation, Testing, and Data Mining for Weak Memory.* ACM TOPLAS, 2014.

---
*Part of the [DBMS Research catalog](../../README.md).*
