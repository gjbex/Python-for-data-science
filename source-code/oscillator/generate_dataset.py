#!/usr/bin/env python
"""Generate a partitioned dataset of driven, damped oscillator simulations."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import tempfile
from functools import partial
from pathlib import Path
from typing import Final
from uuid import uuid4

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import scipy
from scipy.integrate import solve_ivp

DATASET_ID: Final = "oscillator-ensemble-v2"
REPLACEABLE_DATASET_IDS: Final = frozenset({"oscillator-ensemble-v1", DATASET_ID})
GENERATOR_VERSION: Final = "2.0"
SOLVERS: Final = ("DOP853", "RK45")
DEFAULT_DAMPING_RATIOS: Final = (0.01, 0.03, 0.05, 0.10, 0.20, 0.40)


def positive_int(value: str) -> int:
    """Parse a strictly positive integer for an argument."""
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("expected a positive integer")
    return parsed


def positive_float(value: str) -> float:
    """Parse a finite, strictly positive floating-point value."""
    parsed = float(value)
    if not math.isfinite(parsed) or parsed <= 0.0:
        raise argparse.ArgumentTypeError("expected a finite positive number")
    return parsed


def parse_args() -> argparse.Namespace:
    """Parse and validate command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Generate run metadata, solver diagnostics, and partitioned "
            "Parquet observations for a driven, damped oscillator ensemble."
        )
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data"),
        help=(
            "output directory; relative paths are resolved from the directory "
            "containing this script (default: data)"
        ),
    )
    parser.add_argument(
        "--damping-ratios",
        nargs="+",
        type=float,
        default=list(DEFAULT_DAMPING_RATIOS),
        metavar="RATIO",
        help="non-negative dimensionless damping ratios",
    )
    parser.add_argument(
        "--frequency-min",
        type=float,
        default=0.5,
        help="minimum driving-to-natural angular-frequency ratio",
    )
    parser.add_argument(
        "--frequency-max",
        type=float,
        default=1.5,
        help="maximum driving-to-natural angular-frequency ratio",
    )
    parser.add_argument(
        "--frequency-points",
        type=positive_int,
        default=101,
        help="number of evenly spaced frequency ratios",
    )
    parser.add_argument(
        "--samples-per-period",
        type=positive_int,
        default=50,
        help="stored samples per driving period",
    )
    parser.add_argument(
        "--cycles",
        type=positive_int,
        default=40,
        help="number of driving periods simulated per run",
    )
    parser.add_argument(
        "--natural-angular-frequency",
        type=float,
        default=1.0,
        metavar="RAD_PER_S",
        help="positive natural angular frequency in radians per second",
    )
    parser.add_argument(
        "--drive-acceleration",
        type=float,
        default=1.0,
        metavar="M_PER_S2",
        help="non-negative driving-acceleration amplitude",
    )
    parser.add_argument(
        "--solver",
        choices=SOLVERS,
        default="DOP853",
        help="SciPy solve_ivp method (default: DOP853)",
    )
    parser.add_argument(
        "--relative-tolerance",
        type=positive_float,
        default=1.0e-8,
        metavar="RTOL",
        help="relative error tolerance passed to solve_ivp",
    )
    parser.add_argument(
        "--absolute-tolerance",
        type=positive_float,
        default=1.0e-10,
        metavar="ATOL",
        help="absolute error tolerance passed to solve_ivp",
    )
    parser.add_argument(
        "--batch-size",
        type=positive_int,
        default=101,
        help="maximum number of independent oscillators per solve_ivp call",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="replace an existing dataset created by this generator",
    )
    args = parser.parse_args()
    validate_args(parser, args)
    return args


def validate_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    """Reject parameter combinations that cannot produce a valid dataset."""
    finite_values = [
        *args.damping_ratios,
        args.frequency_min,
        args.frequency_max,
        args.natural_angular_frequency,
        args.drive_acceleration,
    ]
    if not all(math.isfinite(value) for value in finite_values):
        parser.error("all physical parameters must be finite")
    if any(ratio < 0.0 for ratio in args.damping_ratios):
        parser.error("damping ratios must be non-negative")
    if len(set(args.damping_ratios)) != len(args.damping_ratios):
        parser.error("--damping-ratios contains duplicates")
    if args.frequency_min <= 0.0:
        parser.error("--frequency-min must be positive")
    if args.frequency_max <= args.frequency_min:
        parser.error("--frequency-max must be greater than --frequency-min")
    if args.natural_angular_frequency <= 0.0:
        parser.error("--natural-angular-frequency must be positive")
    if args.drive_acceleration < 0.0:
        parser.error("--drive-acceleration must be non-negative")


def oscillator_rhs(
    phase: float,
    state: np.ndarray,
    *,
    damping_ratio: np.ndarray,
    natural_angular_frequency: float,
    drive_angular_frequency: np.ndarray,
    drive_acceleration: float,
) -> np.ndarray:
    """Return derivatives with driving phase as the independent variable."""
    run_count = damping_ratio.size
    displacement = state[:run_count]
    velocity = state[run_count:]
    displacement_derivative = velocity / drive_angular_frequency
    acceleration = (
        drive_acceleration * np.cos(phase)
        - 2.0 * damping_ratio * natural_angular_frequency * velocity
        - natural_angular_frequency**2 * displacement
    )
    velocity_derivative = acceleration / drive_angular_frequency
    return np.concatenate((displacement_derivative, velocity_derivative))


def attach_metadata(table: pa.Table, artifact: str) -> pa.Table:
    """Attach dataset identity metadata to a Parquet table."""
    metadata = dict(table.schema.metadata or {})
    metadata.update(
        {
            b"dataset_id": DATASET_ID.encode(),
            b"generator_version": GENERATOR_VERSION.encode(),
            b"artifact": artifact.encode(),
        }
    )
    return table.replace_schema_metadata(metadata)


def solve_batch(
    *,
    batch_id: int,
    run_id_start: int,
    damping_ratio: np.ndarray,
    frequency_ratio: np.ndarray,
    phases: np.ndarray,
    cycles: int,
    samples_per_period: int,
    natural_angular_frequency: float,
    drive_acceleration: float,
    solver: str,
    relative_tolerance: float,
    absolute_tolerance: float,
) -> tuple[pa.Table, pa.Table, pa.Table]:
    """Solve one batch and return batch, run, and observation tables."""
    run_count = damping_ratio.size
    run_ids = np.arange(run_id_start, run_id_start + run_count, dtype=np.int64)
    drive_angular_frequency = frequency_ratio * natural_angular_frequency
    initial_state = np.zeros(2 * run_count, dtype=np.float64)
    right_hand_side = partial(
        oscillator_rhs,
        damping_ratio=damping_ratio,
        natural_angular_frequency=natural_angular_frequency,
        drive_angular_frequency=drive_angular_frequency,
        drive_acceleration=drive_acceleration,
    )
    result = solve_ivp(
        right_hand_side,
        (float(phases[0]), float(phases[-1])),
        initial_state,
        method=solver,
        t_eval=phases,
        rtol=relative_tolerance,
        atol=absolute_tolerance,
    )
    if not result.success:
        raise RuntimeError(
            f"solve_ivp failed for batch {batch_id}: status={result.status}; "
            f"{result.message}"
        )
    expected_shape = (2 * run_count, phases.size)
    if result.y.shape != expected_shape:
        raise RuntimeError(
            f"unexpected result shape for batch {batch_id}: "
            f"{result.y.shape}, expected {expected_shape}"
        )

    displacement = result.y[:run_count]
    velocity = result.y[run_count:]
    completed = np.isfinite(displacement).all(axis=1) & np.isfinite(velocity).all(
        axis=1
    )
    if not completed.all():
        failed_run_ids = run_ids[~completed]
        raise RuntimeError(
            f"non-finite results in batch {batch_id} for run IDs "
            f"{failed_run_ids.tolist()}"
        )

    batch = attach_metadata(
        pa.table(
            {
                "batch_id": np.asarray([batch_id], dtype=np.int32),
                "run_id_start": np.asarray([run_id_start], dtype=np.int64),
                "run_count": np.asarray([run_count], dtype=np.int32),
                "solver": pa.array([solver], type=pa.string()),
                "relative_tolerance": np.asarray(
                    [relative_tolerance], dtype=np.float64
                ),
                "absolute_tolerance": np.asarray(
                    [absolute_tolerance], dtype=np.float64
                ),
                "success": np.asarray([result.success], dtype=np.bool_),
                "status": np.asarray([result.status], dtype=np.int32),
                "message": pa.array([result.message], type=pa.string()),
                "rhs_evaluations": np.asarray([result.nfev], dtype=np.int32),
                "jacobian_evaluations": np.asarray([result.njev], dtype=np.int32),
                "lu_decompositions": np.asarray([result.nlu], dtype=np.int32),
            }
        ),
        "solver_batches",
    )
    runs = attach_metadata(
        pa.table(
            {
                "run_id": run_ids,
                "batch_id": np.full(run_count, batch_id, dtype=np.int32),
                "damping_ratio": damping_ratio,
                "natural_angular_frequency_rad_s": np.full(
                    run_count, natural_angular_frequency, dtype=np.float64
                ),
                "drive_angular_frequency_rad_s": drive_angular_frequency,
                "frequency_ratio": frequency_ratio,
                "drive_acceleration_m_s2": np.full(
                    run_count, drive_acceleration, dtype=np.float64
                ),
                "cycles": np.full(run_count, cycles, dtype=np.int32),
                "samples_per_period": np.full(
                    run_count, samples_per_period, dtype=np.int32
                ),
                "sample_count": np.full(run_count, phases.size, dtype=np.int32),
                "completed": completed,
            }
        ),
        "run_metadata",
    )

    flattened_displacement = displacement.reshape(-1)
    flattened_velocity = velocity.reshape(-1)
    specific_energy = 0.5 * (
        flattened_velocity**2 + natural_angular_frequency**2 * flattened_displacement**2
    )
    observations = attach_metadata(
        pa.table(
            {
                "run_id": np.repeat(run_ids, phases.size),
                "sample_index": np.tile(
                    np.arange(phases.size, dtype=np.int32), run_count
                ),
                "drive_phase_rad": np.tile(phases, run_count),
                "time_s": (
                    phases[np.newaxis, :] / drive_angular_frequency[:, np.newaxis]
                ).reshape(-1),
                "displacement_m": flattened_displacement,
                "velocity_m_s": flattened_velocity,
                "specific_energy_j_kg": specific_energy,
            }
        ),
        "observations",
    )
    return batch, runs, observations


def write_parquet(table: pa.Table, path: Path) -> None:
    """Write a table with stable settings suitable for analytical queries."""
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(
        table,
        path,
        compression="zstd",
        compression_level=6,
        row_group_size=128_000,
        use_dictionary=True,
        write_statistics=True,
    )


def sha256(path: Path) -> str:
    """Return the SHA-256 checksum of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def schema_description(schema: pa.Schema) -> list[dict[str, object]]:
    """Return a JSON-serializable Arrow schema description."""
    return [
        {"name": field.name, "type": str(field.type), "nullable": field.nullable}
        for field in schema
    ]


def ensure_safe_target(output_dir: Path, overwrite: bool) -> None:
    """Refuse to overwrite directories not created by this generator."""
    if not output_dir.exists():
        return
    if output_dir.is_symlink() or not output_dir.is_dir():
        raise RuntimeError(f"output path is not a regular directory: {output_dir}")
    if not overwrite:
        raise RuntimeError(
            f"output directory already exists: {output_dir}; use --overwrite to "
            "replace a dataset produced by this generator"
        )
    contents = list(output_dir.iterdir())
    if not contents:
        return
    manifest_path = output_dir / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            f"refusing to overwrite unrecognized directory: {output_dir}"
        ) from exc
    if manifest.get("dataset_id") not in REPLACEABLE_DATASET_IDS:
        raise RuntimeError(
            f"refusing to overwrite directory for another dataset: {output_dir}"
        )


def resolve_output_dir(path: Path) -> Path:
    """Resolve relative output paths from this script's directory."""
    expanded = path.expanduser()
    if expanded.is_absolute():
        return expanded.resolve()
    return (Path(__file__).resolve().parent / expanded).resolve()


def commit_output(temporary_dir: Path, output_dir: Path) -> None:
    """Atomically replace a recognized prior dataset where possible."""
    backup_dir: Path | None = None
    if output_dir.exists():
        backup_dir = output_dir.with_name(f".{output_dir.name}.backup-{uuid4().hex}")
        output_dir.replace(backup_dir)
    try:
        temporary_dir.replace(output_dir)
    except Exception:
        if backup_dir is not None:
            backup_dir.replace(output_dir)
        raise
    if backup_dir is not None:
        shutil.rmtree(backup_dir)


def generate_dataset(args: argparse.Namespace, output_dir: Path) -> dict[str, object]:
    """Generate all dataset artifacts and return their manifest."""
    damping_ratios = np.asarray(args.damping_ratios, dtype=np.float64)
    frequency_ratios = np.linspace(
        args.frequency_min,
        args.frequency_max,
        args.frequency_points,
        dtype=np.float64,
    )
    all_damping_ratios = np.repeat(damping_ratios, frequency_ratios.size)
    all_frequency_ratios = np.tile(frequency_ratios, damping_ratios.size)
    phases = np.linspace(
        0.0,
        args.cycles * 2.0 * np.pi,
        args.cycles * args.samples_per_period + 1,
        dtype=np.float64,
    )

    batch_tables: list[pa.Table] = []
    run_tables: list[pa.Table] = []
    observation_count = 0
    total_runs = all_damping_ratios.size
    for batch_id, start in enumerate(range(0, total_runs, args.batch_size)):
        stop = min(start + args.batch_size, total_runs)
        batch, runs, observations = solve_batch(
            batch_id=batch_id,
            run_id_start=start,
            damping_ratio=all_damping_ratios[start:stop],
            frequency_ratio=all_frequency_ratios[start:stop],
            phases=phases,
            cycles=args.cycles,
            samples_per_period=args.samples_per_period,
            natural_angular_frequency=args.natural_angular_frequency,
            drive_acceleration=args.drive_acceleration,
            solver=args.solver,
            relative_tolerance=args.relative_tolerance,
            absolute_tolerance=args.absolute_tolerance,
        )
        batch_tables.append(batch)
        run_tables.append(runs)
        observation_count += observations.num_rows
        part_path = (
            output_dir / "observations" / f"batch_{batch_id:04d}" / "part_000.parquet"
        )
        write_parquet(observations, part_path)
        print(
            f"wrote {part_path.relative_to(output_dir)} "
            f"({observations.num_rows:,} rows)"
        )

    all_batches = pa.concat_tables(batch_tables)
    all_runs = pa.concat_tables(run_tables)
    write_parquet(all_batches, output_dir / "solver_batches.parquet")
    write_parquet(all_runs, output_dir / "runs.parquet")
    if all_runs.num_rows != total_runs:
        raise RuntimeError(
            f"run-count validation failed: wrote {all_runs.num_rows}, "
            f"expected {total_runs}"
        )

    artifacts = []
    parquet_observation_count = 0
    for path in sorted(output_dir.rglob("*.parquet")):
        rows = pq.ParquetFile(path).metadata.num_rows
        relative_path = path.relative_to(output_dir).as_posix()
        if relative_path.startswith("observations/"):
            parquet_observation_count += rows
        artifacts.append(
            {
                "path": relative_path,
                "rows": rows,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    if parquet_observation_count != observation_count:
        raise RuntimeError(
            "observation-count validation failed: "
            f"metadata reports {parquet_observation_count:,}, "
            f"expected {observation_count:,}"
        )

    completed_runs = int(
        np.count_nonzero(all_runs.column("completed").to_numpy(zero_copy_only=False))
    )
    manifest: dict[str, object] = {
        "dataset_id": DATASET_ID,
        "generator": "generate_dataset.py",
        "generator_version": GENERATOR_VERSION,
        "software": {
            "numpy": np.__version__,
            "pyarrow": pa.__version__,
            "scipy": scipy.__version__,
        },
        "model": {
            "equation": "x'' + 2*zeta*omega_0*x' + omega_0^2*x = a*cos(omega_d*t)",
            "phase_transformation": "phi = omega_d*t",
            "symbols": {
                "x": "displacement in metres",
                "t": "time in seconds",
                "phi": "dimensionless driving phase in radians",
                "zeta": "dimensionless damping ratio",
                "omega_0": "natural angular frequency in radians per second",
                "a": "driving-acceleration amplitude in metres per second squared",
                "omega_d": "driving angular frequency in radians per second",
            },
            "initial_conditions": {"displacement_m": 0.0, "velocity_m_s": 0.0},
        },
        "parameters": {
            "damping_ratios": args.damping_ratios,
            "frequency_min": args.frequency_min,
            "frequency_max": args.frequency_max,
            "frequency_points": args.frequency_points,
            "samples_per_period": args.samples_per_period,
            "cycles": args.cycles,
            "natural_angular_frequency_rad_s": args.natural_angular_frequency,
            "drive_acceleration_m_s2": args.drive_acceleration,
            "solver": args.solver,
            "relative_tolerance": args.relative_tolerance,
            "absolute_tolerance": args.absolute_tolerance,
            "batch_size": args.batch_size,
        },
        "summary": {
            "solver_batches": all_batches.num_rows,
            "runs": all_runs.num_rows,
            "completed_runs": completed_runs,
            "observations": observation_count,
            "observation_partitions": all_batches.num_rows,
        },
        "schemas": {
            "solver_batches": schema_description(all_batches.schema),
            "runs": schema_description(all_runs.schema),
            "observations": schema_description(observations.schema),
        },
        "artifacts": artifacts,
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> None:
    """Generate the dataset in a temporary directory and commit it on success."""
    args = parse_args()
    output_dir = resolve_output_dir(args.output_dir)
    try:
        ensure_safe_target(output_dir, args.overwrite)
    except RuntimeError as exc:
        raise SystemExit(f"error: {exc}") from None
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    temporary_dir = Path(
        tempfile.mkdtemp(
            prefix=f".{output_dir.name}.generating-", dir=output_dir.parent
        )
    )
    try:
        manifest = generate_dataset(args, temporary_dir)
        commit_output(temporary_dir, output_dir)
    except Exception:
        shutil.rmtree(temporary_dir, ignore_errors=True)
        raise

    summary = manifest["summary"]
    print(
        f"generated {summary['runs']:,} runs and "
        f"{summary['observations']:,} observations in {output_dir}"
    )


if __name__ == "__main__":
    main()
