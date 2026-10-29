# Polars

Polars is an alternative to pandas that is designed to have better performance.


## What is it?

1. `patient_data.ipynb`: Jupyter notebook that explores functional differences
   between pandas and polars.  It replicates the notebook in the `pandas`
   directory with the same name.
1. `create_csv_data.py`: Python script to generate one or more large CSV files
   for benchmarking. (Note: this is a simple utility script that is not intended
   to be robust or production-ready.)
1. `create_parquet_data.py`: Python script to generate reproducible Parquet
   files in bounded-size row groups for benchmarking file-backed workflows.
1. `create_csv_data.slurm`: Slurm script to run `create_csv_data.py` on a
   cluster.  (Note: don't generate excessively large files on a shared cluster,
   or more than 4 files in parallel, as this may impact other users.)
1. `polars_performance.ipynb`: reproducible performance investigation comparing
   equivalent pandas and Polars transformations, CSV input, and Polars eager,
   lazy, and streaming execution on file-backed data.
1. `data`: Directory containing the data used in the notebook.
1. `polars_execution_modes_benchmark.py`: Python script that compares the
   performance of polars in eager and lazy execution modes.
1. `polars_query_plan.py`: Python script that demonstrates how to view the
   query plan of a polars lazy frame.
1. `polars_datatypes.ipynb`: Jupyter notebook illustrating the use of schema
   information when reading data.
1. `polars_missing_values.ipynb`: Jupyter notebook illustrating how polars
   handles missing values.


## Exercises

Some exercises to practice your skills:

1. `EXERCISES.md`: list of exercises.
1. `EXERCISES_INSTRUCTOR.md`: some hints and sketch of solutions.
1. `EXERCISES_SOLUTIONS.ipynb`: Jupyter notebook with solutions to the
   exercises.
