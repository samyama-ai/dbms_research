# Semantic load shedding with answer guarantees

> **Topic:** Streaming & Continuous Queries · **ID:** `18-streaming-queries/semantic-load-shedding-guarantees` · **Status:** open

## 1. Problem Statement

A continuous query system processing one or more high-rate streams may transiently receive tuples faster than it can process them. *Load shedding* drops a subset of input (or intermediate) tuples to keep latency bounded under finite CPU/memory. *Semantic* (as opposed to random) load shedding chooses **which** tuples to drop based on their predicted contribution to query answers, so as to minimize the error introduced.

The core problem: given a query $Q$ (typically windowed aggregates, or sliding-window joins), an instantaneous overload factor (arrival rate $\lambda$ exceeding service rate $\mu$ by a deficit $\delta = \lambda - \mu$), and an error metric $\mathcal{E}$ (relative error, $L_p$ distance on the answer vector, or per-group error), choose a dropping policy that **guarantees** $\mathcal{E} \le \epsilon$ while shedding enough load to restore stability.

Variants:
- **Optimization:** minimize expected/worst-case answer error subject to a throughput (drop-rate) constraint.
- **Decision / feasibility:** does a shedding plan exist meeting both an error bound $\epsilon$ and a load-deficit $\delta$?
- **Online / adversarial:** the bound must hold without knowing future arrivals, against an oblivious or adaptive input.

The open challenge is *provable* a-posteriori or a-priori guarantees (deterministic or $(\epsilon,\delta)$-probabilistic) for **joins** and **correlated multi-stream** queries, not just single-stream aggregates.

## 2. Mathematical Foundations

Model a stream as a sequence of tuples $t_1, t_2, \dots$ with arrival times. A windowed aggregate query partitions tuples into groups $g$ and computes $A_g = f(\{v : t \in g\})$. A *drop operator* with retention probability $p_t \in [0,1]$ (or 0/1 deterministic gate) is inserted; the estimator typically rescales surviving values by $1/p_t$ (Horvitz–Thompson):
$$\hat{A}_g = \sum_{t \in g} \frac{X_t\, v_t}{p_t}, \quad X_t \sim \mathrm{Bernoulli}(p_t),$$
which is unbiased with variance $\mathrm{Var}(\hat{A}_g) = \sum_t v_t^2 (1-p_t)/p_t$. Allocating a fixed drop budget across groups to minimize aggregate variance is a **convex resource-allocation** problem; optimal $p_t \propto v_t$ within a group (a form of priority/IPPS sampling).

For **joins**, the difficulty is that one input tuple may produce many output tuples; dropping it removes a join-partner-dependent number of results. Bounding output error reduces to estimating join sizes — connecting to the **AGM bound** for worst-case join output and to **random sampling over joins** (which is provably hard to do unbiasedly without index structures). For sliding-window joins, MASSA/age-based models predict the future productivity of a tuple from its remaining lifetime in the window.

Concentration (Hoeffding/Bernstein) converts per-tuple variance into $(\epsilon,\delta)$ tail bounds; deterministic guarantees instead require *coverage*-style combinatorial arguments.

## 3. State of the Art (SOTA)

- **Aurora / Borealis** (Tatbul, Çetintemel, Zdonik; VLDB 2003, 2007): introduced operator-level load shedding via "drop boxes," QoS utility functions, and the *load-shedding road map* (LSRM). Pioneered semantic vs. random drops but offered heuristic, not provable, error bounds.
- **STREAM / CQL** (Babcock, Datar, Motwani; 2004): load shedding for sliding-window aggregates with statistically motivated drop placement minimizing relative-error variance — the cleanest *theory-adjacent* result.
- **Loadstar** (Chi, Yu; 2005): feature-based, quality-aware shedding for classification queries.
- **Systems SOTA:** modern engines (Flink, Spark Structured Streaming, Timely/Differential Dataflow) largely favor **backpressure** over lossy shedding; semantic shedding survives mainly in approximate-query and sensor/IoT settings.
- **Theory SOTA:** unbiased *sampling over joins* (Chaudhuri–Motwani–Narasayya 1999; Zhao et al. 2018 "random sampling over joins revisited") underpins join-aware shedding error analysis.

## 4. Upper Bound

For **single-stream windowed sum/count/avg**, priority/probabilistic dropping with HT rescaling achieves *unbiased* answers with relative error $O(1/\sqrt{n_{\text{kept}}})$ w.h.p.; to shed a fraction $\rho$ of load while guaranteeing relative error $\epsilon$ on a group with $n_g$ tuples, one needs $n_g \gtrsim 1/\epsilon^2$ surviving samples — Babcock–Datar–Motwani give the matching budget-allocation policy minimizing maximum group error (model: i.i.d./quasi-stationary stream, additive value model).

For **sliding-window joins**, no algorithm is known that guarantees a relative-error bound on output size under arbitrary load deficit; best results are heuristic (age/MASSA) with empirical error.

## 5. Lower Bound

- **Join sampling hardness:** producing an unbiased uniform sample of join output without auxiliary indexes requires reading essentially the full input in the worst case (related to the difficulty of join-size estimation); communication-complexity lower bounds for set-intersection size imply that estimating a two-stream equi-join's answer to relative error $\epsilon$ from a $\rho$-shed stream needs $\Omega(\epsilon^{-2})$ retained tuples, and worse for skewed key distributions.
- **Adversarial impossibility:** for *correlated* drops on multi-stream queries an oblivious adversary can force $\Omega(1)$ relative error at any fixed drop rate $\rho > 0$ — no deterministic guarantee is possible without distributional assumptions (a folklore overload-vs-accuracy tradeoff).
- General space lower bounds for windowed approximation (Datar–Gionis–Indyk–Motwani exponential histograms) lower-bound the state a *guaranteed* shedder must retain.

## 6. The Gap

For single-stream aggregates the gap is essentially **closed**: optimal variance-minimizing allocation matches the $\Theta(\epsilon^{-2})$ sampling lower bound. For **joins and multi-stream correlated queries the gap is wide and genuinely open**: upper bounds are heuristic with empirical-only error, while lower bounds rule out distribution-free deterministic guarantees. Closing it requires either (a) restricted-input models (bounded skew, known join multiplicity) admitting provable $(\epsilon,\delta)$ shedders, or (b) auxiliary online indices/sketches cheap enough to maintain under the very overload that triggered shedding.

## 7. Current Research (as of June 2026)

- Renewed interest in **approximate streaming under SLOs**: combining load shedding with online sketches (CountSketch/AMS) so that dropped tuples are still summarized, giving guarantees on aggregates even at high drop rates *(frontier — verify)*.
- **Learned shedding policies** (RL/learned cost models) that predict tuple utility for joins; the open question is wrapping learned predictors in *certified* error bounds rather than empirical loss.
- Integration with **provenance/lineage** to compute a-posteriori error intervals on shed answers *(frontier — verify)*.
- Groups historically active: Brown/Zdonik lineage, MIT (Madden), Stanford STREAM alumni; recent work appears at VLDB/SIGMOD approximate-query-processing tracks.

## 8. Future Work

- Provable $(\epsilon,\delta)$ load shedding for sliding-window equi-joins under bounded-skew models.
- Unified shedding + sketching so no dropped tuple is "lost," only summarized, with composable error.
- Worst-case-optimal-join-aware shedding leveraging AGM-style multiplicity estimates online.
- Tail-latency-aware shedding with formal latency *and* accuracy guarantees simultaneously (dual SLO).
- Certified learned shedders: conformal-prediction-style guarantees around learned utility models.

## 9. Key References

- **[Foundational]** Tatbul, Çetintemel, Zdonik, Cherniack, Stonebraker. *Load Shedding in a Data Stream Manager.* VLDB, 2003. — [DBLP](https://dblp.org/rec/conf/vldb/TatbulCZCS03.html)
- **[Foundational]** Babcock, Datar, Motwani. *Load Shedding for Aggregation Queries over Data Streams.* ICDE, 2004. — [DBLP](https://dblp.uni-trier.de/rec/conf/icde/BabcockDM04.xml)
- **[SOTA]** Tatbul, Zdonik. *Window-aware Load Shedding for Aggregation Queries over Data Streams.* VLDB, 2006. — [PDF](https://people.csail.mit.edu/tatbul/publications/vldb06.pdf)
- **[SOTA]** Zhao, Christensen, Li, Hu, Yi. *Random Sampling over Joins Revisited.* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3183739)
- **[Foundational]** Atallah, Grama et al. / Datar, Gionis, Indyk, Motwani. *Maintaining Stream Statistics over Sliding Windows.* SODA / SIAM J. Comput., 2002. — [DOI](https://doi.org/10.1137/S0097539701398363)
- **[Survey]** Cormode, Garofalakis, Haas, Jermaine. *Synopses for Massive Data: Samples, Histograms, Wavelets, Sketches.* Foundations and Trends in Databases, 2012. — [DOI](https://doi.org/10.1561/1900000004)

## 10. Worked Example

**Single-stream aggregate (provable).** A window holds $n_g = 10{,}000$ sensor readings; we must shed $\rho = 90\%$ of load, keeping $\approx 1000$. Random drop with Horvitz–Thompson rescaling ($\hat A_g = \sum X_t v_t / p_t$, $p_t = 0.1$) is unbiased. For a relative-error target $\epsilon = 0.05$ on the sum, the sampling lower bound needs $n_{\text{kept}} \gtrsim 1/\epsilon^2 = 400$ surviving tuples — and $1000 > 400$, so the guarantee holds: $|\hat A_g - A_g|/A_g \le 0.05$ w.h.p. This is the *closed* case, with Babcock–Datar–Motwani's variance-minimizing allocation matching $\Theta(\epsilon^{-2})$.

**Two-stream join (open).** Now query $R \bowtie_{\text{key}} S$ over windows of $N = 10{,}000$ each. Suppose one *heavy* key $k^\star$ appears in $100$ tuples of $R$ and $100$ of $S$, producing $100 \times 100 = 10{,}000$ output tuples — half the join. If shedding randomly drops $90\%$ of $R$, it keeps $\approx 10$ of the $k^\star$ tuples, so $\hat{}$ output for $k^\star$ falls to $\approx 10 \times 100 = 1000$; rescaling by $1/p^2$ (two dropped sides) inflates variance enormously. An oblivious adversary can place all mass on such a skewed key, forcing $\Omega(1)$ relative error at any fixed $\rho > 0$ — illustrating why distribution-free $(\epsilon,\delta)$ guarantees for joins remain open.

---
*Part of the [DBMS Research catalog](../../README.md).*
