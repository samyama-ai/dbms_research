# Oracle for Floating-Point and Decimal Semantics

> **Topic:** Benchmarking, Testing & Verification · **ID:** `33-benchmarking-testing/numeric-semantics-oracle` · **Status:** open

## 1. Problem Statement
When testing or comparing database engines, a query's numeric result depends on **arithmetic semantics**: IEEE-754 binary floating point vs. exact/fixed-scale `DECIMAL/NUMERIC`, rounding mode, intermediate precision and result-type promotion, overflow handling, division/scale rules, and — critically — **aggregate evaluation order**, which differs across engines and across runs (parallel/partitioned execution). The problem: build an **oracle** that decides whether two engines' numeric outputs are "the same answer" — i.e., whether a discrepancy is a *legitimate semantic difference* (allowed by the standard / engine spec) or a **bug**.

Variants:
- **Decision (oracle):** given outputs $a,b$ and the query, decide *equivalent / acceptable-difference / discrepant(bug)*.
- **Tolerance synthesis (optimization):** compute the tightest provably-sound tolerance $\tau$ such that any difference $\le\tau$ is explainable by permitted reordering/rounding.
- **Certification:** prove a result is **exact** (decimal/integer path) so zero tolerance applies.

This is the linchpin that makes differential testing of analytics engines sound — without it, every floating-point aggregate flags spurious "bugs."

## 2. Mathematical Foundations
IEEE-754 floating-point addition is **not associative**: $(a\oplus b)\oplus c \neq a\oplus(b\oplus c)$ in general. The standard model is $\text{fl}(x\circ y)=(x\circ y)(1+\delta),\ |\delta|\le u$ (unit roundoff $u=2^{-53}$ for binary64). For a sum of $n$ terms, naive accumulation has the classic forward bound
$$\Big|\widehat{\textstyle\sum x_i}-\textstyle\sum x_i\Big| \le \frac{(n-1)u}{1-(n-1)u}\sum_i|x_i| = \gamma_{n-1}\sum_i|x_i|,$$
so a *sound* equality oracle for SUM/AVG over reordered, parallel summation must admit a tolerance proportional to $\gamma_{n-1}\sum|x_i|$ (the **condition number** $\kappa=\sum|x_i|/|\sum x_i|$ governs relative sensitivity; catastrophic cancellation $\Rightarrow\kappa\to\infty$). **Compensated (Kahan)** and pairwise summation tighten this to $O(u)$ independent of $n$.

`DECIMAL` arithmetic is **exact** within scale (rational arithmetic with a fixed denominator) but engines differ on *scale-of-result* rules (multiplication scale, division precision, rounding mode: half-up vs. half-even). Thus the oracle is a case analysis on **type lattice + reordering semialgebra**: exact types $\Rightarrow$ zero tolerance modulo declared rounding; float types $\Rightarrow$ interval/error-bound certificate. Overflow turns the comparison into a domain question (`NULL`/error/saturate/wrap differ by SQL dialect).

## 3. State of the Art (SOTA)
- **Differential testing** (SQLancer-style, Rigger & Su) finds result bugs but largely sidesteps float aggregates or uses ad-hoc epsilons — a known soundness gap.
- **Interval/affine arithmetic** and **rigorous error analysis** (Higham's framework) provide sound a-posteriori bounds usable as tolerances.
- **Floating-point reasoning tools:** SMT **QF_FP** solvers (Z3, MathSAT, Colibri), **Gappa** (proved FP bounds), **FPTaylor/Daisy/PRECiSA** (rigorous round-off bound certification) — the toolkit an oracle can call.
- **SQL standard / engine specs** define `DECIMAL` scale rules (SQL:2016) and `IEEE-754` binding; PostgreSQL/DuckDB/Spark/Snowflake differ in promotion and division scale, documenting the legitimate-difference space.

There is **no standard, engine-agnostic numeric oracle**; practitioners hand-tune epsilons.

## 4. Upper Bound
For the **exact** (integer/decimal) fragment with declared rounding, the oracle is *decidable and exact*: recompute in arbitrary-precision rationals and compare — polynomial in input size. For the **float** fragment, a *sound* oracle computes a rigorous error bound via Higham's analysis or tools like Gappa/FPTaylor in time roughly linear in the expression DAG, certifying acceptance whenever $|a-b|\le \tau(\text{data})$. SMT QF_FP can decide *bit-exact* equivalence of two evaluation orders for small expressions, giving an exact (but exponential-worst-case) oracle.

## 5. Lower Bound
Deciding bit-exact equivalence of floating-point expressions is **NP-hard** (QF_FP satisfiability is NP-hard; the bit-blasted theory is large), so an exact reorder-equivalence oracle is intractable in the worst case. Worse, computing the *exact* worst-case round-off error over all reorderings/inputs in a range is at least NP-hard and in general undecidable for unbounded programs (reachability/reasoning over loops). The unavoidable **catastrophic cancellation** phenomenon ($\kappa\to\infty$) means *no finite relative tolerance* is simultaneously sound and useful for ill-conditioned inputs — an information-theoretic obstruction: the engines may legitimately disagree by an unbounded relative amount.

## 6. The Gap
Open. The exact-decimal fragment is solved (recompute in rationals); the float fragment is fundamentally limited by NP-hardness of bit-exact reasoning and by ill-conditioning making *any* fixed tolerance unsound. The gap: between a cheap-but-unsound epsilon and a sound-but-expensive rigorous-error-bound oracle, with no satisfying middle for ill-conditioned aggregates. Closing it requires (a) a standardized semantics map of legitimate cross-engine differences and (b) a condition-number-aware tolerance that is sound *and* practical, plus flagging ill-conditioned queries as "indeterminate" rather than "bug."

## 7. Current Research (as of June 2026)
- Integrating **rigorous FP error analysis** (FPTaylor/Daisy/PRECiSA-style) into differential SQL testing to replace hand-tuned epsilons *(frontier — verify)*.
- Condition-number-aware oracles that classify aggregates as *exact / bounded / indeterminate*; cross-engine **semantics catalogs** for DECIMAL scale and overflow.
- SMT QF_FP-backed checking of summation-order equivalence for vectorized/parallel engines *(frontier — verify)*.
- Groups: Rigger (NUS, SQLancer), the rigorous-numerics community (Higham — Manchester; Darulova — Daisy; Solovyev/FPTaylor; NASA PRECiSA), and SQL-semantics formalization efforts (Chu/Cheung/Suciu — HoTTSQL/Cosette).

## 8. Future Work
- A formal, machine-readable specification of per-engine numeric semantics (promotion, scale, rounding, overflow).
- A composable oracle returning a *certificate* (exact / tolerance $\tau$ / indeterminate) instead of a boolean.
- Compensated-summation-aware reference implementations as ground truth.
- Standardization of acceptable cross-engine numeric divergence for benchmark fairness.

## 9. Key References
- **[Foundational]** IEEE. *IEEE Standard for Floating-Point Arithmetic, IEEE 754-2019.* — [DOI](https://doi.org/10.1109/IEEESTD.2019.8766229)
- **[Foundational]** Higham. *Accuracy and Stability of Numerical Algorithms (2nd ed.).* SIAM, 2002. (Summation error bounds; $\gamma_n$ analysis.) — [DOI](https://doi.org/10.1137/1.9780898718027)
- **[Foundational]** Kahan. *Further Remarks on Reducing Truncation Errors (compensated summation).* CACM, 1965. — [DOI](https://doi.org/10.1145/363707.363723)
- **[SOTA]** Solovyev, Jacobsen, Rakamarić, Gopalakrishnan. *Rigorous Estimation of Floating-Point Round-off Errors with Symbolic Taylor Expansions (FPTaylor).* FM 2015 / TOPLAS. — [DOI](https://doi.org/10.1145/3230733)
- **[SOTA]** Rigger, Su. *Testing Database Engines via Pivoted Query Synthesis / NoREC.* OSDI 2020. — [USENIX](https://www.usenix.org/conference/osdi20/presentation/rigger)
- **[SOTA]** Darulova, Izycheva, et al. *Daisy: Framework for Analysis and Optimization of Numerical Programs.* TACAS 2018. — [DOI](https://doi.org/10.1007/978-3-319-89960-2_15)
- **[Foundational]** Daumas, Melquiond. *Gappa: Certifying Floating-Point Computations.* ACM TOMS, 2010. — [DOI](https://doi.org/10.1145/1644001.1644003)

## 10. Worked Example

Take a one-column table `R(x)` with three binary64 values and the query `SELECT SUM(x) FROM R`:
$$x_1 = 10^{16},\quad x_2 = 1.0,\quad x_3 = -10^{16}.$$
The exact sum is $1.0$. Engine $A$ partitions and accumulates left-to-right: $(x_1 \oplus x_2)\oplus x_3$. But $10^{16}+1$ is not representable in binary64 (next representable value above $10^{16}$ is $10^{16}+2$), so $x_1\oplus x_2 = 10^{16}$ exactly, and the result is $10^{16}\oplus(-10^{16}) = 0.0$. Engine $B$ accumulates $x_1\oplus x_3$ first $=0$, then $0\oplus x_2 = 1.0$. So $A$ reports $0$ and $B$ reports $1$.

A naive equality oracle flags a "bug." But this is **catastrophic cancellation**: $\sum|x_i| = 2{\times}10^{16}$ while $|\sum x_i| = 1$, so the condition number is $\kappa = 2{\times}10^{16}$. The sound forward bound admits tolerance $\tau \approx \gamma_2 \sum|x_i| \approx 2u\cdot 2{\times}10^{16} \approx 2^{-53}\cdot 4{\times}10^{16} \approx 4.4$. Since $|0-1| = 1 \le \tau$, both outputs are *acceptable* under reordering. The oracle's correct verdict is **indeterminate** (ill-conditioned), not "bug."

---
*Part of the [DBMS Research catalog](../../README.md).*
