# Oscillator ensemble

This directory contains a deterministic generator for a dataset of driven,
damped harmonic-oscillator simulations. SciPy solves independent oscillators
in batches, and the resulting observations are spread across several Parquet
files. The dataset is intended to illustrate why an analytical query engine is
useful for scientific output that would otherwise be analysed file by file.

The model is

$$
\frac{\mathrm{d}^2 x}{\mathrm{d}t^2}
+ 2\zeta\omega_0\frac{\mathrm{d}x}{\mathrm{d}t}
+ \omega_0^2x
= a\cos(\omega_\mathrm{d}t),
$$

where $x$ is displacement in metres, $t$ is time in seconds, $\zeta$ is the
dimensionless damping ratio, $\omega_0$ is the natural angular frequency in
radians per second, $a$ is the driving-acceleration amplitude in metres per
second squared, and $\omega_\mathrm{d}$ is the driving angular frequency in
radians per second.

The generator uses the dimensionless driving phase
$\phi = \omega_\mathrm{d}t$ as the independent variable, where $\phi$ is the
driving phase in radians. This gives every oscillator the same phase interval
and sampling positions even though their physical periods differ. SciPy's
adaptive `solve_ivp` integrator uses the DOP853 method by default, with an
explicit relative tolerance of $10^{-8}$ and absolute tolerance of $10^{-10}$.

## Generate the data

From the repository root, run:

```bash
pixi run --environment oscillator generate-oscillator-data
```

The default configuration produces 606 simulations and 1,212,606 sampled
observations. Use `python generate_dataset.py --help` inside the environment to
inspect the available size and model parameters. Regeneration is explicit:

```bash
pixi run --environment oscillator generate-oscillator-data --overwrite
```

The generated `data/` directory is intentionally ignored by Git. It contains:

- `solver_batches.parquet`: one row per `solve_ivp` call, containing solver
  status, tolerances, and evaluation counts;
- `runs.parquet`: one row per simulation, containing its physical parameters
  and solver-batch identifier;
- `observations/`: Parquet files such as `batch_0000/part_000.parquet`,
  containing phase, physical time, displacement, velocity, and specific
  energy;
- `manifest.json`: model definitions, generation parameters, schemas, row
  counts, file sizes, and SHA-256 checksums.

The generator first writes and validates a temporary dataset. `--overwrite`
will replace only a directory containing a manifest for this dataset, so it
cannot silently remove an unrelated data directory.

Relative values passed to `--output-dir` are resolved from this `oscillator`
directory, irrespective of the shell's current working directory. Use an
absolute path when generating a temporary dataset elsewhere.

## Intended investigation

The data support an investigation of how the resonance response depends on
damping and how the chosen time window affects an estimated steady-state
amplitude. Lightly damped oscillators may still contain a substantial transient
after 40 driving periods, so treating the final period as representative is an
analytical decision rather than a safe default.

DuckDB can scan the partitioned observations, join them to `runs.parquet` using
`run_id`, aggregate successive phase windows, and reduce the data to one or a
few rows per run. That smaller result can then be moved to pandas or Polars for
visualization. Solver diagnostics remain batch-level metadata and should not be
misinterpreted as per-run performance measurements.

The partition directories deliberately use plain names rather than Hive-style
`key=value` names. Batch identifiers are authoritative columns in
`solver_batches.parquet` and `runs.parquet`.
