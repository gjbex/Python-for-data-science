#!/usr/bin/env python

from argparse import ArgumentParser
from concurrent.futures import ProcessPoolExecutor
import csv
from datetime import datetime, timedelta
import random
import sys


def write_file(args):
    file_name, rows, curr_time, delta_time, curr_vals, delta_val, seed = args
    random.seed(seed)
    fieldnames = ["timestamp"]
    fieldnames.extend([f"C{i + 1:d}" for i in range(len(curr_vals))])
    with open(file_name, "w", newline="", buffering=1_024 * 1_024) as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for _ in range(rows):
            data = {f"C{i + 1:d}": val for i, val in enumerate(curr_vals)}
            data["timestamp"] = curr_time
            writer.writerow(data)
            curr_time += delta_time
            curr_vals = [x + random.uniform(-delta_val, delta_val) for x in curr_vals]
    return file_name


def get_options():
    arg_parser = ArgumentParser(description="create a set of CSV files")
    arg_parser.add_argument(
        "--files", type=int, default=1, help="number of files to create"
    )
    arg_parser.add_argument("base_name", help="base file name to use")
    arg_parser.add_argument(
        "--cols", type=int, default=1, help="number of columns to generate"
    )
    arg_parser.add_argument(
        "--rows", type=int, default=100, help="number of rows to generate per file"
    )
    arg_parser.add_argument(
        "--workers", type=int, default=None, help="number of workersto use"
    )
    arg_parser.add_argument("--seed", type=int, default=1234, help="random seed to use")
    arg_parser.add_argument(
        "--curr_time",
        type=str,
        default=None,
        help="current time to use (YYYY-MM-DD HH:MM:SS)",
    )
    options = arg_parser.parse_args()
    if options.files < 1:
        print("Error: number of files must be at least 1", file=sys.stderr)
        sys.exit(1)
    if options.cols < 1:
        print("Error: number of columns must be at least 1", file=sys.stderr)
        sys.exit(1)
    if options.rows < 1:
        print("Error: number of rows must be at least 1", file=sys.stderr)
        sys.exit(1)
    if options.curr_time is not None:
        try:
            options.curr_time = datetime.strptime(
                options.curr_time,
                "%Y-%m-%d %H:%M:%S",
            )
        except ValueError:
            print(
                "Error: current time must be in the format YYYY-MM-DD HH:MM:SS",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        options.curr_time = datetime.now()
    return options


def main():
    options = get_options()
    random.seed(options.seed)
    seeds = [random.randint(0, 2**32 - 1) for _ in range(options.files)]
    delta_time = timedelta(seconds=1)
    curr_vals = [1.0] * options.cols
    delta_val = 0.01
    with ProcessPoolExecutor(max_workers=options.workers) as executor:
        args = [
            (
                f"{options.base_name}_{i + 1:04d}.csv",
                options.rows,
                options.curr_time + i * options.rows * delta_time,
                delta_time,
                curr_vals,
                delta_val,
                seeds[i],
            )
            for i in range(options.files)
        ]
        for file_name in executor.map(write_file, args):
            print(f"{file_name} done")


if __name__ == "__main__":
    main()
