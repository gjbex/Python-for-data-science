#!/usr/bin/env python3

import polars as pl

query = (
    pl.scan_parquet("benchmark.parquet")
    .filter(pl.col("group") == 3)
    .select(pl.col("value").mean())
)

print(query.explain())
