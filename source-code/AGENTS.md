# Repository Guidelines

## Project Structure & Module Organization
This repository is organized by topic rather than as a single Python package. Each top-level directory contains examples, notebooks, and supporting data for one subject area: `pandas/`, `polars/`, `duckdb/`, `gis/`, `networkx/`, `web-scraping/`, `altair/`, `holoviews/`, `regexes/`, `seaborn/`, `xarray/`, and `db-access/`. Keep source files close to the material they support. Store sample datasets in local `data/` or `Data/` folders, and keep generated visuals or screenshots beside the notebook that uses them.

## Build, Test, and Development Commands
There is no root build system or unified test runner. Use the command that matches the material you changed:

- `jupyter lab` or `jupyter notebook`: open and run notebooks such as `pandas/pandas_intro.ipynb`.
- `python pandas/generate_csv_files.py --help`: inspect script options before changing CLI behavior.
- `python polars/create_csv_data.py demo --files 2 --cols 4 --rows 100`: generate local CSV input for examples.
- `python networkx/topo_sort.py`: run a representative standalone script.

Run commands from the repository root unless a notebook or README says otherwise.

## Coding Style & Naming Conventions
Follow the style already used in the repository: 4-space indentation, readable function names in `snake_case`, and short, focused scripts. Use descriptive notebook names such as `missing_values.ipynb` or `world_happiness.ipynb`. Keep command-line examples simple and explicit. Avoid introducing package-level abstractions unless several examples genuinely need shared code.

## Testing Guidelines
This repository does not currently include automated tests. Validate changes by running the affected script or re-executing the relevant notebook from a clean kernel. For data-focused changes, verify that required local inputs still exist and that output files are written to the expected topic directory. If you add reusable Python modules, add `test_*.py` tests near that module or in a small local `tests/` folder.

## Commit & Pull Request Guidelines
Recent commits use short, imperative summaries such as `Improve formatting` and `Adapted for pandas 3`. Keep commit messages concise, capitalized, and focused on one change. Pull requests should describe the topic area touched, list notebooks/scripts verified, note any new data files, and include screenshots only when visual output materially changed.
