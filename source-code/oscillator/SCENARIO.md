# Scenario: when is a resonance curve trustworthy?

## Purpose

You are studying an ensemble of simulated, driven, damped oscillators. Your
scientific goal is to determine how damping changes the resonance response. A
curve can look plausible even when some simulations still contain a strong
transient, so the analysis must first establish which response estimates are
credible.

This investigation is deliberately technology-agnostic. Use any query,
dataframe, numerical, or visualization tools that can perform the required
operations. The important outcomes are the analytical decisions, the evidence
supporting them, and the limitations of the resulting claims.

Suggested time: 90--120 minutes. Familiarity with grouping, joining, summary
statistics, and basic plotting is helpful; prior database experience is not
required.

## Learning objectives

By the end of the investigation, you should be able to:

- reduce partitioned time-series data to scientifically meaningful summaries;
- choose and justify a response-amplitude estimator;
- diagnose whether a forced oscillator has reached steady state;
- explain how damping changes the height, location, and width of a resonance
  curve;
- test a data-derived result against an analytical prediction; and
- distinguish a scientific conclusion from limitations caused by sampling,
  simulation duration, and analysis choices.

## Scientific model

Each run solves

$$
\frac{\mathrm{d}^2 x}{\mathrm{d}t^2}
+ 2\zeta\omega_0\frac{\mathrm{d}x}{\mathrm{d}t}
+ \omega_0^2x
= a\cos(\omega_\mathrm{d}t),
$$

where:

- $x$ is displacement in metres;
- $t$ is time in seconds;
- $\zeta$ is the dimensionless damping ratio;
- $\omega_0$ is the natural angular frequency in radians per second;
- $\omega_\mathrm{d}$ is the driving angular frequency in radians per second;
  and
- $a$ is the driving-acceleration amplitude in metres per second squared.

Define the dimensionless frequency ratio
$r = \omega_\mathrm{d}/\omega_0$. All runs start from zero displacement and
zero velocity. They span six values of $\zeta$ and 101 values of $r$, from
0.5 to 1.5. Each run contains 40 driving periods sampled at 50 positions per
period, plus the final endpoint.

For a steady-state sinusoidal response with amplitude $A$, the theoretical
dimensionless gain is

$$
G(r, \zeta)
= \frac{A\omega_0^2}{a}
= \frac{1}{\sqrt{(1-r^2)^2 + (2\zeta r)^2}}.
$$

This expression is a prediction to test, not evidence that every recorded run
has reached steady state.

## Data and grain

The dataset has three related components:

| Component | One row represents | Role in the investigation |
| --- | --- | --- |
| `runs.parquet` | one oscillator run | Physical parameters and run metadata |
| `observations/` | one sampled time point in one run | Hive-partitioned by damping ratio; contains displacement, velocity, phase, time, and specific energy |
| `solver_batches.parquet` | one batch of runs submitted to the solver | Numerical success and batch-level diagnostics |

`run_id` links observations to run parameters. `batch_id` links runs to solver
metadata. Solver evaluation counts describe a whole batch and must not be
interpreted as the computational cost of an individual run.

The observation directories follow the Hive convention
`damping_ratio=<value>`. A dataset reader can expose that path value as a
column and avoid reading other damping partitions when a filter selects one or
more values. Treat it as a useful access path, not as a second independent
source of physics metadata. Hive readers commonly expose directory values as
strings, so convert the canonical decimal value before verifying that it
agrees with `runs.parquet`, which remains authoritative for run parameters.

Before interpreting the physics, establish that:

- the parameter grid contains the expected $6 \times 101 = 606$ runs;
- run identifiers have the expected uniqueness and join cardinality;
- Hive partition values agree with the damping ratios in the run metadata;
- every run is marked complete and belongs to a successful solver batch;
- each run has the expected number and range of samples; and
- the quantities used in the analysis are finite.

Record any failed check. Do not silently discard a run merely because it is
inconvenient to analyse.

## Central research question

> How does damping change the resonance response, and which simulated runs
> have evolved long enough for that response to be estimated reliably?

Answer this through the following linked questions. Treat each question as a
scientific decision rather than as a prescribed sequence of software calls.

## 1. What should count as response amplitude?

The observations contain many rows per run, but the resonance curve needs one
credible response estimate per run. Decide how to obtain it over an integer
number of driving periods. The driving period is already known from the run
metadata:

$$
T_\mathrm{d} = \frac{2\pi}{\omega_\mathrm{d}},
$$

where $T_\mathrm{d}$ is the driving period and $\omega_\mathrm{d}$ is the
driving angular frequency. Using windows that span whole driving periods
reduces dependence on where a window begins and ends; the estimators below do
not estimate the period.

Let $x_i$ be displacement sample $i$ in a window containing $n$ samples, and
let $\bar{x}$ be the mean displacement in that window. Possible amplitude
estimators include:

- half the peak-to-peak displacement,

  $$
  \hat{A}_\mathrm{pp}
  = \frac{\max_{1 \leq i \leq n}(x_i)
  - \min_{1 \leq i \leq n}(x_i)}{2},
  $$

  where $\hat{A}_\mathrm{pp}$ is the estimated amplitude. This estimator is
  intuitive and unaffected by a constant displacement offset, but it is
  sensitive to sampling positions, window length, and transient beating;

- the amplitude derived from the root-mean-square variation about the mean,

  $$
  \bar{x} = \frac{1}{n}\sum_{i=1}^{n}x_i,
  \qquad
  \hat{A}_\mathrm{RMS}
  = \sqrt{\frac{2}{n}\sum_{i=1}^{n}(x_i-\bar{x})^2},
  $$

  where $\hat{A}_\mathrm{RMS}$ is the estimated amplitude. It equals the
  amplitude of a single sinusoid sampled over complete periods. Subtracting
  $\bar{x}$ removes a constant offset, but drift, multiple frequencies, and
  transients can make that interpretation invalid; and

- a harmonic fit at the known driving frequency,

  $$
  x_i = b_0 + b_c\cos(\phi_i) + b_s\sin(\phi_i) + \epsilon_i,
  $$

  where $\phi_i = \omega_\mathrm{d}t_i$ is the driving phase of sample $i$ in
  radians, $t_i$ is its time in seconds, $b_0$ is an offset, $b_c$ and $b_s$
  are fitted coefficients, and $\epsilon_i$ is the unexplained residual. Since
  the driving frequency is known, obtain the coefficients by the linear
  least-squares problem

  $$
  \underset{b_0,b_c,b_s}{\operatorname{minimize}}
  \sum_{i=1}^{n}
  \left[x_i-b_0-b_c\cos(\phi_i)-b_s\sin(\phi_i)\right]^2.
  $$

  The sampling design makes this fit much simpler than a general matrix
  decomposition. For uniformly spaced phases over complete driving periods,
  the constant, cosine, and sine terms are mutually orthogonal. The
  least-squares coefficients then reduce to grouped aggregates:

  $$
  b_0 = \frac{1}{n}\sum_{i=1}^{n}x_i,
  $$

  $$
  b_c = \frac{2}{n}\sum_{i=1}^{n}x_i\cos(\phi_i),
  \qquad
  b_s = \frac{2}{n}\sum_{i=1}^{n}x_i\sin(\phi_i).
  $$

  The fitted drive-frequency amplitude is

  $$
  A = \sqrt{b_c^2+b_s^2}.
  $$

  A residual root-mean-square measure can also be calculated from aggregates:

  $$
  R_\mathrm{RMS}
  = \sqrt{\max\left(
      0,
      \frac{1}{n}\sum_{i=1}^{n}x_i^2
      - b_0^2
      - \frac{b_c^2+b_s^2}{2}
    \right)},
  $$

  where $R_\mathrm{RMS}$ measures motion not explained by the fitted harmonic.
  The maximum with zero prevents a tiny negative value caused by floating-point
  rounding.

The simplified least-squares formulas are valid only when:

- phase samples are uniformly spaced;
- each analysis window spans an integer number of driving periods;
- windows are half-open, so the endpoint that duplicates the starting phase is
  not counted twice; and
- all expected samples are present and have equal weight.

Check these assumptions before using the shortcut. If any fails, the three
basis terms are not guaranteed to be orthogonal and the grouped formulas may
be biased. In that case, solve the general three-parameter least-squares
problem with a QR- or singular-value-decomposition method after reducing or
extracting the relevant window data. Under the stated assumptions, only
counts, sums, trigonometric evaluations, and square roots are needed.

The peak-to-peak and root-mean-square estimators describe the total motion in
the selected window; neither separates the forced response from a decaying
transient. The harmonic fit directly targets the drive-frequency response
predicted by the theoretical gain. Its residual is also useful evidence of
motion not synchronized with the drive. Its disadvantage is that a stable
fitted drive component does not, by itself, prove that all transient motion has
disappeared.

Choose an estimator and state why it is appropriate for your claim. If you use
a harmonic fit, retain a residual measure rather than reporting only $A$.

## 2. Which runs have reached steady state?

Estimate the response in several successive windows rather than only in the
last period. Five-period windows are a reasonable starting point, but the
choice should later be tested. For each run and window, retain at least:

- the window boundaries;
- the amplitude estimate;
- the number of observations; and
- a measure of non-sinusoidal or unexplained variation.

Compare adjacent late windows. One possible scale-independent change measure
is

$$
\Delta_A = \frac{2|A_2-A_1|}{A_1+A_2},
$$

where $A_1$ and $A_2$ are amplitudes from consecutive windows. Choose and
justify a tolerance for declaring an amplitude stable. A tolerance is a
scientific acceptance criterion, not a universal constant.

Use the transient envelope to form a prior expectation. Its magnitude decays
approximately as $\exp(-\zeta\omega_0t)$. After $N$ driving periods this factor
is

$$
\exp\left(-\frac{2\pi\zeta N}{r}\right),
$$

where $N$ is the number of elapsed driving periods. Consequently, equal
numbers of driving periods do not imply equal amounts of settling across the
parameter grid. Investigate whether the data follow this pattern.

Take care at window boundaries. The dataset includes both the initial sample
and the endpoint after 40 periods. Use non-overlapping, half-open windows, or
otherwise account explicitly for boundary samples, so that one observation is
not counted in two windows.

Produce a run-level assessment that distinguishes at least:

- stable response with little unexplained motion;
- apparently stable drive-frequency amplitude but appreciable residual motion;
  and
- response still changing between late windows.

Do not simply remove the unsettled runs and continue. Failure to settle is
related to $\zeta$ and $r$, so such filtering can bias the scientific result.
Report these runs separately and explain what additional simulation would be
needed to resolve them.

## 3. How does damping change resonance?

For runs with defensible response estimates, calculate the dimensionless gain
$G = A\omega_0^2/a$. Compare gain against $r$ separately for each value of
$\zeta$.

For every damping ratio, describe:

- the largest observed gain;
- the frequency ratio at which it occurs;
- the width and sharpness of the response peak; and
- the evidence that the estimate is or is not affected by a remaining
  transient.

The frequency grid has spacing 0.01. A very narrow peak may therefore be
represented by only a few runs. Report peak locations and widths at the
resolution supported by the grid; a smooth interpolated curve does not create
new evidence between sampled frequencies.

## 4. Does the steady-state theory explain the data?

Evaluate the theoretical gain at the same $(r, \zeta)$ combinations as the
simulations. Compare predicted and estimated gain using both a signed
difference and a relative difference where the denominator is safely away
from zero.

Examine discrepancies as a function of:

- damping ratio;
- frequency ratio, especially near resonance;
- the settling classification; and
- the chosen estimation window.

Agreement for well-settled runs supports both the simulation and the analysis,
but it is not an independent experimental validation of the oscillator model:
the formula and simulation describe the same idealized linear system.
Disagreement may reveal a transient, an unsuitable summary, a join or grouping
error, insufficient frequency resolution, or a numerical problem. Diagnose
the pattern before choosing an explanation.

## 5. How sensitive is the conclusion to analytical choices?

Repeat the decisive parts of the analysis with at least one credible
alternative, such as:

- a different window length or pair of late windows;
- a stricter or looser stability tolerance; or
- a second amplitude estimator.

Identify which conclusions remain unchanged and which depend on the choice.
If a headline result changes materially, report the range of defensible
answers rather than selecting the most convenient one.

## Organize the analysis around data reduction

The observations contain more than a million rows, whereas the final resonance
curve needs only hundreds. A defensible workflow therefore has three conceptual
stages:

1. select relevant Hive partitions where the research question permits, then
   combine observation rows with the physical parameters for their run;
2. calculate window-level summaries close to the partitioned source data; and
3. move only the compact run- or window-level result into plotting and detailed
   interpretation.

This separation is valuable independently of the software used. It limits
memory use, makes the grain of each intermediate result explicit, and allows
the expensive reduction to be checked separately from visualization. Its cost
is that prematurely discarding residual or convergence information can make a
compact result scientifically misleading.

## Expected evidence

Your completed investigation should contain:

1. a short data-integrity report, including join cardinality and failed checks;
2. a window-level table with one row per run and analysis window;
3. a run-level table containing amplitude, gain, settling evidence, and an
   explicit classification;
4. a visualization of gain against frequency ratio for each damping ratio;
5. a visualization showing where convergence is weak across the $(r, \zeta)$
   parameter grid;
6. a comparison with the theoretical gain at the sampled parameter values;
7. a sensitivity check for at least one consequential analysis choice; and
8. a concise conclusion that answers the central research question while
   separating supported findings from unresolved runs and dataset limitations.

The analysis is successful when another researcher can reconstruct why a run
was considered settled, trace every plotted point to a defined aggregation,
and see how the conclusion would change under a reasonable alternative choice.
