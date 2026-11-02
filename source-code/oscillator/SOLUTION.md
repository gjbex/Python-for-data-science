# Conceptual reference solution: when is a resonance curve trustworthy?

This document is a reference answer to the investigation in
[`SCENARIO.md`](SCENARIO.md). It explains the scientific reasoning and the
conclusions; it deliberately does not reproduce the DuckDB or Polars
implementation. Try the investigation before reading further if you want to
make the analytical decisions independently.

The numerical results below apply to the deterministic default dataset and to
the model choices documented here. The executable calculations remain in
[`duckdb_analysis.ipynb`](duckdb_analysis.ipynb) and
[`polars_analysis.ipynb`](polars_analysis.ipynb). If the generator settings,
analysis windows, or decision thresholds change, the numerical values should
be recalculated rather than copied from this document.

## Notation and analysis choices

The following symbols are used throughout:

- $A$ is the estimated displacement amplitude in metres;
- $r = \omega_\mathrm{d}/\omega_0$ is the dimensionless ratio of driving
  angular frequency $\omega_\mathrm{d}$ to natural angular frequency
  $\omega_0$;
- $\zeta$ is the dimensionless damping ratio;
- $G = A\omega_0^2/a$ is the dimensionless response gain, where $a$ is the
  driving-acceleration amplitude;
- $Q$ is the quality factor obtained by dividing the sampled peak frequency
  ratio by the half-power bandwidth;
- $\tau_A$ is the accepted relative change in amplitude between the last two
  windows; and
- $\tau_R$ is the accepted ratio of unexplained root-mean-square residual to
  fitted amplitude.

The model solution uses eight non-overlapping, half-open windows of five
driving periods. The baseline classification sets both $\tau_A$ and $\tau_R$
to 1%. These thresholds make the decision rule explicit, but they are not
universal physical constants.

## Central conclusion

Increasing damping lowers the resonance peak, moves it gradually below
$r=1$, and broadens it. That conclusion is supported for the ensembles with
$\zeta \geq 0.03$. The least-damped ensemble, $\zeta=0.01$, has not settled
sufficiently after 40 driving periods to support a trustworthy peak height or
bandwidth. Its apparent curve should be reported as unresolved rather than as
a noisy version of the steady-state curve.

The analytical steady-state response explains the settled simulations very
well. The remaining disagreement is concentrated in the lightly damped runs
and decreases as later windows are used, which is the pattern expected from a
slowly decaying transient. This is a consistency check between two
representations of the same idealized oscillator, not an independent
experimental validation of the physical model.

## Establish the data integrity first

The default dataset contains 606 runs on a grid of six damping ratios and 101
frequency ratios, 1,212,606 observations, and six solver batches. Every
observation joins to exactly one run. The validation finds:

- no missing or additional samples within a run;
- no incomplete runs;
- no disagreement between the Hive partition value and the authoritative run
  metadata; and
- no failed solver batches.

These checks do not prove that the simulation represents a real physical
system, but they rule out several mundane explanations for a distorted
resonance curve. Solver evaluation counts remain batch-level diagnostics and
cannot be interpreted as per-run computational costs.

## 1. What should count as response amplitude?

The harmonic least-squares amplitude is the most appropriate primary
estimator for this question. It isolates the component at the known driving
frequency and provides a residual measure for motion that the fitted harmonic
does not explain. That is precisely the component represented by the
steady-state gain formula.

Half peak-to-peak amplitude and demeaned root-mean-square amplitude remain
useful diagnostics. Their advantage is simplicity; their disadvantage is that
they summarize all motion in the selected window. A decaying free oscillation,
beating, drift, or another frequency can therefore change them without being
part of the drive-synchronous response.

The simplified grouped harmonic fit is justified here because the samples are
uniformly spaced in phase, every window spans a whole number of driving
periods, half-open windows avoid double-counting the repeated endpoint, and no
samples are missing. Without those conditions, the constant, sine, and cosine
terms need not be orthogonal. A general least-squares solution based on a QR or
singular-value decomposition would then be required.

At $r=1$ in the final five-period window, the three estimators illustrate both
their agreement and their limitations:

| $\zeta$ | Half peak-to-peak $A$ (m) | Demeaned RMS $A$ (m) | Harmonic $A$ (m) | Harmonic residual RMS (m) |
| ---: | ---: | ---: | ---: | ---: |
| 0.01 | 45.7304 | 45.2438 | 45.2419 | 0.2998 |
| 0.03 | 16.6242 | 16.6520 | 16.6520 | 0.0028 |

The close estimates for $\zeta=0.01$ do **not** establish steady state. All
three estimators can describe the same transient-contaminated window. Evidence
from changes between successive windows is still required.

## 2. Which runs have reached steady state?

The baseline decision compares the final two five-period windows. A run is
classified as:

- `still_changing` when its harmonic amplitudes differ by more than
  $\tau_A=1\%$;
- `stable_amplitude_with_residual` when the amplitude passes that test but the
  residual fraction exceeds $\tau_R=1\%$; or
- `stable_response` only when both tests pass.

The resulting counts are:

| $\zeta$ | Stable response | Stable amplitude with residual | Still changing |
| ---: | ---: | ---: | ---: |
| 0.01 | 8 | 38 | 55 |
| 0.03 | 101 | 0 | 0 |
| 0.05 | 101 | 0 | 0 |
| 0.10 | 101 | 0 | 0 |
| 0.20 | 101 | 0 | 0 |
| 0.40 | 101 | 0 | 0 |

Thus, 93 of the 101 least-damped runs remain unresolved by the baseline rule.
Even the other eight should be treated cautiously: a slowly varying transient
can happen to change little between two adjacent windows. Their later
disagreement with steady-state theory shows that passing this local rule is
not sufficient evidence in the least-damped ensemble.

This pattern is physically plausible. The transient envelope decreases only
as $\exp(-2\pi\zeta N/r)$ after $N$ driving periods. Equal simulation lengths
in periods therefore do not imply equal settling at different $\zeta$ and
$r$. The decay expression is useful for planning a longer run, but it cannot
reclassify an existing run: the transient's initial magnitude and phase are
not inferred from the envelope alone.

The correct response to an unresolved run is to retain and label it, extend
the simulation, and repeat the window comparison. Removing unresolved runs
would preferentially remove low-damping and near-resonance cases and would
bias the scientific result.

## 3. How does damping change resonance?

The final-window harmonic estimates give the following sampled peaks and
half-power results:

| $\zeta$ | Peak $r$ | Peak $G$ | Peak defensible? | Half-power width | $Q$ interval |
| ---: | ---: | ---: | :---: | :---: | :---: |
| 0.01 | 1.00 | 45.2419 | No | unresolved | unresolved |
| 0.03 | 1.00 | 16.6520 | Yes | 0.05--0.07 | 14.29--20.00 |
| 0.05 | 1.00 | 9.9999 | Yes | 0.09--0.11 | 9.09--11.11 |
| 0.10 | 0.99 | 5.0252 | Yes | 0.19--0.21 | 4.71--5.21 |
| 0.20 | 0.96 | 2.5515 | Yes | 0.41--0.43 | 2.23--2.34 |
| 0.40 | 0.82 | 1.3638 | Yes | not bracketed | not bracketed |

The width and $Q$ intervals acknowledge the frequency-grid spacing of 0.01;
they do not claim sub-grid interpolation. The table supports three linked
conclusions: greater damping lowers the peak, shifts it below the natural
frequency, and broadens the response.

Two rows require different follow-up experiments. For $\zeta=0.01$, the
simulation must run longer before its peak can be interpreted. For
$\zeta=0.40$, the peak is settled, but the lower half-power crossing lies
outside the sampled range. Extending the frequency grid below $r=0.5$ is
needed to determine the full bandwidth. A smoother plot would solve neither
problem because interpolation cannot create missing evidence.

## 4. Does the steady-state theory explain the data?

For $\zeta \geq 0.03$, the final-window estimates closely match the
steady-state prediction. The maximum absolute relative differences are about
0.13% for $\zeta=0.03$, 0.0059% for $\zeta=0.05$, and below
$4\times10^{-6}\%$ for $\zeta\geq0.10$.

The time dependence of the discrepancy matters more than any one number. For
$\zeta=0.03$, the maximum difference falls from about 64.8% in periods 1--5
to about 0.13% in periods 36--40. For $\zeta=0.05$, it falls from about 50.5%
to about 0.0059%. This systematic decrease supports transient decay as the
explanation for early disagreement.

The least-damped ensemble remains problematic. Its maximum final-window
difference is about 9.5% near resonance. More importantly, the eight runs
provisionally labelled `stable_response` still include a difference of about
6.9%. Adjacent-window stability can therefore produce a false sense of
convergence when a slowly decaying oscillation happens to change little over
that comparison interval.

Agreement has a limited interpretation. It supports the implementation of the
simulation, aggregation, and analytical calculation under their shared
assumptions. It does not independently validate linear damping, the forcing
model, or the applicability of this idealized oscillator to an experiment.

## 5. How sensitive is the conclusion to analytical choices?

The first sensitivity check changes both tolerances together:

| Scenario | $\tau_A=\tau_R$ | $\zeta$ | Stable response | Stable amplitude with residual | Still changing |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Strict | 0.5% | 0.01 | 0 | 37 | 64 |
| Baseline | 1% | 0.01 | 8 | 38 | 55 |
| Permissive | 2% | 0.01 | 18 | 40 | 43 |
| Strict | 0.5% | 0.03 | 93 | 8 | 0 |
| Baseline | 1% | 0.03 | 101 | 0 | 0 |
| Permissive | 2% | 0.03 | 101 | 0 | 0 |

The number assigned to each class is visibly threshold-dependent. Because
$\tau_A$ and $\tau_R$ are changed together, this experiment cannot identify
which criterion causes a particular reclassification. Varying them
independently would be the appropriate follow-up if that distinction mattered.

The headline result is nevertheless robust. The apparent $\zeta=0.01$ peak
at $r=1$ remains `still_changing` under all three tolerance scenarios, while
the peaks for $\zeta\geq0.03$ remain defensible. The response trend therefore
does not depend on selecting the most convenient threshold, but the precise
count of settled runs does.

Changing the amplitude estimator produces the same peak frequency for most
ensembles. One meaningful exception occurs at $\zeta=0.40$: harmonic
least-squares and demeaned RMS select $r=0.82$, whereas peak-to-peak selects
$r=0.83$. The difference, $\Delta r=0.01$, is exactly one frequency-grid
step. It is evidence against claiming a more precise peak location, not
evidence for choosing one estimator because it gives a preferred answer.

## What remains unresolved?

A defensible report should retain the following limitations:

1. Extend the $\zeta=0.01$ simulations and repeat the same settling tests. No
   trustworthy peak range can be reported from the current duration.
2. Extend the frequency grid below $r=0.5$ for $\zeta=0.40$ to bracket the
   lower half-power crossing.
3. Refine the frequency grid around narrow, settled peaks only if finer peak
   locations or bandwidths are scientifically important.
4. Test window lengths and $\tau_A$ and $\tau_R$ independently if the
   classification itself is a central result.
5. Use a general least-squares fit if future data contain missing samples,
   unequal weights, or windows that do not span complete driving periods.

The general lesson is not specific to oscillators or to a particular data
tool: reduce large time-series data near its source, retain diagnostics during
that reduction, and make convergence an explicit part of the scientific
claim. A plausible curve is not evidence that the underlying simulations have
reached the state the curve is intended to represent.
