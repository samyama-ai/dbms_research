# The latency-completeness-cost trade-off frontier

> **Topic:** Streaming & Continuous Queries · **ID:** `18-streaming-queries/latency-completeness-tradeoff` · **Status:** empirically-open

## 1. Problem Statement

For a windowed continuous query under out-of-order, skewed input, three quantities are in tension:

- **Latency** $L$ — processing-time delay from when a result *could* be emitted (event-time complete) to when it *is* emitted;
- **Completeness** $C$ — fraction (or weight) of relevant input reflected in the emitted result, i.e. $1$ minus incompleteness from late/dropped data;
- **Cost** $R$ — resource usage (state size, CPU, memory, $/hour, energy) needed to sustain the chosen $(L,C)$.

The problem: **characterize the Pareto frontier $\mathcal{P}\subseteq \{(L,C,R)\}$ of achievable triples for a given query class and input model, and design policies that operate on or near $\mathcal{P}$ with knobs (watermark lag, trigger policy, allowed lateness, state TTL, parallelism, shedding).** Variants: a fixed-budget optimization (max $C$ s.t. $L\le L_0, R\le R_0$); the *shape* of the frontier (is it convex? where are the knees?); and an online/adaptive variant (track a moving frontier under workload drift). Marked **empirically-open**: the qualitative trade-off is folklore, but a *quantitative, query-aware, provable* frontier is not established.

## 2. Mathematical Foundations

Let the input delay distribution be $F_D$ with tail $\bar F_D(\delta)=\Pr[D>\delta]$. For a watermark-lag policy with lag $\delta$ and no retraction: latency $L=\delta$ and incompleteness $1-C=\bar F_D(\delta)$, so the latency–completeness curve is exactly the **delay CDF**: $C(L)=F_D(L)$ — concave for typical (sub-exponential) delays, with diminishing completeness returns (the long tail). Cost enters via **state retention**: holding window state until lag $\delta$ costs $R\propto$ (window state) $\times$ (retention time $\propto\delta$) plus reprocessing cost if retractions are enabled.

This is a **multi-objective optimization** over policies $\pi$; the frontier is $\mathcal P=\{(L,C,R): \nexists\,\pi' \text{ dominating}\}$. With retraction/refinement (emit early, correct later), $C$ can reach $1$ asymptotically at the price of *result churn* — a fourth axis (number of revisions). Queueing theory (Little's law $\bar n = \lambda \bar L$) bounds backlog vs latency; **competitive analysis** frames online policy choice; and the cost–accuracy axis connects to **sketch/approximation** error budgets. No closed-form $\mathcal P$ is known except in the simplest single-operator, stationary-delay case where it equals the delay CDF crossed with a linear retention-cost model.

## 3. State of the Art (SOTA)

- **The Dataflow Model** (Akidau et al., VLDB 2015) names the trade-off explicitly via *triggers* (when to emit), *accumulation mode* (how revisions combine), and *allowed lateness* — the practical control surface, but provides **no frontier characterization**.
- **AQP / online aggregation** lineage (Hellerstein, Haas, Wang 1997; **BlinkDB** Agarwal et al. EuroSys 2013) characterizes the *accuracy–latency–cost* trade-off for *approximate* queries with error bars — the closest formal frontier, in the sampling (not lateness) regime.
- **Adaptive scheduling / latency-SLA systems** (Aurora/Borealis QoS; **Flink/Spark Structured Streaming** with watermark + trigger tuning) operate the knobs heuristically.
- **Stream slicing / shared windows** (Traub et al.) push down the $R$ axis. No system exposes a *measured* 3-D Pareto surface.

## 4. Upper Bound

In the single-operator, stationary-delay model, the achievable curve is **exactly $C(L)=F_D(L)$** (no policy beats the delay CDF without retraction), and with retraction $C\to 1$ as revision budget grows — these are tight *constructive* upper bounds. For approximate aggregates, BlinkDB-style sampling gives error $\propto 1/\sqrt{n}$ at cost $\propto n$, an explicit $C$–$R$ Pareto curve. Beyond these special cases, only empirical Pareto fronts (benchmark-measured) exist.

## 5. Lower Bound

Lower bounds on the frontier come from the **delay-tail impossibility**: distribution-free, no finite latency guarantees completeness $>\sup$ of the realized tail, so $\mathcal P$ cannot dominate the input CDF (an information-theoretic limit, same root as the watermark lower bound). Queueing lower bounds (Little's law) force $\bar L\ge \bar n/\lambda$, lower-bounding latency for a given backlog. **Communication/space lower bounds** for streaming aggregates (e.g., $\Omega(1/\epsilon^2)$ space for $\epsilon$-approximate frequency moments — Alon–Matias–Szegedy) lower-bound the cost axis for accuracy targets. A *unified* lower bound coupling all three axes for general windowed queries is **not known**.

## 6. The Gap

The gap is that **special cases are characterized** (single-operator stationary delay = delay CDF; AQP accuracy–cost = sampling curve) while the **general, multi-operator, drifting-workload 3-D frontier is empirically observed but theoretically uncharacterized**. We lack (i) a model coupling lateness-completeness with resource cost across an operator graph, (ii) proof that practical knob-tuning is near-Pareto, and (iii) lower bounds binding all three axes jointly. This is why the status is **empirically-open**: benchmarks show the trade-off, theory has not pinned its shape or optimality.

## 7. Current Research (as of June 2026)

Active directions: (i) **cost-aware autoscaling + watermark co-tuning** with SLA guarantees (DS2, Megaphone, and successors) *(frontier — verify)*; (ii) **revision-budgeted streaming** via DBSP/differential dataflow, making the completeness axis cheap to recover and reframing the frontier around *revision cost*; (iii) **learned controllers** (RL/Bayesian-opt) that empirically trace the Pareto surface online under drift *(frontier — verify)*. Groups: ETH/Systems (Hoffmann, Roscoe), TU Berlin (Markl), Berkeley RISE-lineage (AQP), Microsoft (DBSP/Materialize). A clean theoretical frontier remains the prize.

## 8. Future Work

- A provable 3-D Pareto characterization for canonical windowed query classes.
- Joint lower bounds coupling latency, completeness, and space/cost.
- Online controllers with regret guarantees against the (drifting) optimal frontier.
- Incorporating the *revision/churn* axis as a first-class fourth dimension.

## 9. Key References

- **[Foundational/SOTA]** Tyler Akidau et al. *The Dataflow Model.* PVLDB, 2015.
- **[Foundational]** Joseph M. Hellerstein, Peter J. Haas, Helen J. Wang. *Online Aggregation.* SIGMOD, 1997.
- **[SOTA]** Sameer Agarwal, Barzan Mozafari, Aurojit Panda, Henry Milner, Samuel Madden, Ion Stoica. *BlinkDB: Queries with Bounded Errors and Bounded Response Times on Very Large Data.* EuroSys, 2013.
- **[Foundational]** Noga Alon, Yossi Matias, Mario Szegedy. *The Space Complexity of Approximating the Frequency Moments.* STOC, 1996.
- **[SOTA]** Mihai Budiu et al. *DBSP: Automatic Incremental View Maintenance for Rich Query Languages.* PVLDB, 2023.

---
*Part of the [DBMS Research catalog](../../README.md).*
