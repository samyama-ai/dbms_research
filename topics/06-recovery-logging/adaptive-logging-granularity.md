# Adaptive logging granularity

> **Topic:** Recovery, Logging & Durability · **ID:** `06-recovery-logging/adaptive-logging-granularity` · **Status:** empirically-open

## 1. Problem Statement

A WAL can record an update at different **granularities**:

- **Physical / page logging** — before/after images of whole pages (or byte ranges); large but trivially idempotent and replay-cheap.
- **Physiological / row (tuple) logging** — logical-within-a-page record of the changed tuple (ARIES); the standard middle ground.
- **Logical / command logging** — record only the *operation/statement* (e.g., the stored procedure and its arguments); tiny to write but expensive to recover (must re-execute deterministically).

These trade **log write volume** (and thus commit-path bandwidth/latency) against **recovery cost** (replay work) and **applicability** (command logging needs determinism). The problem: **dynamically choose, per operation / per transaction / per workload phase, the granularity that minimizes total log volume** (and a recovery-time budget), switching as the workload changes.

Variants: (a) *decision* — given a recovery-time SLO, is there a per-operation granularity assignment under log-volume budget $B$? (b) *optimization* — minimize expected log bytes subject to a recovery-time bound (or minimize a weighted sum of write volume + recovery time); (c) *online* — choose granularity without knowing future updates.

## 2. Mathematical Foundations

For an update $u$ touching $\delta$ bytes within a page of size $P$, log costs are roughly: physical $\approx P$ (or the dirtied range); row $\approx \delta + h$ (header/overhead $h$); command $\approx |\text{op-encoding}|$, often $\ll \delta$ but **amortized over all rows the command touches**. So a single statement updating $m$ rows costs $\approx m(\delta+h)$ under row logging but $\approx |\text{op}|$ under command logging — command logging wins exactly when **per-statement fan-out $m$ is large** and re-execution is deterministic and cheap relative to replaying $m$ records.

Recovery cost inverts this: physical/row replay is $O(\\#\text{records})$ idempotent applies; command replay re-runs the operation, costing its original CPU time, and demands **deterministic re-execution** (no nondeterministic reads, controlled ordering). Formalize per-operation choice $g(u)\in\{\text{phys,row,cmd}\}$ minimizing $\sum_u \text{write}(u,g) $ subject to $\sum_u \text{replay}(u,g) \le T$. This is a **knapsack-like / Lagrangian** assignment; the online form is a **ski-rental-style** decision (pay small-write-now vs. risk-large-replay-later) and, under switching costs between modes, a **metrical task system**. Determinism is a hard constraint: command logging is only *valid* for operations in a deterministic class $\mathcal{D}$.

## 3. State of the Art (SOTA)

- **Foundational:** **ARIES** (Mohan et al., 1992) standardizes physiological (row-level) logging. **Command/transaction logging** is classic in main-memory systems (e.g., **VoltDB/H-Store** use command logging for determinism-friendly stored procedures).
- **Systems-SOTA:** The defining study is **"Rethinking Main Memory OLTP Recovery"** (Malviya, Weisberg, Madden, Stonebraker, ICDE 2014), which directly compares command (logical) vs. ARIES-style (physical) logging for in-memory databases and quantifies the write-volume / recovery-time trade-off — motivating *adaptivity*. **SiloR** (Zheng et al., OSDI 2014) does parallel value logging + checkpointing. Engines mix modes statically (InnoDB physiological redo + logical-ish undo; SQL Server minimal/bulk logging modes). **Adaptive/hybrid logging** has been proposed (e.g., per-transaction choice between command and physical logging based on cost estimates) but is workload-tuned, not provably optimal.

## 4. Upper Bound

Best constructive results are hybrid policies: choosing **command logging for high-fan-out deterministic statements** and **row logging otherwise** provably reduces log volume versus either pure scheme on mixed workloads, with the savings bounded by the fan-out distribution. A per-transaction cost-model switch (estimate write-bytes and replay-time for each mode, pick the Lagrangian-best) achieves **min(per-mode) cost up to estimation error**, and online ski-rental-style switching is **2-competitive** for the single binary phys-vs-command decision under switching cost (deterministic) — a clean upper bound for the simplest variant.

## 5. Lower Bound

- **Information-theoretic write floor:** to recover via *idempotent replay* (no re-execution), the log must encode the actual changed bytes — $\Omega(\sum \delta)$ bits for the net dirtied data (you cannot redo data you never recorded). Command logging beats this only by *spending recovery compute* to regenerate the bytes, shifting cost rather than removing it.
- **Online competitive lower bound:** the phys-vs-command switching decision under switching cost is a ski-rental/metrical-task problem; deterministic online is $\ge 2$-competitive, randomized $\ge e/(e-1)$.
- **Determinism barrier:** command logging is *infeasible* (not merely costly) for nondeterministic operations — a correctness lower bound on its applicability, not a quantitative one.
- No problem-specific NP-hardness or tight fine-grained bound for the full three-way, workload-parameterized assignment is established — hence "empirically-open."

## 6. The Gap

Empirically open. We know the trade-off qualitatively and have hybrid heuristics and clean bounds for the *binary* online sub-problem, but no tight theory for the **three-way, online, workload-adaptive** assignment under a joint write-volume + recovery-time + determinism model, nor a policy proven near-optimal across workload shifts. The gap is between borrowed ski-rental/knapsack bounds and the real multi-mode, switching-cost-bearing, determinism-constrained decision; closing it needs a model capturing all three granularities, mode-switch cost, and the recovery-compute-for-bytes exchange, with a matching competitive bound.

## 7. Current Research (as of June 2026)

Active directions: workload-aware and learned logging-mode selection in HTAP/in-memory engines *(frontier — verify)*; deterministic execution frameworks (Calvin lineage) that broaden the class $\mathcal{D}$ where command logging is valid; recovery-time-bounded logging for serverless/elastic databases where cold recovery dominates SLOs; differential/delta logging granularity on PM where the "page" granule shrinks to cache lines. Groups: MIT (Madden/Stonebraker lineage), CMU-DB, VoltDB/H-Store descendants, TUM (Neumann/Leis) on HTAP logging.

## 8. Future Work

- A unified three-way (page/row/command) cost model with provably near-optimal online switching under mode-change cost.
- Automatic determinism analysis to safely enlarge the command-logging-eligible operation class.
- Recovery-time-budgeted adaptive logging with worst-case guarantees, not just average-case tuning.
- Granularity adaptation for PM/CXL where atomic-write granule and replay cost differ from block storage.

## 9. Key References

- **[Foundational]** C. Mohan, Don Haderle, Bruce Lindsay, Hamid Pirahesh, Peter Schwarz. *ARIES: A Transaction Recovery Method...* ACM TODS, 1992. — [DOI](https://doi.org/10.1145/128765.128770)
- **[SOTA]** Nirmesh Malviya, Ariel Weisberg, Samuel Madden, Michael Stonebraker. *Rethinking Main Memory OLTP Recovery.* ICDE, 2014. — [IEEE](https://ieeexplore.ieee.org/document/6816685/)
- **[SOTA]** Wenting Zheng, Stephen Tu, Eddie Kohler, Barbara Liskov. *Fast Databases with Fast Durability and Recovery Through Multicore Parallelism (SiloR).* OSDI, 2014. — [DBLP](https://dblp.org/rec/conf/osdi/ZhengTKL14.html)
- **[Foundational]** Robert Kallman, Hideaki Kimura, Jonathan Natkins, et al. *H-Store: A High-Performance, Distributed Main Memory Transaction Processing System.* VLDB, 2008. — [DOI](https://doi.org/10.14778/1454159.1454211)
- **[Foundational]** Jim Gray, Andreas Reuter. *Transaction Processing: Concepts and Techniques.* Morgan Kaufmann, 1993. — [DBLP](https://dblp.org/rec/books/mk/GrayR93.html)

## 10. Worked Example

Consider a single statement `UPDATE accounts SET active=false WHERE region='EU'` that touches $m=10{,}000$ rows, each dirtying $\delta=8$ bytes within $P=8\,\text{KB}$ pages, with row-record overhead $h=40$ bytes.

- **Row (physiological) logging:** $\approx m(\delta+h) = 10{,}000 \times 48 = 480\,\text{KB}$ of log, but redo replays 10,000 cheap idempotent applies.
- **Command logging:** records only the statement text $\approx 60$ bytes — a $\mathbf{8000\times}$ write-volume reduction — but recovery must re-execute the full scan + 10,000 updates (its original CPU cost), and is valid only if execution is deterministic.

Now a point update `UPDATE accounts SET bal=bal-1 WHERE id=42` ($m=1$): row logging costs $48$ bytes; command logging costs $\approx 50$ bytes with re-execution overhead — no win. The adaptive rule: pick command logging when fan-out $m$ is large (here above $\sim |\text{op}|/(\delta+h)$), row logging otherwise. The high-fan-out statement saves $\sim 480\,\text{KB}$; the point update stays on row logging.

---
*Part of the [DBMS Research catalog](../../README.md).*
