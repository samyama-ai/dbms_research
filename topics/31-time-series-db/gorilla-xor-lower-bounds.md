# Lower bounds for XOR float compression

> **Topic:** Time-Series Databases · **ID:** `31-time-series-db/gorilla-xor-lower-bounds` · **Status:** empirically-open

## 1. Problem Statement

Gorilla-style compression encodes a stream of IEEE-754 doubles by XOR-ing each value with its predecessor and coding the result by its leading/trailing zero structure. The question: **what is the information-theoretic limit on lossless compression of real-valued float time series, and how far is XOR encoding from it?**

Variants:
- **Optimality (decision/quantitative):** for a stochastic source model (e.g., slowly varying signal + quantization), is there a constant-factor or additive separation between Gorilla's bit-rate and the source entropy $H$?
- **Worst-case lower bound:** over adversarial float streams, what is the minimum bits/value any *XOR-then-prefix-code* scheme must spend?
- **Structural:** which properties of the XOR residual distribution (leading-zeros, block width) does Gorilla exploit, and are they sufficient statistics?

"Empirically-open": XOR variants (Chimp, Patas, Elf) keep beating Gorilla in practice, but no proof characterizes the optimum or the gap.

## 2. Mathematical Foundations

A value $v_i \in \{0,1\}^{64}$; residual $x_i = v_i \oplus v_{i-1}$. Gorilla codes $x_i$ by: a 1-bit "same-block" flag; else leading-zero count $\ell_i$ and meaningful-bit width $w_i$, then the $w_i$ significant bits. The achievable rate is

$$R = \mathbb{E}[\,\text{flag} + [\text{new block}](5 + 6) + w_i\,] \text{ bits/value.}$$

The relevant lower bound is Shannon: for any source $P$ over streams, no lossless code beats $H(P)$ in expectation, and no code beats the **Kolmogorov complexity** pointwise up to $O(1)$. For a *parametric* model — say $v_i = q(s_i)$ where $s_i$ is a smooth signal and $q$ a fixed-point/float quantizer — the entropy of $x_i$ is governed by the distribution of changed mantissa bits, i.e. the magnitude of $|s_i - s_{i-1}|$ relative to ULP.

Key tension: XOR is a **fixed, linear** preprocessing map. It is optimal only when the predictor "previous value" matches the source's autocorrelation; against sources with trend or multi-lag structure, XOR-of-lag-1 is provably suboptimal versus a predictor matched to the source, giving an unavoidable redundancy term.

## 3. State of the Art (SOTA)

- **Foundational:** **Gorilla** (Pelkonen et al., VLDB 2015) — Facebook's in-memory TSDB codec; the canonical XOR scheme.
- **Systems-SOTA:** **Chimp** and **Chimp128** (Liakos et al., VLDB 2022) improve trailing-zero handling; **Patas**; **Elf** (Li et al., SIGMOD 2023) erases trailing mantissa zeros before XOR; **ALP** (Afroozeh et al., SIGMOD 2024) adaptively chooses decimal vs. float paths and often dominates XOR families on real decimals.
- **Theory-SOTA:** essentially Shannon/MDL bounds and quantization theory; there is **no tight, codec-specific lower bound** for the XOR class — hence "empirically-open."

## 4. Upper Bound

Gorilla and successors give concrete bits/value upper bounds on real datasets (often 1–2 bytes/value vs. 8). Provable upper bounds exist only relative to source models: under a quantized-smooth-signal model, the rate is $O(\log(\Delta/\text{ULP}))$ bits/value where $\Delta$ bounds successive differences. ALP/Elf tighten the constant on decimal-derived floats. No scheme is proven to reach $H$ for general sources.

## 5. Lower Bound

- **Information-theoretic:** Shannon's source-coding theorem gives $R \ge H(P)$; for incompressible (i.i.d. uniform mantissa) streams, **no codec beats ~64 bits/value**, and XOR cannot help — a trivial but tight worst-case bound.
- **Class-restricted (open):** a tight lower bound on the redundancy of *XOR-with-lag-1 + prefix coding* versus the best predictor-matched code is **not established**. Conjectured separations against trended/seasonal sources are observed empirically (why Chimp/Elf/ALP win) but unproven.
- No cell-probe or communication lower bound is known for the random-access decompression variant.

## 6. The Gap

The gap is genuinely open. We have (a) a trivial worst-case bound (incompressible streams) that XOR meets, and (b) strong empirical evidence that XOR is *sub*-optimal on structured real data, with each new codec extracting more. Missing: a model in which the optimum is characterized and Gorilla's redundancy is provably bounded above/below — i.e., either a theorem "XOR is within $c$ of entropy for source class $\mathcal{C}$" or a separation "any XOR-class codec loses $\Omega(g(n))$ bits on $\mathcal{C}$."

## 7. Current Research (as of June 2026)

- Adaptive/learned predictors replacing fixed lag-1 XOR (ALP-style decimal detection; per-block predictor selection) *(frontier — verify)*.
- SIMD/vectorized decoders making fairer rate-vs-throughput Pareto comparisons (FastLanes/ALP line, CWI/Boncz group).
- Theoretical efforts to model float residual entropy under quantization.
- Groups: CWI Database Architectures (Boncz, Afroozeh), the Chimp/Elf authors (Athens), TSDB vendors (InfluxData, Timescale, VictoriaMetrics).

## 8. Future Work

- A redundancy theorem for the XOR codec class against autocorrelated sources.
- Lower bounds for random-access (block-decodable) float compression.
- Unifying decimal-aware (ALP) and bit-pattern (Gorilla/Chimp) views under one optimality criterion.

## 9. Key References

- **[Foundational]** T. Pelkonen et al. *Gorilla: A Fast, Scalable, In-Memory Time Series Database.* VLDB, 2015.
- **[SOTA]** P. Liakos, K. Papakonstantinou, Y. Kotidis. *Chimp: Efficient Lossless Floating Point Compression for Time Series Databases.* VLDB, 2022.
- **[SOTA]** R. Li, Z. Li, et al. *Elf: Erasing-Based Lossless Floating-Point Compression.* SIGMOD/VLDB, 2023.
- **[SOTA]** A. Afroozeh, L. Kuffo, P. Boncz. *ALP: Adaptive Lossless Floating-Point Compression.* SIGMOD, 2024.
- **[Foundational]** T. Cover, J. Thomas. *Elements of Information Theory.* Wiley, 2006.

---
*Part of the [DBMS Research catalog](../../README.md).*
