---
id: 07-storage-buffer/writeback-scheduling
title: "Write-Back Scheduling to Minimize Stall and Wear"
topic: 07-storage-buffer
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Write-Back Scheduling to Minimize Stall and Wear

> **Topic:** Storage & Buffer Management · **ID:** `07-storage-buffer/writeback-scheduling` · **Status:** open

## 1. Problem Statement

A buffer pool accumulates *dirty* pages that must eventually be flushed to durable storage. A **write-back (checkpoint/cleaner) scheduler** decides *which* dirty pages to flush, *when*, and *in what order*. Two objectives conflict:

- **Foreground stall minimization:** if too few pages are cleaned, a transaction needing a free frame must wait for a synchronous flush (a *page-replacement stall*); recovery time also grows with the dirty-page horizon (oldest unflushed LSN).
- **Wear / write-amplification minimization on SSDs:** flushing the same logical page repeatedly, or in an order that defeats the device's internal log-structuring, inflates the *write amplification factor* (WAF), consuming finite NAND program/erase cycles and eroding endurance.

**Decision variant:** does a schedule exist that keeps stall probability $\le \epsilon$ while issuing $\le B$ physical writes over a horizon? **Optimization variant:** minimize a weighted sum $\alpha \cdot \mathbb{E}[\text{stall}] + \beta \cdot \text{WAF}$ subject to a recovery-time bound and a flush-bandwidth budget. **Online variant:** decisions made without knowing future writes/re-dirties. The tension is that *delaying* a flush coalesces repeated writes (reducing WAF) but raises stall and recovery risk; *eager* flushing does the opposite.

## 2. Mathematical Foundations

Model time as a sequence of page accesses; each write marks a page dirty with a *recency* and *re-dirty rate* $\lambda_p$. A flush of page $p$ at time $t$ incurs one physical write but is "wasted" if $p$ is re-dirtied before eviction. Expected wasted writes relate to the *inter-write time distribution*: flushing is worthwhile when the residual time to eviction is short relative to $1/\lambda_p$ — an instance of the classic **ski-rental / rent-or-buy** tradeoff per page. Stall is governed by a queueing model: free-frame depletion is a birth-death process with arrival rate = page-miss rate and service rate = clean-frame production; the scheduler must keep the clean-frame buffer above a safety stock (an $(s,S)$ inventory policy). Recovery time is bounded by the *fuzzy-checkpoint* invariant: the redo scan length $\propto$ (current LSN − min dirty-page recLSN). SSD wear adds a constraint that physical writes should be *aligned and sequential* to minimize the device's internal copy-forward; this links to the **erase-block packing** problem (bin-packing of dirty pages into flush groups). Submodularity of coalescing benefit supports greedy batching.

## 3. State of the Art (SOTA)

**Systems-SOTA:** PostgreSQL's background writer + checkpointer with `checkpoint_completion_target` spreading; InnoDB's adaptive flushing driven by redo-log fill and dirty-page-ratio with an LRU-tail cleaner; the **WiredTiger** and **LeanStore** (CIDR'18, "in-memory performance for big data") cleaners; **Umbra** (CIDR'20) variable-size pages. SSD-aware DB write shaping appears in research prototypes and in FlashStore/SILT lineage. **Theory-SOTA:** the write-back ordering problem is studied as *flush scheduling* and connects to *online buffer management* and *energy/wear-aware scheduling*; no single canonical optimal online algorithm dominates. Ski-rental and its randomized $e/(e-1)$ refinement underpin per-page flush timing.

## 4. Upper Bound

For the **per-page flush-timing** subproblem framed as rent-or-buy, the deterministic 2-competitive and randomized $\tfrac{e}{e-1}\approx 1.58$-competitive ski-rental algorithms give the best-known online guarantees. For **clean-frame provisioning** as an $(s,S)$/newsvendor problem, the optimal safety stock has a closed form given the miss-rate distribution; online, a $O(\log(\text{ratio}))$-competitive guarantee follows from generalized inventory results. End-to-end joint $\alpha$-stall + $\beta$-WAF scheduling has only heuristic upper bounds (adaptive flushing controllers); there is no published constant-competitive algorithm for the full multi-objective online problem.

## 5. Lower Bound

Ski-rental's deterministic lower bound of $2$ and randomized $e/(e-1)$ are tight, so per-page timing cannot be improved online. For the joint problem, an adversary that alternates re-dirty bursts with sudden read floods forces any online scheduler to either over-flush (paying WAF) or stall, yielding a constant-factor lower bound strictly above $1$; the exact constant for the two-objective version is **open**. Recovery-time bounds impose a hard information-theoretic floor: to bound redo to $R$ bytes you must flush at rate ≥ log-generation rate, independent of cleverness. No NP-hardness is needed for the online core; the *offline* multi-constraint version (minimize WAF subject to stall and recovery bounds with batching) is NP-hard by reduction from bin-packing (erase-block packing of dirty pages).

## 6. The Gap

The decomposed pieces (ski-rental timing, $(s,S)$ provisioning) are tight, but the **coupled online objective** — jointly minimizing stall and SSD wear under a recovery constraint — has no matching upper/lower bound. Practice ships PID-style adaptive controllers (InnoDB, PostgreSQL) with no competitive guarantee, and their WAF behavior on modern SSDs is largely empirical. The gap is genuinely open: we lack both a tight competitive algorithm and a proof that constant-competitiveness is unattainable when WAF and stall are weighted adversarially.

## 7. Current Research (as of June 2026)

- **SSD-WAF-aware cleaners** that group dirty pages into device-aligned flush units and exploit FTL hints / NVMe ZNS (zoned namespaces) to control internal write amplification *(frontier — verify)*.
- **Learned flush controllers** replacing PID heuristics with RL/predictive models of re-dirty rates (LeanStore/Umbra lineage at TU Munich; CMU DB group's self-driving systems) *(frontier — verify)*.
- **CXL/persistent-memory** changes the cost model (byte-addressable durability shifts where the stall vs. wear tradeoff lives).
- Recovery-bounded checkpoint scheduling formalized with competitive analysis.

## 8. Future Work

- A provable multi-objective competitive algorithm for stall + WAF + recovery.
- Tail-latency (p99) flush scheduling, since checkpoint spikes dominate stalls.
- Co-design with ZNS / open-channel SSDs to make WAF a controllable rather than emergent quantity.
- Endurance-budget-aware policies that ration lifetime writes across a device's service life.

## 9. Key References

- **[Foundational]** Jim Gray, Andreas Reuter. *Transaction Processing: Concepts and Techniques.* Morgan Kaufmann, 1992. (Checkpointing, buffer management.) — [ACM](https://dl.acm.org/doi/10.5555/573304)
- **[Foundational]** C. Mohan, Don Haderle, Bruce Lindsay, Hamid Pirahesh, Peter Schwarz. *ARIES: A Transaction Recovery Method Supporting Fine-Granularity Locking and Partial Rollbacks Using Write-Ahead Logging.* ACM TODS, 1992. — [DOI](https://doi.org/10.1145/128765.128770)
- **[SOTA]** Viktor Leis, Michael Haubenschild, Alfons Kemper, Thomas Neumann. *LeanStore: In-Memory Data Management Beyond Main Memory.* ICDE, 2018. — [DBLP](https://dblp.org/rec/conf/icde/LeisHK018.html)
- **[Foundational]** Anna Karlin, Mark Manasse, Larry Rudolph, Daniel Sleator. *Competitive Snoopy Caching.* Algorithmica, 1988. (Rent-or-buy / ski-rental.) — [DOI](https://doi.org/10.1007/BF01762111)
- **[SOTA]** Matias Bjørling, et al. *ZNS: Avoiding the Block Interface Tax for Flash-based SSDs.* USENIX ATC, 2021. — [USENIX](https://www.usenix.org/conference/atc21/presentation/bjorling)
- **[Survey]** Goetz Graefe. *A Survey of B-Tree Logging and Recovery Techniques.* ACM TODS, 2012. — [DOI](https://doi.org/10.1145/2109196.2109197)

## 10. Worked Example

**Per-page flush as ski-rental.** A dirty page $p$ is re-dirtied on average every $1/\lambda_p$ time units. *Flushing now* costs 1 physical write but is wasted if $p$ is re-dirtied before eviction (write amplification); *waiting* risks a synchronous stall if a free frame is needed. This is rent-or-buy: "rent" = keep deferring (risk stall later), "buy" = flush now (pay a write that may be wasted).

Concretely, suppose flushing costs $B=1$ unit and each time step deferred risks a re-dirty (wasting the eventual flush). The deterministic break-even rule "flush once the page has been clean-eligible for $B$ steps" is **2-competitive**: $\text{ALG} \le 2\cdot\text{OPT}$. Randomizing the threshold over $[0,B]$ with density $\propto e^{t/B}$ improves this to $\frac{e}{e-1}\approx 1.58$.

**Numbers.** With re-dirty rate $\lambda=0.1$/step and eviction expected in $5$ steps, residual-to-eviction $5 < 1/\lambda = 10$, so flushing is worthwhile (the page likely won't be re-dirtied first). If instead eviction is $20$ steps away ($> 10$), deferring coalesces an expected $\approx 2$ writes into one — halving WAF on that page.

---
*Part of the [DBMS Research catalog](../../README.md).*