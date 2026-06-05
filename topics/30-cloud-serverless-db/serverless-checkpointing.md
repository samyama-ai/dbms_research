# Stateful serverless query checkpointing

> **Topic:** Cloud & Serverless Databases · **ID:** `30-cloud-serverless-db/serverless-checkpointing` · **Status:** empirically-open

## 1. Problem Statement
Running long analytical queries on **serverless/ephemeral compute** (FaaS functions with hard wall-clock timeouts, or spot/preemptible VMs subject to reclamation) means a worker can vanish mid-query. To survive this without restarting from scratch, the engine must **checkpoint** the in-flight query state cheaply and frequently, and **restore** it on a fresh function. The problem: **design checkpoint/restore for long-running query operators that is cheap and frequent enough to bound lost work, yet does not dominate query runtime or storage cost.**

- **Decision variant:** Given a function timeout $T$, reclamation hazard rate, and a per-checkpoint cost $c$, does a checkpoint schedule exist that completes the query within a cost/time budget in expectation?
- **Optimization variant:** Choose checkpoint interval(s) to minimize expected total time (or cost) = useful work + checkpoint overhead + expected re-execution after failures.
- **Counting variant:** Bound the state size that must be persisted per operator (the "checkpoint footprint").

## 2. Mathematical Foundations
The optimal checkpoint interval is the classic **Young–Daly formula** from HPC: with checkpoint cost $C$ and mean time between failures (here, expected time to timeout/reclamation) $M$, the optimal interval is
$$
\tau^\* \approx \sqrt{2\,C\,M},
$$
minimizing the expected wasted time (checkpoint overhead + lost work on failure). For frequent, bounded-loss serverless settings $M$ is *known and short* (the function timeout $T$), unlike HPC where failures are rare and random — this shifts the regime: checkpoints must be very cheap because they are taken many times within one query.

The state to persist is the **operator's intermediate state**: hash tables (build side of joins), sort runs, aggregation accumulators, and the **scan cursor / pipeline position**. For *deterministic, partitionable* operators, restore is cheap because re-deriving lost partitions is possible; the theory connects to **lineage-based recovery** (Spark RDD lineage, NSDI 2012) — recompute lost partitions from inputs instead of persisting state, trading recompute cost vs. checkpoint cost. The decision of *which* operators to materialize vs. recompute is a **min-cost recovery cut** on the dataflow DAG, analogous to selective checkpointing in autodiff (the optimal-rematerialization / "checkmate" LP).

Reclamation timing is often **adversarial-ish** (spot interruption with ~2-min notice) or modeled as a hazard process; worst-case analysis uses **online/competitive** framing: an algorithm that checkpoints on the 2-minute warning plus periodic insurance checkpoints.

## 3. State of the Art (SOTA)
**Systems-SOTA.** **Starling** (SIGMOD 2020) runs a query engine on AWS Lambda using S3 as the exchange/shuffle medium. **Lambada** (SIGMOD 2020, ETH) shows serverless analytics with serverless shuffle. **Pixels-Turbo / cloud-native query engines**, and spot-instance analytics like **Spark on spot with RDD lineage recovery** and **Flink** incremental/aligned-checkpointing (Chandy–Lamport-based) are the production reference points. **Boxer / Pocket** (OSDI 2018) provide elastic ephemeral storage for serverless intermediate state. **Photon/Velox/DuckDB**-style vectorized engines are being adapted to checkpoint pipeline state.

**Theory-SOTA.** Young–Daly optimal checkpointing; Chandy–Lamport consistent global snapshots (1985) for distributed dataflow; lineage-based recovery (RDDs). Optimal rematerialization (Checkmate, MLSys 2020) for the recompute-vs-store cut.

## 4. Upper Bound
With known timeout $M=T$ and checkpoint cost $C$, the Young–Daly interval $\tau^\*=\sqrt{2CT}$ yields expected overhead $\approx \sqrt{2C/T}$ fraction of runtime — provably near-optimal for the periodic-checkpoint model. Lineage/recompute recovery upper-bounds restore cost by the cost of re-running the lineage of lost partitions, which for narrow dependencies is local. Chandy–Lamport gives a consistent snapshot in one message-marker pass, $O(|E|)$ messages.

## 5. Lower Bound
There is an **information-theoretic floor**: to resume a stateful operator you must persist enough bits to reconstruct its state, so checkpoint size is lower-bounded by the (incompressible) intermediate-state entropy — for a full hash join build side, that is $\Omega(\text{build-side size})$ unless you recompute. Consistent distributed snapshots inherit **FLP**-style limits under asynchrony for *coordinated* checkpoints. There is **no closed-form optimum** for the *combined* problem of (a) which operators to checkpoint vs. recompute, (b) under adversarial spot-reclamation timing, (c) with separate cloud prices for ephemeral storage vs. recompute — this combination is what keeps the problem **empirically open**; the recompute-vs-store cut generalizes NP-hard graph-partition flavored problems.

## 6. The Gap
For a *single* operator with known timeout, Young–Daly essentially closes the interval-selection problem. The open, **empirical** gap is the *system-level* policy: real queries are DAGs of heterogeneous operators with very different state sizes and recompute costs, reclamation is partly adversarial, and ephemeral-storage vs. recompute carry different prices — there is no policy with proven competitive/optimality guarantees over this joint space, and no standard benchmark quantifying checkpoint overhead vs. survival probability for production analytical queries. Closing it needs both empirical characterization and a competitive analysis of the per-operator store-vs-recompute cut under adversarial reclamation.

## 7. Current Research (as of June 2026)
- Incremental and asynchronous checkpointing of vectorized pipeline state (DuckDB/Velox on serverless). *(frontier — verify)*
- Lineage-aware selective checkpointing that recomputes cheap operators and persists only expensive state, ported from the autodiff rematerialization literature. *(frontier — verify)*
- Spot-reclamation-aware schedulers that checkpoint on the interruption notice plus light periodic insurance.
- Groups: Starling/Lambada authors (CMU, ETH Systems Group), serverless-analytics at Berkeley Sky, Flink/Chandy–Lamport snapshotting community.

## 8. Future Work
- A competitive theory for per-operator checkpoint-vs-recompute under adversarial preemption.
- Standardized benchmarks for checkpoint overhead vs. survival probability on TPC-H/TPC-DS at serverless scale.
- Hardware-assisted fast snapshots (CXL/persistent memory) to drive checkpoint cost $C\to 0$.

## 9. Key References
- **[Foundational]** Daly, J. *A Higher Order Estimate of the Optimum Checkpoint Interval for Restart Dumps.* Future Generation Computer Systems, 2006. (Young–Daly formula.)
- **[Foundational]** Chandy, K.M., Lamport, L. *Distributed Snapshots: Determining Global States of Distributed Systems.* ACM TOCS, 1985.
- **[Foundational]** Zaharia, M. et al. *Resilient Distributed Datasets: A Fault-Tolerant Abstraction for In-Memory Cluster Computing.* NSDI, 2012.
- **[SOTA]** Perron, M., Fernandez, R.C., DeWitt, D., Madden, S. *Starling: A Scalable Query Engine on Cloud Functions.* SIGMOD, 2020.
- **[SOTA]** Müller, I., Marroquín, R., Alonso, G. *Lambada: Interactive Data Analytics on Cold Data Using Serverless Cloud Infrastructure.* SIGMOD, 2020.

---
*Part of the [DBMS Research catalog](../../README.md).*
