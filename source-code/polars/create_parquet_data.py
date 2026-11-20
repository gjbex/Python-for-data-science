#!/usr/bin/env python3

from argparse import ArgumentParser, ArgumentTypeError, Namespace
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path
import random

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq


DEFAULT_START_TIME = datetime(2024, 1, 1, 0, 0, 0)
DEFAULT_ROW_GROUP_SIZE = 100_000
DELTA_VALUE = 0.01

FileJob = tuple[
    str,
    int,
    int,
    datetime,
    int,
    int,
    str | None,
]


def parse_datetime(value: str) -> datetime:
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except ValueError as exc:
        raise ArgumentTypeError("expected YYYY-MM-DD HH:MM:SS") from exc


def positive_integer(value: str) -> int:
    try:
        result = int(value)
    except ValueError as exc:
        raise ArgumentTypeError("expected an integer") from exc
    if result < 1:
        raise ArgumentTypeError("expected a positive integer")
    return result


def create_row_group(
    *,
    rows: int,
    columns: int,
    start_time: np.datetime64,
    row_offset: int,
    current_values: np.ndarray,
    column_rngs: list[np.random.Generator],
) -> pa.Table:
    offsets = np.arange(row_offset, row_offset + rows, dtype="timedelta64[s]")
    data: dict[str, np.ndarray] = {"timestamp": start_time + offsets}

    for column_index in range(columns):
        increments = column_rngs[column_index].uniform(
            -DELTA_VALUE, DELTA_VALUE, size=rows
        )
        values = np.empty(rows, dtype=np.float64)
        values[0] = current_values[column_index]
        if rows > 1:
            np.cumsum(increments[:-1], out=values[1:])
            values[1:] += current_values[column_index]
        current_values[column_index] += increments.sum()
        data[f"C{column_index + 1}"] = values

    return pa.Table.from_pydict(data)


def write_file(job: FileJob) -> str:
    (
        file_name,
        rows,
        columns,
        start_time,
        row_group_size,
        seed,
        compression,
    ) = job

    output_path = Path(file_name)
    column_rngs = [
        np.random.default_rng(column_seed)
        for column_seed in np.random.SeedSequence(seed).spawn(columns)
    ]
    current_values = np.ones(columns, dtype=np.float64)
    parquet_start_time = np.datetime64(start_time, "us")
    schema = pa.schema(
        [("timestamp", pa.timestamp("us"))]
        + [(f"C{index + 1}", pa.float64()) for index in range(columns)]
    )

    with pq.ParquetWriter(output_path, schema, compression=compression) as writer:
        for row_offset in range(0, rows, row_group_size):
            rows_in_group = min(row_group_size, rows - row_offset)
            table = create_row_group(
                rows=rows_in_group,
                columns=columns,
                start_time=parquet_start_time,
                row_offset=row_offset,
                current_values=current_values,
                column_rngs=column_rngs,
            )
            writer.write_table(table)

    return str(output_path)


def get_options() -> Namespace:
    parser = ArgumentParser(
        description="create one or more Parquet files containing random-walk data"
    )
    parser.add_argument("base_name", help="base file name to use")
    parser.add_argument(
        "--files",
        type=positive_integer,
        default=1,
        help="number of files to create (default: 1)",
    )
    parser.add_argument(
        "--cols",
        type=positive_integer,
        default=1,
        help="number of data columns (default: 1)",
    )
    parser.add_argument(
        "--rows",
        type=positive_integer,
        default=100,
        help="number of rows per file (default: 100)",
    )
    parser.add_argument(
        "--workers",
        type=positive_integer,
        default=None,
        help="number of files to generate concurrently",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=1234,
        help="seed used to derive a distinct seed for each file (default: 1234)",
    )
    parser.add_argument(
        "--start-time",
        "--start_time",
        dest="start_time",
        type=parse_datetime,
        default=DEFAULT_START_TIME,
        metavar="DATETIME",
        help=(
            "timestamp of the first row in YYYY-MM-DD HH:MM:SS format "
            "(default: 2024-01-01 00:00:00)"
        ),
    )
    parser.add_argument(
        "--row-group-size",
        type=positive_integer,
        default=DEFAULT_ROW_GROUP_SIZE,
        help=f"maximum rows per Parquet row group (default: {DEFAULT_ROW_GROUP_SIZE})",
    )
    parser.add_argument(
        "--compression",
        choices=("none", "snappy", "gzip", "brotli", "lz4", "zstd"),
        default="zstd",
        help="Parquet compression codec (default: zstd)",
    )
    return parser.parse_args()


def main() -> None:
    options = get_options()
    seed_generator = random.Random(options.seed)
    seeds = [seed_generator.randrange(2**32) for _ in range(options.files)]
    compression = None if options.compression == "none" else options.compression

    jobs: list[FileJob] = [
        (
            f"{options.base_name}_{file_index + 1:04d}.parquet",
            options.rows,
            options.cols,
            options.start_time + timedelta(seconds=file_index * options.rows),
            options.row_group_size,
            seeds[file_index],
            compression,
        )
        for file_index in range(options.files)
    ]

    with ProcessPoolExecutor(max_workers=options.workers) as executor:
        for file_name in executor.map(write_file, jobs):
            print(f"{file_name} done")


if __name__ == "__main__":
    main()
