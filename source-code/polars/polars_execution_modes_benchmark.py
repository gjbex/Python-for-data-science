#!/usr/bin/env python3

import argparse
import resource
import sys
from time import perf_counter

import numpy as np
import polars as pl

FILE = "benchmark.parquet"
DEFAULT_N = 2_000_000


def generate(n=DEFAULT_N):
    rng = np.random.default_rng(42)

    df = pl.DataFrame({
        "group": rng.integers(0, 100, size=n),
        "value": rng.random(n),
        **{
            f"noise_{i}": rng.random(n)
            for i in range(16)
        },
    })

    df.write_parquet(FILE, row_group_size=100_000)
    print(f"Generated {n:,} rows")


def eager():
    return (
        pl.read_parquet(FILE)
        .filter(pl.col("group") == 3)
        .select(pl.col("value").mean())
    )


def lazy(engine="auto"):
    return (
        pl.scan_parquet(FILE)
        .filter(pl.col("group") == 3)
        .select(pl.col("value").mean())
        .collect(engine=engine)
    )


def benchmark(mode):
    start = perf_counter()

    if mode == "eager":
        result = eager()
    elif mode == "lazy-memory":
        result = lazy(engine="in-memory")
    else:
        result = lazy()

    elapsed = perf_counter() - start

    # Linux: ru_maxrss is expressed in KiB.
    peak_mib = ( resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)
    print(f"Mode:       {mode}")
    print(f"Result:     {result.item():.6f}")
    print(f"Time:       {elapsed:.3f} s")
    print(f"Peak RSS:   {peak_mib:.1f} MiB")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode",
        choices=["generate", "eager", "lazy-memory", "lazy"],
    )
    parser.add_argument(
        "-n",
        type=int,
        default=DEFAULT_N,
        help=f"Number of rows to generate (default: {DEFAULT_N:,})",
    )
    args = parser.parse_args()

    if args.mode == "generate":
        generate(args.n)
    else:
        benchmark(args.mode)

